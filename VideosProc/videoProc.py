import os
import subprocess
import json
import uuid
import hashlib
import shutil

# 获取视频文件的M扩展名值
def get_file_extension(filename):
    return os.path.splitext(filename)[1]

# 获取视频文件的MD5值
def get_file_md5(filepath):
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error calculating MD5 for {filepath}: {e}")
        return None

# 生成视频信息
def get_full_video_info(input_video, md5, json_info):
    # 判断视频文件是否存在
    if not os.path.isfile(input_video):
        raise FileNotFoundError(f"Input video file not found: {input_video}")

    ffprobe_command = [
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', input_video
    ]
    
    try:
        result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)

        video_info['streams'] = sorted(
            video_info['streams'],
            key=lambda x: 0 if x['codec_type'] == 'video' else 1
        )
        
        video_info['format']['filename'] = os.path.basename(input_video)
        video_info['format']['md5'] = md5
        video_info['format']['ext'] = get_file_extension(input_video)
        video_info['format']['mime'] = f"{video_info['streams'][0]['codec_type']}/{video_info['format']['ext'].lstrip('.')}"

        with open(json_info, 'w', encoding='utf-8') as f:
            json.dump(video_info, f, ensure_ascii=False, indent=4)
        print(f"Full video information saved to {json_info}")
    
    except subprocess.CalledProcessError as e:
        print(f"FFprobe error: {e.stderr}")
    except json.JSONDecodeError:
        print("Unable to parse JSON from FFprobe output")

def convert_to_encrypted_hls_from_json(json_info, key_info, output_dir):
    if not os.path.isdir(output_dir):
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    with open(json_info, 'r', encoding='utf-8') as f:
        codec_info = json.load(f)

    video_codec, audio_codec, bit_rate, r_frame_rate, w, h = None, None, None, None, None, None

    for stream in codec_info.get('streams', []):
        if stream.get('codec_type') == 'video' and stream.get('codec_name') != 'mjpeg' :
            video_codec = stream.get('codec_name')
            bit_rate = int(stream.get('bit_rate', 0)) // 1000
            r_frame_rate = stream.get('r_frame_rate')
            w, h = stream.get('width'), stream.get('height')
        elif stream.get('codec_type') == 'audio':
            audio_codec = stream.get('codec_name')

    if r_frame_rate:
        try:
            num, denom = map(int, r_frame_rate.split('/'))
            r_frame_rate = num / denom
        except ValueError:
            r_frame_rate = None
   
    ffmpeg_command = ['ffmpeg', '-i',  os.path.join(os.path.dirname(json_info), codec_info['format']['filename'])]
    
    if video_codec == 'h264':
        ffmpeg_command.extend(['-c:v', 'copy'])
    else:
        ffmpeg_command.extend(['-c:v', 'libx264'])
        if bit_rate:
            ffmpeg_command.extend(['-b:v', f"{bit_rate}k"])
        if r_frame_rate:
            ffmpeg_command.extend(['-r', f"{r_frame_rate}"])

    if audio_codec == 'aac':
        ffmpeg_command.extend(['-c:a', 'copy'])
    else:
        ffmpeg_command.extend(['-c:a', 'aac'])
    
    ffmpeg_command.extend([
        '-hls_time', '10',
        '-hls_key_info_file', key_info,
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', os.path.join(output_dir, f"{str(uuid.uuid4())}%05d.ts"),
        os.path.join(output_dir, 'playlist.m3u8')
    ])
    
    try:
        print("Running command:", " ".join(ffmpeg_command))
        subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, timeout=3600)
        os.remove(os.path.join(os.path.dirname(json_info), codec_info['format']['filename']))
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg processing failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise TimeoutError("FFmpeg processing timed out")

def process_video_file(video_path, key_info):
    
    # 判断视频文件路径是否存在
    if not os.path.isfile(video_path):
        print(f"Invalid path or file not found: {video_path}")
        return
    # 判断MD5是否正确生成
    fMD5 = get_file_md5(video_path)
    if not fMD5:
        print(f"Failed to calculate MD5 for {video_path}")
        return
    
    # 构造文件保存路径
    base_dir = os.path.join(os.path.dirname(video_path), fMD5)
    json_info = os.path.join(base_dir, f"{str(uuid.uuid4())}.json")
    
    # 判断视频流是否已存在
    if os.path.exists(base_dir):
        os.makedirs(os.path.join(os.path.dirname(video_path), "Exist"), exist_ok=True)
        shutil.move(video_path, os.path.join(os.path.dirname(video_path), "Exist"))
        return
    
    # 如果视频流不存在，则继续
    os.makedirs(base_dir, exist_ok=True)

    try:
        get_full_video_info(video_path, fMD5, json_info)
        shutil.move(video_path, base_dir)
        print(f"Moved video to {base_dir}")
        convert_to_encrypted_hls_from_json(json_info, key_info, base_dir)
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")

if __name__ == "__main__":
    
    # 定义数据文件
    video_data = "/Users/cc/Documents/CC_Self/CCHome/ALLProcess/VideosProc/videoData.txt"
    # 定义Key密钥
    key_info = "/Users/cc/Documents/CC_Self/CCFiles/Files/VKey/ALL/key.keyinfo"
    
    ccNub = 0
    
    with open(video_data, 'r') as file:
        for video_path in map(str.strip, file):
            print(f"正在处理第 {ccNub} 个文件：{video_path}")
            if os.path.exists(video_path):
                process_video_file(video_path, key_info)
                ccNub = ccNub + 1