from PyQt5.QtWidgets import QApplication

import re

app = QApplication([])
clipboard = app.clipboard()

# 有俩字符编码会出问题，于是创建了个替换表
replace_table = {'\\u3000':'　','\\xa0':' '}

# 这里不直接return最后处理好的字符串是因为
# 要是这个函数能在其他地方用的话就直接能复制过去23333
def get_clipboard_file():
    data = clipboard.mimeData()
    if data.hasFormat('text/uri-list'):

        pattern = re.compile(r'file:///(.*)\'\)')
        urls = []

        for path in data.urls():
            url = ''
            try:
                url = pattern.findall(str(path))[0]
            except IndexError:
                pass
            urls.append(url)
        return urls

if __name__ == '__main__':

    urls_ = get_clipboard_file()

    urls_str = '#EXTM3U\n'
    for url_ in urls_:
        urls_str +=  url_ + '\n'

    # 替换掉有问题的字符
    for key,value in replace_table.items():
        urls_str = urls_str.replace(key,value)


    file_name = input('请输入 文件/播放列表 名 : ')
    with open('%s.m3u' % file_name, 'w', encoding='utf-8') as u:
        u.write(urls_str)
