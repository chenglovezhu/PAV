import os
import json

def format_json_file(file_path):
    """格式化指定路径的 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            json_data = json.loads(content)  # 检查 JSON 格式是否正确

        # 将 JSON 对象重新格式化并写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        print(f"已格式化：{file_path}")
    except (json.JSONDecodeError, OSError) as e:
        print(f"处理文件 {file_path} 时出错：{e}")

def process_folder(folder_path):
    """递归遍历文件夹，处理其中的所有 JSON 文件"""
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                json_file_path = os.path.join(root, file)
                format_json_file(json_file_path)
    