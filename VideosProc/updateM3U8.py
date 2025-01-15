import os
import re

# 指定要查找的文件夹路径
folder_path = "/Users/cc/Documents/CC_Self/CCFiles/Files/CCAV/2024-10-19/"  # 替换为你的文件夹路径

# 新的URI地址
new_uri = 'http://127.0.0.1:8888/media/VKey/ALL/encrypt.key'

# 正则表达式匹配 #EXT-X-KEY URI 部分
pattern = re.compile(r'(#EXT-X-KEY:METHOD=AES-128,URI=")([^"]*)(")')

def update_m3u8_file(file_path):
    """更新m3u8文件中的URI地址"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换URI部分
    new_content = pattern.sub(rf'\1{new_uri}\3', content)

    # 如果内容有变化则写入文件
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"已更新文件: {file_path}")
    else:
        print(f"无需更新: {file_path}")

def find_and_update_m3u8_files(folder):
    """查找并更新所有m3u8文件"""
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.m3u8'):
                file_path = os.path.join(root, file)
                update_m3u8_file(file_path)

# 执行查找与更新
find_and_update_m3u8_files(folder_path)