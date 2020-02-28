import sys
import math
import time


# showing bar
# @staticmethod
def show_process(description_text, curr, total):
	# curr/totoal = percent/100 = count/bar_total_len
	bar_total_len = 50
	percent = math.ceil(curr / total * 100)
	count = math.ceil(curr / total * bar_total_len)

	show_line = '\r' + 'DownLoading' + ':' + '>' * count \
				+ ' ' * (bar_total_len - count) + '[%s%%]' % (percent+1) \
				+ '[%s/%s]' % (curr+1, total)
	sys.stdout.write(show_line)
	sys.stdout.flush()


def showing_progress(description, done_list_len, all_list_len):
	curr = done_list_len
	total = all_list_len

	# curr/total = percent/100 = count/bar_total_len
	bar_total_len = 50
	percent = math.ceil(curr / total * 100)
	count = math.ceil(curr / total * bar_total_len)

	show_line = '\r' + description + ':' + '>' * count \
				+ ' ' * (bar_total_len - count) + '[%s%%]' % (percent+1) \
				+ '[%s/%s]' % (curr+1, total)
	sys.stdout.write(show_line)
	sys.stdout.flush()

	# if curr == total:
	# 	print("Downloading Done!")
	# 	break
	# time.sleep(0.5)


def _test():
	for i in range(100):
		time.sleep(0.1)
		show_process('Downloading', i, 100)


if __name__ == '__main__':
	_test()