import requests
import time
from bs4 import BeautifulSoup

def fetch_article_data(url, sg, eg, save_file):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Cookie": "_ga=GA1.1.782270987.1734054142; _ga_P6HKH41365=GS1.1.1734054142.1.1.1734055322.18.0.0"  # 将此处替换为实际的Cookie
    }
    
    with open(save_file, "a", encoding="utf-8") as file:
        
        for page in range(sg, eg + 1):
            
            while True:
                try:
                    # 请求
                    response = requests.get(f"{url}{page}/", headers=headers)
                    response.raise_for_status()  # 检查请求是否成功
                    
                    # 创建 BeautifulSoup 对象
                    soup = BeautifulSoup(response.content, 'lxml')

                    # 提取所有标题内容# 精准定位到包含特定标题的 <a> 标签
                    target_articles = soup.find_all('article', itemtype="http://schema.org/BlogPosting")  # 定位父级 <article>
                    
                    for target_article in target_articles:
                        target_url = target_article.find('a', href=True)  # 在特定 <article> 下查找 <a> 标签
                        target_title = target_article.find('h2', class_='post-card-title')
                        
                        if target_title and target_title.get_text(strip=True) and target_title.get_text(strip=True)!="热搜 HOT":
                            # print(f"url: {target_url['href']}, title: {target_title.get_text(strip=True)}")
                            file.write(f'{{"url": "{target_url["href"]}", "title": "{target_title.get_text(strip=True).replace("\"", " ")}"}}\n') 
                    print(f"第 {page} 页数据保存成功！")
                    break # 请求成功，跳出无限循环
                    
                except requests.RequestException as e:
                    print(f"Error fetching data on page {page}: {e}")                     
                    # 适当的延时，避免过多请求
                    time.sleep(5)


if __name__ == "__main__":
    
    url = input("请输入要抓取的URL（如：https://wikiwiki.plzyjff.xyz/category/xsxy/）：")
    sg = int(input("请输入起始页码（sg 如：100）："))
    eg = int(input("请输入结束页码（eg 如：100）："))
    save_file = input("请输入保存文件名（如 output.txt）：")

    fetch_article_data(url=url, sg=sg, eg=eg, save_file=save_file)

