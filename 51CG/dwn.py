import os
import requests
from multiprocessing import Pool
from urllib.parse import urljoin
from m3u8 import M3U8



# 解析 m3u8 文件，获取所有 TS 文件和 key 文件的 URL
def get_m3u8_data(m3u8_file_path):
    with open(m3u8_file_path, 'r', encoding='utf-8') as f:
        m3u8_data = f.read()
    
    # 使用 m3u8 库解析文件
    playlist = M3U8(m3u8_data)
    
    # 获取 base_uri，通常 m3u8 文件中的 ts 文件路径是相对路径，base_uri 是它们的根路径
    base_uri = playlist.base_uri
    
    # 获取 TS 文件和密钥文件的 URL
    ts_urls = [urljoin(base_uri, segment.uri) for segment in playlist.segments]
    key_url = urljoin(base_uri, playlist.keys[0].uri) if playlist.keys else None
    
    return ts_urls, key_url

# 下载单个文件
def download_file(url, save_path):
    try:
        # 获取文件
        response = requests.get(url, stream=True)
        # 检查请求是否成功
        response.raise_for_status()
        
        # 保存文件到指定路径
        with open(save_path, 'wb') as f:
            # 遍历文件内容，分块写入
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    except Exception as e:
        print(f"下载失败: {url}, 错误: {e}")

# 下载多个文件（通过多进程）
def download_files_parallel(urls, save_dir):
    # 如果保存目录不存在，则创建目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 使用 Pool 并行下载文件
    with Pool(processes=4) as pool:  # 设置进程数，通常 4 到 8 个进程是合理的
        pool.starmap(download_file, [(url, os.path.join(save_dir, os.path.basename(url))) for url in urls])

# 下载 key 文件
def download_key_file(key_url, save_dir):
    # 如果key不为空，则下载key文件
    if key_url:
        # 获取key文件的保存路径 
        key_file_path = os.path.join(save_dir, os.path.basename(key_url))
        # 下载key文件
        download_file(key_url, key_file_path)