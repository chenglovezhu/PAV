import requests
import json
import time

def fetch_konachan_data(num_iterations=10, page_limit=1, save_file="/data/ccav/ALLProcess/dataKonachan.txt"):
    
    base_url = "https://konachan.com/post.json"

    proxies = {
    "http": "http://127.0.0.1:7897",  # 本地代理地址
    "https": "http://127.0.0.1:7897"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Cookie": "country=GB; blacklisted_tags=%5B%22%22%5D; konachan.com=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTZjZjQ2ODM2ZTA1MWQyYTcyZTcyNzdhYzM4Y2ZmMjkzBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMWh6Z2JpU0FyRDZPRi9zTVZBKzdjc0U5SEQ3cGtQaHRhSW1INnozOEpOdVk9BjsARg%3D%3D--bce3698d1e2ed3581902582b1f88468dd21812b8; __utma=235754395.708138956.1731919253.1731919253.1731919253.1; __utmc=235754395; __utmz=235754395.1731919253.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); forum_post_last_read_at=%222024-11-18T09%3A40%3A54%2B01%3A00%22; vote=1; cf_clearance=FQv01EVzQBR_YXYw4qyXQKB2KVD_Tzk6F9qt5_YVgxw-1731985034-1.2.1.1-nx3mMb9ymLvHfIKFeJf24mqR2PmDF2EVu4hlwNexla25Qm6VdoJOkb9d5Np4evlHX5gUCxRI.bvWeio1pYSRD99ONfvlmQfnVB3osECPfExlrDhGNGgn3y.6_c7UGpAKNrWjAVgLWB6LYhEp6LTm0Exl0fa1qN7hFXEZzpCX2kRLcMXUszogY_WqpShzHqSFvYk_9EyBZTzHdb2dSDBuYN8Dn0sTJvKcqDT7d89ls7vZU9HoTpsIL7CaAtZD8jq2uKxG6iK.8uluw7B_Y7XhrzRrBSc4H3gHaMEsxnG0BMcq.gH3cxTWCMaH21Q3J2w5SC5z_8ezJs5K45SByW.6rYFe6ptWs8R6SD0A8PjW4s1o4L7MexL_9ad7XP4FASOayTvdjGZeQdPMXV91t9vavfCiFsGSXQnxKLvKX7Yiwy8"  # 将此处替换为实际的Cookie
    }
    
    with open(save_file, "w", encoding="utf-8") as file:
        for page in range(1, num_iterations + 1):
            # 设置请求参数
            params = {
                "page": page,
                "limit": page_limit
            }
            
            while True:
                try:
                    # 请求API
                    response = requests.get(base_url, headers=headers ,params=params, proxies=proxies)
                    response.raise_for_status()  # 检查请求是否成功
                    data = response.json()
                    
                    # 将数据写入文件
                    for post in data:
                        file.write(json.dumps(post, ensure_ascii=False) + "\n")
                    
                    print(f"第 {page} 页数据保存成功！")
                    break # 请求成功，跳出无限循环
                    
                except requests.RequestException as e:
                    print(f"Error fetching data on page {page}: {e}")                     
                    # 适当的延时，避免过多请求
                    time.sleep(5)

if __name__ == "__main__":
    fetch_konachan_data(num_iterations=400, page_limit=1000)  # 设置循环次数和每页数据量