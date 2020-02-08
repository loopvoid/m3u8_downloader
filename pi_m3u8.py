#-*- coding:utf-8 -*-
import requests
import re
from Crypto.Cipher import AES
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import time

class DownM3u8:
	# 多线程最大设置数量应该为os.cpu_count()的五倍,尽量不要多
	def __init__(self, url,save_ts_dir, max_workers=16):
		self.url = url
		self.real_m3u8_url = ''
		self.root_ts_key = ''
		self.ts_queue = Queue()
		self.key_aes = ''
		self.executor = ThreadPoolExecutor(max_workers=max_workers)
		self.save_ts_dir = save_ts_dir

	def aes_decode(self, data):
		"""AES解密
		:param key:  密钥（16.32）一般16的倍数 str
		:param data:  要解密的数据
		:return:  处理好的数据
		"""
		cryptor = AES.new(self.key_aes, AES.MODE_CBC, self.key_aes)
		plain_text = cryptor.decrypt(data)
		return plain_text.rstrip(b'\0')  # .decode("utf-8")

	def show_time(self):
		local_time = time.asctime(time.localtime(time.time()))
		print(local_time)

	def get_real_m3u8_url(self):
		root = self.url.replace('index.m3u8', '')
		r = requests.get(self.url)
		index_arr = r.text.split('\n')
		self.real_m3u8_url = root + index_arr[2]

	def get_converted_key_aes_and_ts_queue(self):

		m3u8_file = requests.get(self.real_m3u8_url).text

		self.root_ts_key = self.real_m3u8_url.replace('index.m3u8', '')

		pattern_key = re.compile('URI=".*"')
		pattern_ts  = re.compile('(?<=\n).*.ts')
		key_match = (pattern_key.findall(m3u8_file))[0].replace('URI=','').replace('"','')

		key_url = self.root_ts_key + key_match
		key = requests.get(key_url, timeout=15)
		self.key_aes = key.content

		ts = pattern_ts.findall(m3u8_file)
		for i in ts:
			self.ts_queue.put(i)
		# 这里获得了ts列表，key_ase，接着就是多线程的下载ts视频了
		# resp = requests.get(root_ts_key+ts[i],timeout=120)
		# with open(file_name,'ab+') as f:
		# 	data = aes_decode(resp.content,key_ase)
		# 	f.write(data)

	def down_one_ts(self,ts_filename):
		try:
			url = self.root_ts_key+ts_filename
			resp = requests.get(url)
			save_dir = self.save_ts_dir+'/'+ts_filename
			with open(save_dir,'ab+') as f:
				# f.write(resp.content)
				data = self.aes_decode(resp.content)
				f.write(data)

		except:
			self.ts_queue.put(ts_filename, block=1)

	def conver2mp4(self):
		# full_path = os.path.realpath(__file__)
		mp4_path = './mp4'
		path = './ts'
		path_list = os.listdir(path)
		path_list.sort()
		li = [os.path.join(path, filename) for filename in path_list]
		# 类似于[001.ts|00.2ts|003.ts]
		input_file = '|'.join(li)
		# 指定输出文件名称
		output_file = mp4_path + path_list[0] + '.mp4'
		# 使用ffmpeg将ts合并为mp4
		command = 'ffmpeg -i "concat:%s" -acodec copy -vcodec copy -absf aac_adtstoasc %s' % (input_file, output_file)
		# 指行命令
		os.system(command)
		# os.system('rm /home/pi/udisk/ts/temp/*.ts')

	def run(self):
		self.get_real_m3u8_url()
		self.get_converted_key_aes_and_ts_queue()

		while not self.ts_queue.empty():
			ts_filename = self.ts_queue.get()
			self.executor.submit(self.down_one_ts,ts_filename)
			# self.down_one_ts(ts_filename)
		self.conver2mp4()

if __name__ == '__main__':
	url = sys.argv[1]
	if len(url)>5:
		down = DownM3u8(url,'ts')
		# down = DownM3u8(url, '/home/pi/udisk/ts')
		down.run()
