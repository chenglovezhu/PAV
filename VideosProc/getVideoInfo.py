import os
import json
import uuid
import hashlib
import shutil
import subprocess

def get_md5(file_path):
    try:
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        print(f"Error getting MD5: {str(e)}")
        return None
    
def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension


def get_file_extension(filename):
    return os.path.splitext(filename)[1]

def get_file_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_full_video_info(input_video, json_info):
    # 检查输入视频文件是否存在
    if not os.path.isfile(input_video):
        raise FileNotFoundError(f"Input video file not found: {input_video}")

    # 使用 FFprobe 获取完整的视频和音频信息
    ffprobe_command = [
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', input_video
    ]
    
    try:
        result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)

        # 对流信息进行排序，确保视频流在音频流之前
        video_info['streams'] = sorted(
            video_info['streams'],
            key=lambda x: 0 if x['codec_type'] == 'video' else 1
        )

        # 添加额外的信息：文件名、MD5、扩展名和 MIME 类型
        video_info['format']['filename'] = os.path.basename(video_info['format']['filename'])
        file_md5 = get_file_md5(input_video)
        video_info['format']['md5'] = file_md5
        video_info['format']['ext'] = get_file_extension(video_info['format']['filename'])
        video_info['format']['mime'] = f"{video_info['streams'][0]['codec_type']}/{video_info['format']['ext'].lstrip('.')}"
        
        # 将信息保存到 JSON 文件
        with open(json_info, 'w', encoding='utf-8') as f:
            json.dump(video_info, f, ensure_ascii=False, indent=4)
        print(f"Full video information saved to {json_info}")
    
    except subprocess.CalledProcessError as e:
        print(f"FFprobe error: {e.stderr}")
    except json.JSONDecodeError:
        print("Unable to parse JSON from FFprobe output")

# Usage example
if __name__ == "__main__":
    
    input_video = "/Users/cc/Downloads/NBDS/汤唯-色戒.mp4"  # Replace with actual video file path

    file_md5 = get_md5(input_video)
    if not file_md5:
        print("Failed to calculate MD5, exiting.")
    
    else:
        base_dir = os.path.join(os.path.dirname(input_video), file_md5)
        json_info = os.path.join(base_dir, f"{str(uuid.uuid4())}.json")
        
        os.makedirs(base_dir, exist_ok=True)
        
        get_full_video_info(input_video, json_info)
        
        # Move the input video to the new directory
        try:
            shutil.move(input_video, base_dir)
            print(f"Moved video to {base_dir}")
        except Exception as e:
            print(f"Error moving video file: {str(e)}")