import os
import json
import time
import requests
from bs4 import BeautifulSoup
from dwn import get_m3u8_data, download_files_parallel, download_key_file

# 写入已成功下载文章的数据
def write_successful(content):
    with open("51CG/successful.txt", "a") as file:
        file.write(f"{content}\n")

# 读取已成功写入的数据
def read_successful():
    with open("51CG/successful.txt", "r") as file:
        article_list = [line.strip() for line in file.readlines()]  # 去掉换行符
        return article_list

# 创建51CG类
class GetPV:
    
    def __init__(self, data_file):
        self.base_url = "https://break.qyjgqjwj.com"
        self.proxies = {
            "http": "http://127.0.0.1:7897",  # 本地代理地址
            "https": "http://127.0.0.1:7897"
            }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Cookie": "_ga=GA1.1.782270987.1734054142; _ga_P6HKH41365=GS1.1.1734054142.1.1.1734055322.18.0.0"  # 将此处替换为实际的Cookie
        }
        self.data_file = data_file

    def get_pv_url(self):
        """
        获取文章的pv地址:list
        """
        article_list = []
        
        with open(self.data_file, 'r') as file:
            articles = file.readlines()
        
        for article in articles:
            try:
                article_data = json.loads(article)  # 添加异常处理
                article_url = f"{self.base_url}{article_data['url']}"
                article_list.append(article_url)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e} - 文章内容: {article.strip()}")  # 输出错误信息和内容
        
        return article_list
    
    def get_context_data(self, article_url):
        '''
        获取文章的pv数据
        '''
        while True:
            try:
                # 请求
                response = requests.get(f"{article_url}", headers=self.headers, proxies=self.proxies)
                
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
                response = requests.get(f"{m3u8_url}", headers=self.headers, proxies=self.proxies)
                
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
    
    # 判断是否已成功写入的数据
    if os.path.exists("51CG/successful.txt"):
        # 读取已成功写入的数据
        data_list = read_successful()
    else:
        data_list = []
    
    # 创建对象  
    get_pv = GetPV("51CG/tmp.txt")
    # 获取文章列表
    urls = get_pv.get_pv_url()
    # 遍历文章列表
    for url in urls:
        # 判断是否已成功写入，如果已成功写入，则跳过
        if url in data_list:
            print(f"文章 {url} 已成功下载过, 即将跳过...")
            continue
        
        # 获取文章数据
        print(f"正在获取 {url} 的文章HTML数据, 请稍等...") 
        context = get_pv.get_context_data(url)
        
        # 获取文章的pv数据
        """"
        返回数据格式：
        {
            "title": "文章标题",
            "m3u8_url_list": ["m3u8文件链接1", "m3u8文件链接2", ...]
        }
        """
        print(f"文章HTML数据获取成功, 正在解析文章数据, 请稍等...")
        article_info = get_pv.get_pv_data(context)
        
        # 保存m3u8文件
        print(f"文章数据解析成功, 将开始保存m3u8文件, 请稍等...")
        save_dir = os.path.join("51CG/Articles", article_info['title'])
        
        for index, m3u8_url in enumerate(article_info['m3u8_url_list']):
            # 创建保存目录
            os.makedirs(f"{save_dir}_{index}", exist_ok=True)
            m3u8_file = get_pv.save_pv_m3u8(m3u8_url, f"{article_info['title']}_{index}", save_dir=f"{save_dir}_{index}")
        
            # 解析m3u8文件
            print(f"{article_info['title']}_{index} m3u8文件保存成功, 将开始解析m3u8文件, 请稍等...")
            ts_urls, key_url = get_m3u8_data(m3u8_file)
        
            # 下载key文件和ts文件
            print(f"开始下载key文件, 请稍等...")
            download_key_file(key_url=key_url, save_dir=f"{save_dir}_{index}")
            print(f"开始下载ts文件, 请稍等...")
            download_files_parallel(ts_urls, save_dir=f"{save_dir}_{index}")
            print(f"下载当前视频完成, 开始写入已成功写入的数据")
            
        # 写入已成功写入的数据
        print(f"已下载当前文章的所有视频, 开始写入已成功下载文件的数据")
        write_successful(f"{url}")
        print(f"写入完成")