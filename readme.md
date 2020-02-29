# M3u8 Multithreading Downloader

Use:

```shell
python downM3U8.py m3u8_stream_url/index.m3u8 video_name
```





Pipeline:

* web url  parse (get index.m3u8 start url)
* m3u8 playlist file parse (get key.key url)

Types:

- [x] url	->	playlist.m3u8(with no key)
- [x] url    ->    playlist.m3u8(#EXT-X-KEY:METHOD=AES-128,URI="key.key")
- [x] url    ->    playlist.m3u8(#EXT-X-KEY:METHOD=AES-128,URI="some/special/url/like/key.key")
- [ ] ​	





## Reference

m3u8

https://blog.csdn.net/a33445621/article/details/80377424

多线程

https://blog.csdn.net/s_kangkang_A/article/details/103051184

地址转换

https://juejin.im/post/5db2d8e26fb9a020433f59d3

完整（单线程）
https://www.cnblogs.com/chen0307/articles/9679139.html


ffmpeg -i "https://cdn7-video.hnqiyouquan.com:8081/20200104/kOnEloiL/index.m3u8" -codec copy file.mp4