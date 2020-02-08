#-*- coding:utf-8 -*-
import requests
from Crypto.Cipher import AES
import re
from queue import Queue
import os
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
import sys

class DownM3u8:
	def	__init__(self, url, mp4_name, max_workers=16):
		self.mp4_name = mp4_name
		self.url = url
		self.root_stage_1 = url.replace('index.m3u8','')
		self.root_stage_2 = ''

		self.m3u8_file_url = ''
		self.key_url = ''

		self.save_ts_dir = 'ts'
		self.max_workers = max_workers
		self.key_aes = ''

		self.ts_queue = Queue()
		self.all_ts_order_list = []
		# self.all_ts_order_full_path_list = []
		self.executor = ThreadPoolExecutor(max_workers=max_workers)
		self.all_tasks = []

	def _aes_decode(self, data):
		cryptor = AES.new(self.key_aes,AES.MODE_CBC, self.key_aes)
		plain_text = cryptor.decrypt(data)
		return plain_text.rstrip(b'\0') # .decode('urf-8')

	def address_index_file(self):
		r = requests.get(self.url, timeout=15)
		arr = r.text.split('\n')
		for x in arr:
			if not '#' in x:
				self.m3u8_file_url = self.root_stage_1 + x
				break

	def address_m3u8_file(self):
		m3u8_file = requests.get(self.m3u8_file_url, timeout=15).text

		# 获取加密密码
		pattern_key = re.compile('(?<=URI=").*(?=")')
		# pattern_key = re.compile('URI=".*"')
		key_dir = re.search(pattern_key, m3u8_file).group(0)
		# key_dir = pattern_key.findall(m3u8_file)[0]
		self.root_stage_2 = self.m3u8_file_url.replace('index.m3u8', '')
		self.key_url = self.root_stage_2 + key_dir
		self.key_aes = requests.get(self.key_url, timeout=15).content

		# 获取所有ts文件名的list
		temp_arr = m3u8_file.split('\n')
		for i in temp_arr:
			if '#' in i or len(i)<1:
				pass
			else:
				self.ts_queue.put(i)
				self.all_ts_order_list.append(i)


	def down_single_ts(self, ts_filename):
		try:
			url = self.root_stage_2 + ts_filename
			resp = requests.get(url, timeout = 30)
			save_dir = self.save_ts_dir+'/'+ts_filename
			with open(save_dir, 'ab+') as f:
				data = self._aes_decode(resp.content)
				f.write(data)
		except:
			self.ts_queue.put(ts_filename, block=1)

	def convertTs2Mp4(self):
		script_path = os.getcwd().replace('\\','/')
		# 生成concat.txt
		concat_data = []
		concat_file_name = self.all_ts_order_list[0]+'.txt'
		for i in self.all_ts_order_list:
			# full_path = ("file "+script_path+'/ts/'+i+"\n").replace('//','/')
			# dir_path = ("file ./ts/" + i +"\n").replace('//', '/')
			dir_path = ("file " + i + "\n").replace('//', '/')
			concat_data.append(dir_path)
		with open('./ts/'+concat_file_name, 'a+') as f:
			f.writelines(concat_data)

		# 类似于[001.ts|00.2ts|003.ts]
		# input_file = '|'.join(temp_li)
		concat_file = './ts/'+concat_file_name
		# 指定输出文件名称
		# output_file = './mp4/' + self.all_ts_order_list[0] + '.mp4'
		output_file = './mp4/' + self.mp4_name + '.mp4'
		# 使用ffmpeg将ts合并为mp4
		# command = 'ffmpeg -i "concat:%s" -acodec copy -vcodec copy -absf aac_adtstoasc %s' % (input_file, output_file)
		command = 'ffmpeg -f concat -safe 0 -i %s -acodec copy -vcodec copy -absf aac_adtstoasc %s' % (concat_file, output_file)
		os.system(command)


	def run(self):
		self.address_index_file()
		self.address_m3u8_file()

		all_tasks_1 = []
		while not self.ts_queue.empty():
			ts_filename = self.ts_queue.get()
			all_tasks_1.append(self.executor.submit(self.down_single_ts, ts_filename))
			# wait(all_tasks,None,ALL_COMPLETED)
			# total = len(self.all_ts_order_list)
			# present = total - self.ts_queue.qsize()
			# # 归一化为1到100
			# i = int(present / total * 100)
			# print('\r' + '▇' * (i // 2) + str(i) + '%', end='')
		wait(all_tasks_1,None,ALL_COMPLETED)

		all_tasks_2 = []
		while not self.ts_queue.empty():
			ts_filename = self.ts_queue.get()
			all_tasks_2.append(self.executor.submit(self.down_single_ts, ts_filename))
		wait(all_tasks_2, None, ALL_COMPLETED)

		all_tasks_3 = []
		while not self.ts_queue.empty():
			ts_filename = self.ts_queue.get()
			all_tasks_3.append(self.executor.submit(self.down_single_ts, ts_filename))
		wait(all_tasks_3, None, ALL_COMPLETED)


		self.convertTs2Mp4()





if __name__ == '__main__':
	url = sys.argv[1]
	name = sys.argv[2]
	if len(url) > 5:
		down = DownM3u8(url, name)
		down.run()

