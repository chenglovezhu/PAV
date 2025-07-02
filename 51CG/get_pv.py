import os
import json
import time
import requests
from bs4 import BeautifulSoup
from dwn import get_m3u8_data, download_files_parallel, download_key_file

# 写入已成功下载文章的数据
def write_successful(f, c):
    with open(f, "a") as file:
        file.write(f"{c}\n")

# 读取已成功写入的数据
def read_successful(f):
    with open(f, "r") as file:
        article_list = [line.strip() for line in file.readlines()]  # 去掉换行符
        return article_list

# 获取需要下载的文章id
def g_51_c_d(f):

    id_list = []

    with open(f, "r") as f:
        a_i_s = f.readlines()
    
    for a_i in a_i_s:
            try:
                a_d = json.loads(a_i)
                a_id = f"{a_d['url']}"
                id_list.append(a_id)

            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e} - 文章内容: {article.strip()}")

    return id_list

# 创建51CG类，主要用于获取视频的m3u8文件
class GetPV:
    
    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Cookie": "_ga=GA1.1.782270987.1734054142; _ga_P6HKH41365=GS1.1.1734054142.1.1.1734055322.18.0.0"  # 将此处替换为实际的Cookie
        }
    
    def get_context_data(self):
        '''
        获取文章的pv数据
        '''
        while True:
            try:
                # 请求
                response = requests.get(f"{self.url}", headers=self.headers)
                
                if response.status_code == 200:
                    return response.content  # 请求成功，返回内容
                else:
                    print(f"请求失败，状态码: {response.status_code}")  # 输出失败状态码
                    time.sleep(5)  # 等待5秒后重试
                
            except requests.RequestException as e:
                # 记录或处理异常
                print(f"请求发生异常: {e}")
                time.sleep(2)  # 等待2秒后重试
    
    def get_pv_data(self, context):
        '''
        获取文章的pv数据
        '''
        # 创建soup对象
        soup = BeautifulSoup(context, 'html.parser')
        # 获取文章标题
        title = soup.find('div', id='post').find('article').find('h1').get_text(strip=True).replace("/", " ")
        m3u8_urls = []
        
        # 获取dplayer对象
        dplayers = soup.find_all('div', class_='dplayer')
        # 获取m3u8文件链接
        if dplayers:
            for dplayer in dplayers:
                data_config = dplayer.get('data-config')
                # 将 data-config 的值转换为字典
                config_dict = json.loads(data_config.replace("&quot;", '"'))
                # 提取 m3u8 文件链接
                m3u8_url = config_dict.get('video', {}).get('url')
                m3u8_urls.append(m3u8_url)
                
        return {
            "title": title,
            "m3u8_url_list": m3u8_urls
        }
    
    def save_pv_m3u8(self, m3u8_url, title, save_dir):
        '''
        保存m3u8文件
        '''
        while True:  # 保持无限重试
            try:
                # 请求
                response = requests.get(f"{m3u8_url}", headers=self.headers)
                
                if response.status_code == 200:
                    with open(f"{os.path.join(save_dir, title)}.m3u8", 'wb') as file:  # 使用 'wb' 模式以处理二进制内容
                        file.write(response.content)  # 直接写入内容而不是转换为字符串
                    return  f"{os.path.join(save_dir, title)}.m3u8"
                else:
                    print(f"请求失败，状态码: {response.status_code}")  # 输出失败状态码
                    time.sleep(5)  # 等待5秒后重试
                
            except requests.RequestException as e:
                # 记录或处理异常
                print(f"请求发生异常: {e}")
                time.sleep(2)  # 等待2秒后重试
    


if __name__ == "__main__":
    
    # 已下载数据路径
    successful_data = "successful.txt"
    # 需要下载数据路径
    download_data = input("请输入需要下载的数据文件(如:MRDS.txt ：")
    # 下载视频文件的网站链接
    base_url = input("请输入要抓取的URL（如：https://wikiwiki.plzyjff.xyz/）：")

    # 判断是否已成功写入的数据
    if os.path.exists(successful_data):
        # 读取已成功写入的数据
        downloaded_data_list = read_successful(successful_data)

    else:
        data_list = []
    
    a_id_list = g_51_c_d(download_data)

    for a_id in a_id_list:
         
        #  判断文章是否已下载
        if a_id in downloaded_data_list:
            print(f"文章 ：{a_id} 已下载，无须再次下载！已跳过......")
            break
        
        # 创建51CG对象，获取相应的m3u8文件
        v = GetPV(f"{base_url}{a_id}")

        page_context = v.get_context_data()
        page_pv_data = v.get_pv_data(page_context)

        for index, m3u8_url in enumerate(page_pv_data['m3u8_url_list']):

            save_dir = os.path.join("Articles", page_pv_data['title'])
            os.makedirs(f"{save_dir}_{index}", exist_ok=True)
            m3u8_file = v.save_pv_m3u8(m3u8_url, f"{page_pv_data['title']}", save_dir=f"{save_dir}_{index}")

            # 解析m3u8文件
            print(f"{page_pv_data['title']}_{index} m3u8文件保存成功, 将开始解析m3u8文件, 请稍等...")
            ts_urls, key_url = get_m3u8_data(m3u8_file)
        
            # 下载key文件和ts文件
            print(f"开始下载key文件, 请稍等...")
            download_key_file(key_url=key_url, save_dir=f"{save_dir}_{index}")
            print(f"开始下载ts文件, 请稍等...")
            download_files_parallel(ts_urls, save_dir=f"{save_dir}_{index}")
            print(f"下载当前视频完成, 开始写入已成功写入的数据")
    

        # 写入已成功写入的数据
        print(f"已下载当前文章的所有视频, 开始写入已成功下载文件的数据！")
        write_successful(successful_data, f"{a_id}")
        print(f"写入完成!")
