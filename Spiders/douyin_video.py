# !/user/bin/env python
# -*- coding:utf-8 -*- 
# time: 2018/7/22--22:07
__author__ = 'Henry'

'''
抖音视频下载
'''

# 注意:爬取中间会出现{'cursor': 10, 'status_code': 0, 'has_more': 1, 'aweme_list': []},取不到视频,一直请求即可

import requests, re, sys, os, time

# 增加函数递归次数
sys.setrecursionlimit(1000000)
# 获取dytk值(每个id,dytk值是固定的)
def get_param(user_id):
    url = 'https://www.douyin.com/share/user/{}/'.format(user_id)
    headers = {
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    html = requests.get(url, headers=headers).text
    dytk = re.search("dytk: '(.*?)'", html).group(1)
    params = {
        'user_id': str(user_id),
        'count': '35',  # 默认21,写再大最多也就一次35个视频
        'max_cursor': '0', # 开始爬取的标记
        'aid': '1128',
        # '_signature': signature, # signature可以不带(js加密的)
        'dytk': dytk,
    }
    return params

# 下载喜欢的视频(音乐已经下载不到了,music字段为空)
num = 1
def get_favor_video(param,max_cursor=None):
    if not os.path.exists('douyin_video'):
        os.mkdir('douyin_video')
    if max_cursor:
        param['max_cursor'] = str(max_cursor)
    url = 'https://www.douyin.com/aweme/v1/aweme/favorite/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'referer': 'https://www.douyin.com/share/user/{}/'.format(user_id),
    }
    html = requests.get(url=url, params=param, headers=headers).json()
    content = html.get('aweme_list')
    print(html)
    if content:
        for i in content:
            global num  # 在函数中引用函数外定义的变量就要用全局变量引用
            # 标题
            title = i['share_info']['share_desc']
            # 清洗一下标题名称(不能有\ / : * ? " < > |)
            title = re.sub(r'[\/\\:*?"<>|]', '', title)  # 替换为空的
            print(str(num) + '-' + title)
            # 视频地址
            video_uri = i['video']['play_addr']['uri']
            video = 'https://aweme.snssdk.com/aweme/v1/playwm/?video_id={}'.format(
                video_uri)  # 原来可以playwm去掉wm,下载无水印视频;现在不行了
            print(video)
            # 下载视频
            mp4 = requests.get(video, headers=headers, stream=True).content  # 必须加上headers,不然跳转失败!!!
            open('douyin_video\\{}-{}.mp4'.format(num, title), 'wb').write(mp4)
            num = num + 1
    if max_cursor:
        print(max_cursor)
    if html['has_more'] == 1:
        return get_favor_video(param,html.get('max_cursor'))
    else:
        print('下载结束...')
        end_time = time.time()  # 结束时间
        print("一共下载了%s个抖音视频,总耗时%.2f秒,大约%.2f分钟" % (num, end_time - start_time, int(end_time - start_time) / 60))
        exit()

# 获取作者的作品(就把url改成'https://www.douyin.com/aweme/v1/aweme/post/')


if __name__ == '__main__':
    user_id = input('请输入您要爬取的作者的ID:') # 不是抖音ID,是url中的ID(见UserID.png)
    start_time = time.time()
    param = get_param(user_id)
    get_favor_video(param)
