# -*- coding:utf-8 -*-

import sqlite3
import json
import os
import re

from collections import Counter


# TODO
def logger(info):
    """日志记录器"""
    info = str(info)
    print(info)


def make_string_windows_compatible(_str):
    return re.sub(r'[\\\/\:\*\?\"\<\>\|]', '_', _str)


def get_dir_of_db():
    """输出library和webdb的路径"""
    user_dir = os.path.expanduser('~')
    library = os.path.join(
        user_dir,
        r'AppData\Local\Netease\CloudMusic\Library\library.dat')
    webdb = os.path.join(
        user_dir,
        r'AppData\Local\Netease\CloudMusic\Library\webdb.dat')
    if os.path.exists(library) and os.path.exists(webdb):
        return {'library.dat': library, 'webdb.dat': webdb, 'ok': True}
    else:
        return {'ok': False}


def get_playlist(playlist_dir):
    """获取播放列表以及播放列表的信息
    返回值：{pid:{'playlist_name': playlist_name,
            'userid': userid,
            'username': username,
            'songs': list()},...}"""
    # 获取播放列表
    playlist = sqlite3.connect(playlist_dir)
    playlist_con = playlist.cursor()
    playlist_info = playlist_con.execute(
        'SELECT pid,playlist FROM web_playlist')

    # 获取播放列表信息
    # 格式:{pid:{'playlist_name':..,'userid':..,'username':..,'songs':[]}}
    playlists = dict()
    for pid, playlist_json in playlist_info:
        playlist_info_dict = json.loads(playlist_json)
        playlist_name = playlist_info_dict['name']
        userid = playlist_info_dict['userId']
        issubscribed = playlist_info_dict['subscribed']
        # 有些歌单没有nickname，比如 我喜欢的音乐 之类的,就只能这样了。
        if 'nickname' in playlist_info_dict['creator']:
            username = playlist_info_dict['creator']['nickname']
        else:
            username = False
        playlists[pid] = ({'playlist_name': playlist_name,
                           'userid': userid,
                           'username': username,
                           'subscribed': issubscribed,
                           'songs': list()})

    # 获取播放列表对应歌曲
    playlist_track = playlist_con.execute(
        'SELECT pid,tid FROM web_playlist_track')

    # 将歌曲添加到播放列表中
    for pid, tid in playlist_track:
        playlists[pid]['songs'].append(tid)

    return playlists


def get_songs_dir(library_dir):
    """尝试获取歌曲保存目录
    返回值是歌曲目录"""
    lib_sql = sqlite3.connect(library_dir)
    lib_data = lib_sql.execute('SELECT dir FROM track')
    # 转化为列表，这样就能计数啦
    lib_data = [i[0] for i in lib_data]
    songs_dir, times = Counter(lib_data).most_common(1)[0]
    return songs_dir


def tid2dir_offline(library_dir, webdb_dir):
    """转化tid为 文件路径
    返回{tid1:dir1,tid2:dir2}"""
    songs_dir = get_songs_dir(library_dir)
    webdb_sql = sqlite3.connect(webdb_dir)
    webdb_cursor = webdb_sql.cursor()

    # 在web_offline_track中找文件，届时需要手动合成目录和歌曲文件名
    songs_dict = dict()
    web_offline_track = webdb_cursor.execute(
        'SELECT track_id, relative_path, track_name, artist_name, album_name FROM web_offline_track')
    for tid, relative_path, name, artist, album in web_offline_track:
        if relative_path == '':
            continue
        else:
            songs_dict[tid] = dict()
            songs_dict[tid]['file_path'] = os.path.join(songs_dir, relative_path)
            songs_dict[tid]['name'] = name
            songs_dict[tid]['artist'] = artist
            songs_dict[tid]['album'] = album

    return songs_dict


def playlist_dict_to_m3u(playlists, songs, playlist_ids):
    """转换指定播放列表为m3u文件内容"""
    m3u_content = dict()

    _all = 0
    _in = 0
    for _id in playlist_ids:
        present_playlist = playlists[_id]
        name = present_playlist['playlist_name']
        # 预先加一个m3u标签
        m3u_content[name] = '#EXTM3U'

        for song in present_playlist['songs']:
            # 如果歌曲id存在于转换表中，就转换，否则放弃。
            _all += 1
            if song in songs:
                _in += 1
                m3u_content[name] += '\n' + songs[song]['file_path']
    return m3u_content


def playlist_fliter_as_subscribed(playlists, is_subscribed):
    """返回值是一个pid为元素的列表"""
    playlist_ids = list()
    for pid, playlist in playlists.items():
        if playlist['subscribed'] is is_subscribed:
            playlist_ids.append(pid)
    return playlist_ids


def playlist_filter_as_userid(playlists, userid):
    """返回值是一个pid为元素的列表"""
    playlist_ids = list()
    for pid, playlist in playlists.items():
        if playlist['userid'] == userid:
            playlist_ids.append(pid)
    return playlist_ids


def save_m3u(m3u_content, top, encoding='utf-8'):
    """把m3u字典写入文件"""
    for name, content in m3u_content.items():
        # 去除敏感字符
        name = make_string_windows_compatible(name)

        file_name = name + '.m3u'
        file_path = os.path.join(top, file_name)
        with open(file_path, 'w', encoding=encoding, errors='ignore') as m3u_file:
            m3u_file.write(content)


def main():
    # 获取数据库文件
    dirs = get_dir_of_db()
    if not dirs['ok']:
        logger('无法找到网易云数据库文件')
        quit()
    library_dat = dirs['library.dat']
    webdb_dat = dirs['webdb.dat']

    playlists = get_playlist(webdb_dat)
    songs = tid2dir_offline(library_dat, webdb_dat)

    # 用户筛选
    filter_mode = input('请输入筛选模式，1代表按照用户id筛选，2代表按照是否是自己的歌单筛选:')
    playlist_ids = []

    if filter_mode == '1':
        userid_str = input('请输入歌单拥有者用户id，如果需要全部转换就直接回车：')
        if userid_str == '':
            for id_ in playlists.keys():
                playlist_ids.append(id_)
        else:
            userid = int(userid_str)
            playlist_ids = playlist_filter_as_userid(playlists, userid)

    if filter_mode == '2':
        is_sub = input('是否下载自己的歌单？只下载自己的歌单输入1，下载收藏的歌单输入2:')
        if is_sub == '1':
            playlist_ids = playlist_fliter_as_subscribed(playlists, False)
        if is_sub == '2':
            playlist_ids = playlist_fliter_as_subscribed(playlists, True)

    # 生成m3u格式字符串
    m3u_dict = playlist_dict_to_m3u(playlists, songs, playlist_ids)
    # 保存到文件
    save_m3u(m3u_dict, os.path.abspath('.'))


if __name__ == '__main__':
    main()
