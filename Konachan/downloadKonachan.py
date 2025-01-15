import os
import json
import requests
import time

# 文件路径
baseDir = "/data/ccav/ALLProcess/KonachanFiles"
file_path = "/data/ccav/ALLProcess/KData_20241129.txt"
success_log_path = "/data/ccav/ALLProcess/KonachanFiles/success.txt"
error_log_path = "/data/ccav/ALLProcess/KonachanFiles/error.txt"

# 配置下载参数
proxies = {
    "http": "http://127.0.0.1:7897",  # 本地代理地址
    "https": "http://127.0.0.1:7897"
    }
    
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Cookie": "country=GB; blacklisted_tags=%5B%22%22%5D; konachan.com=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTZjZjQ2ODM2ZTA1MWQyYTcyZTcyNzdhYzM4Y2ZmMjkzBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMWh6Z2JpU0FyRDZPRi9zTVZBKzdjc0U5SEQ3cGtQaHRhSW1INnozOEpOdVk9BjsARg%3D%3D--bce3698d1e2ed3581902582b1f88468dd21812b8; __utma=235754395.708138956.1731919253.1731919253.1731919253.1; __utmc=235754395; __utmz=235754395.1731919253.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); forum_post_last_read_at=%222024-11-18T09%3A40%3A54%2B01%3A00%22; vote=1; cf_clearance=FQv01EVzQBR_YXYw4qyXQKB2KVD_Tzk6F9qt5_YVgxw-1731985034-1.2.1.1-nx3mMb9ymLvHfIKFeJf24mqR2PmDF2EVu4hlwNexla25Qm6VdoJOkb9d5Np4evlHX5gUCxRI.bvWeio1pYSRD99ONfvlmQfnVB3osECPfExlrDhGNGgn3y.6_c7UGpAKNrWjAVgLWB6LYhEp6LTm0Exl0fa1qN7hFXEZzpCX2kRLcMXUszogY_WqpShzHqSFvYk_9EyBZTzHdb2dSDBuYN8Dn0sTJvKcqDT7d89ls7vZU9HoTpsIL7CaAtZD8jq2uKxG6iK.8uluw7B_Y7XhrzRrBSc4H3gHaMEsxnG0BMcq.gH3cxTWCMaH21Q3J2w5SC5z_8ezJs5K45SByW.6rYFe6ptWs8R6SD0A8PjW4s1o4L7MexL_9ad7XP4FASOayTvdjGZeQdPMXV91t9vavfCiFsGSXQnxKLvKX7Yiwy8"  # 将此处替换为实际的Cookie
}

# 读取已成功下载的文件记录到一个集合中
downloaded_urls = set()
if os.path.exists(success_log_path):
    with open(success_log_path, "r", encoding="utf-8") as success_log:
        for line in success_log:
            try:
                data = json.loads(line.strip())
                downloaded_urls.add(data["file_url"])
            except json.JSONDecodeError:
                print("跳过success.txt中无法解析的行")

# 逐行读取和处理
with open(file_path, "r", encoding="utf-8") as file, \
     open(success_log_path, "a", encoding="utf-8") as success_log, \
     open(error_log_path, "a", encoding="utf-8") as error_log:
    
    for line_num, line in enumerate(file, start=1):
        try:
            # 解析每一行的 JSON 数据
            data = json.loads(line.strip())
            
            # 提取 file_url 和 rating
            file_url = data["file_url"]
            rating = data["rating"]

            # 检查 file_url 是否已经下载过
            if file_url in downloaded_urls:
                print(f"第 {line_num} 行的文件已下载，将跳过本次下载......")
                continue

            # 检查 file_url 是否已经下载过
            if rating == 's':
                print(f"第 {line_num} 行的文件属于安全文件，将跳过本次下载......")
                continue

            # 设置保存路径
            output_dir = os.path.join(baseDir, rating)  # 使用 rating 作为文件夹名称
            os.makedirs(output_dir, exist_ok=True)

            # 提取文件名并构建完整保存路径
            file_name = file_url.split("/")[-1]
            output_path = os.path.join(output_dir, file_name)

            # 尝试下载图片
            while True:
                try:
                    
                    response = requests.get(file_url, headers=headers ,proxies=proxies)  # 添加超时时间
                    
                    if response.status_code == 200:
                        # 下载成功，保存图片
                        with open(output_path, "wb") as img_file:
                            img_file.write(response.content)
                        # 记录成功的 JSON 数据到 success.txt
                        success_log.write(json.dumps(data) + "\n")
                        success_log.flush()  # 立即写入文件
                        print(f"第 {line_num} 行的图片已保存至 {output_path}")
                        break

                    elif response.status_code == 404:
                        # 如果状态码为 404，跳过并记录到 error 文件
                        error_log.write(json.dumps(data) + "\n")
                        error_log.flush()
                        print(f"第 {line_num} 行 - 404 错误: {file_url}，已记录到 error.txt")
                        break

                    else:
                        print(f"第 {line_num} 行下载失败 (状态码: {response.status_code})，即将重试......")
                        time.sleep(5)  # 等待5秒后重试

                except requests.exceptions.RequestException as req_err:
                    print(f"第 {line_num} 行请求失败，原因: {req_err}，即将重试......")
                    time.sleep(5)

        except json.JSONDecodeError:
            error_log.write(line.strip() + "\n")
            error_log.flush()
            print(f"第 {line_num} 行的 JSON 数据解析失败，已记录到 error.txt")
        except KeyError:
            error_log.write(line.strip() + "\n")
            error_log.flush()
            print(f"第 {line_num} 行的 JSON 数据缺少必要的键，已记录到 error.txt")
        except Exception as e:
            error_log.write(line.strip() + "\n")
            error_log.flush()
            print(f"第 {line_num} 行处理时出现错误: {e}，已记录到 error.txt")
