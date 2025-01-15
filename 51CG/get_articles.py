import requests
import time
from bs4 import BeautifulSoup


def fetch_article_data(num_iterations=1, save_file="51CG/20250114.txt"):
    
    base_url = "https://break.qyjgqjwj.com/page/"

    proxies = {
    "http": "http://127.0.0.1:7890",  # 本地代理地址
    "https": "http://127.0.0.1:7890"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Cookie": "_ga=GA1.1.782270987.1734054142; _ga_P6HKH41365=GS1.1.1734054142.1.1.1734055322.18.0.0"  # 将此处替换为实际的Cookie
    }
    
    with open(save_file, "a", encoding="utf-8") as file:
        for page in range(50, num_iterations + 1):
            
            while True:
                try:
                    # 请求
                    response = requests.get(f"{base_url}{page}/", headers=headers, proxies=proxies)
                    response.raise_for_status()  # 检查请求是否成功
                    
                    # 创建 BeautifulSoup 对象
                    soup = BeautifulSoup(response.content, 'lxml')
                    # 提取所有标题内容# 精准定位到包含特定标题的 <a> 标签
                    target_articles = soup.find_all('article', itemtype="http://schema.org/BlogPosting")  # 定位父级 <article>
                    
                    for target_article in target_articles:
                        target_url = target_article.find('a', href=True)  # 在特定 <article> 下查找 <a> 标签
                        target_title = target_article.find('h2', class_='post-card-title')
                        
                        if target_title.get_text(strip=True) and target_title.get_text(strip=True)!="热搜 HOT":
                            # print(f"url: {target_url['href']}, title: {target_title.get_text(strip=True)}")
                            file.write("{" + f"\"url\": \"{target_url['href']}\", \"title\": \"{target_title.get_text(strip=True)}.replace('\"', ' ')\"" + "}" + "\n")
                        
                    print(f"第 {page} 页数据保存成功！")
                    break # 请求成功，跳出无限循环
                    
                except requests.RequestException as e:
                    print(f"Error fetching data on page {page}: {e}")                     
                    # 适当的延时，避免过多请求
                    time.sleep(5)

if __name__ == "__main__":
    fetch_article_data(num_iterations=80)  # 设置循环次数和每页数据量