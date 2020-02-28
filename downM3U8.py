import os
import sys
import time
import requests
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from parseM3U8 import parse_url
from decryption import aes_decryption
from progressBar import showing_progress


class DownM3u8:
	def __init__(self, url, mp4_name, max_workers=16):
		self.url = url
		self.mp4_name = mp4_name
		self.max_workers = max_workers
		self.save_ts_dir = './ts'
		self.save_mp4_dir = 'mp4'

		self.task_queue = Queue()
		self.ts_base_url = None
		self.key = ''
		self.playlist = []

		self.done_list = []

		# self.all_ts_order_full_path_list = []
		self.executor = ThreadPoolExecutor(max_workers=max_workers)
		self.all_tasks = []

	def show_bar(self):
		while True:
			done_list_len = len(self.done_list)
			all_list_len = len(self.playlist)
			showing_progress('Downloading', done_list_len, all_list_len)
			if done_list_len == all_list_len:
				print("Downloading Done!")
				break
			time.sleep(0.1)

	def download_single_ts_file(self, ts_filename):
		try:
			_url = self.ts_base_url + ts_filename
			# print("downloading {} with key={}".format(_url, self.key))
			resp = requests.get(_url, timeout=30)
			# print("resp.content len {}".format(len(resp.content)))
			save_dir = self.save_ts_dir+'/'+ts_filename
			_data = None
			with open(save_dir, 'ab+') as f:
				if self.key:
					_data = aes_decryption(self.key, resp.content)
				else:
					_data = resp.content
				f.write(_data)
				self.done_list.append(ts_filename)
				DownM3u8.DONE_TASK_NUMBER = len(self.done_list)
		except:
			self.task_queue.put(ts_filename, block=True)

	def merge_ts_2_mp4(self):
		# make concat.txt for ffmpeg
		concat_data = []
		concat_file_name = self.playlist[0] + '.txt'
		concat_file_dir = './ts/' + concat_file_name
		for i in self.playlist:
			data = ("file " + i + "\n").replace('//', '/')
			concat_data.append(data)
		with open(concat_file_dir, 'a+') as f:
			f.writelines(concat_data)

		output_file_dir = './mp4/' + self.mp4_name + '.mp4'
		command = 'ffmpeg -f concat -safe 0 -i %s -acodec copy -vcodec copy -absf aac_adtstoasc %s'\
		% (concat_file_dir, output_file_dir)
		os.system(command)

	def run(self):
		print("Requesting index.m3u8 file... ...")
		# parse m3u8 file
		self.ts_base_url, self.key, self.playlist = parse_url(self.url)

		# add all tasks into queue
		for i in self.playlist:
			self.task_queue.put(i)

		# starting progress bar showing thread
		# self.show_executor.submit(self.showing_progress,len(self.done_list),len(self.playlist))
		showing_thread = threading.Thread(target=self.show_bar)
		showing_thread.start()

		# download ts files
		if self.ts_base_url or self.playlist:
			# try round 1
			all_tasks_round_1 = []
			# print("=====================> round 1 ... ")
			while not self.task_queue.empty():
				ts_filename = self.task_queue.get()
				all_tasks_round_1.append(self.executor.submit(self.download_single_ts_file, ts_filename))
			wait(all_tasks_round_1, None, ALL_COMPLETED)

			# try round 2
			all_tasks_round_2 = []
			# print("=====================> round 2 ... ")
			while not self.task_queue.empty():
				ts_filename = self.task_queue.get()
				all_tasks_round_2.append(self.executor.submit(self.download_single_ts_file, ts_filename))
			wait(all_tasks_round_2, None, ALL_COMPLETED)

			# try round 3
			all_tasks_round_3 = []
			# print("=====================> round 3 ... ")
			while not self.task_queue.empty():
				ts_filename = self.task_queue.get()
				all_tasks_round_3.append(self.executor.submit(self.download_single_ts_file, ts_filename))
			wait(all_tasks_round_3, None, ALL_COMPLETED)

			# merge all ts files into one mp4
			self.merge_ts_2_mp4()

		else:
			print("========== can't get ts file base url or playlist! ==========")


if __name__ == '__main__':
	if len(sys.argv) < 2:
		exit("Usage: python downM3U8.py http://m3u8url mp4VideoName")
	m3u8_url = sys.argv[1]
	m3u8_name = sys.argv[2]
	if len(m3u8_url) > 5:
		down = DownM3u8(m3u8_url, m3u8_name)
		down.run()
