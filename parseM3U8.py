import requests


def _parse_playlist(playlist_text):
	# get all ts file list
	ts_files_list = []
	arr = playlist_text.split('\n')
	for i in arr:
		if '#' in i or len(i) < 1:
			pass
		else:
			# deal with the situation where the line not clean ts filename
			# such as /dir1/dir2/tsfile001.ts
			after_split = i.split('/')[-1]
			ts_files_list.append(after_split)
	return ts_files_list


# index	https://hong.tianzhen-zuida.com/20200224/20816_d0d00746/index.m3u8
# 	#EXTM3U
# 	#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=800000,RESOLUTION=1080x608
# 	1000k/hls/index.m3u8
# playlist https://hong.tianzhen-zuida.com/20200224/20816_d0d00746/1000k/hls/index.m3u8
def parse_index_m3u8(index_text, url):
	if '#EXTM3U' not in index_text: raise BaseException("It's not m3u8 file !")

	ts_base_url = None
	key_base_url = None
	key = None
	playlist = []

	exit('============== not addressed parse index page yet ==============')
	# NOT ADDRESSED YET !!!!!
	# return(ts_base_url,key, playlist)


def parse_playlist_m3u8(playlist_text, url):
	if '#EXTM3U' not in playlist_text: raise BaseException("It's not m3u8 file !")

	ts_base_url = url.replace('index.m3u8','')
	key_base_url = url.replace('index.m3u8','')
	key_url = key_base_url + 'key.key'
	key = None
	playlist = []

	if '#EXT-X-KEY' in playlist_text:
		key = requests.get(key_url, timeout=15).content

	playlist = _parse_playlist(playlist_text)

	return ts_base_url, key, playlist


# Input：	m3u8 url
# Output:	ts_base_url  ts file site prefix
# 			key 		 encryption file key.key context
# 			playlist	 ts filename list ,[filename001.txt, ...]
def parse_url(url):
	ts_base_url = None
	key_base_url = None
	key = None
	playlist = []

	url_html = None
	try:
		url_html = requests.get(url, timeout=15)
	except Exception as e:
		print("========= Can't open index.m3u8 url! =========")
		exit()
	url_text = url_html.text

	# index.m3u8 (stage-1)
	if '#EXT-X-STREAM-INF' in url_text:
		ts_base_url,key,playlist = parse_index_m3u8(url_text, url)
	# playlist.m3u8 (stage-2)
	else:
		ts_base_url,key,playlist = parse_playlist_m3u8(url_text, url)

	return ts_base_url, key, playlist


def _test01():
	# not_encrypted_url = 'https://hong.tianzhen-zuida.com/20200224/20816_d0d00746/1000k/hls/index.m3u8'
	encrypted_url = 'https://www.baiducomcdn.com/20191126/t4M734wg/20488kb/hls/index.m3u8'
	ts_base_url, key, playlist = parse_url(encrypted_url)

	print("test01")

	# parse_url(encrypted_url)


if __name__=='__main__':
	_test01()