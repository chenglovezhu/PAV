import os
import json
import uuid
import subprocess


def get_codec_info(input_video):
    # 检查输入视频文件是否存在
    if not os.path.isfile(input_video):
        raise FileNotFoundError(f"输入视频文件未找到: {input_video}")
    
    # 使用 FFmpeg 获取视频和音频的编解码信息
    ffprobe_command = [
        'ffprobe', '-v', 'error', '-show_entries',
        'stream=width,height,bit_rate,r_frame_rate,codec_name,codec_type,duration',
        '-of', 'json', input_video
    ]
    
    try:
        result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True, timeout=600)
        codec_info = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"无法获取视频编解码信息: {e.stderr}")
    except json.JSONDecodeError:
        raise ValueError("无法解析 FFprobe 输出的 JSON 信息")
    except subprocess.TimeoutExpired:
        raise TimeoutError("获取编解码信息超时")

    # 默认值设置
    video_codec = None
    audio_codec = None
    bit_rate = None
    r_frame_rate = None
    w, h = None, None

    # 提取编解码信息
    for stream in codec_info.get('streams', []):
        if stream.get('codec_type') == 'video':
            video_codec = stream.get('codec_name')
            bit_rate = int(stream.get('bit_rate', 0)) // 1000  # 转换为 kbps
            r_frame_rate = stream.get('r_frame_rate')
            w, h = stream.get('width'), stream.get('height')
        elif stream.get('codec_type') == 'audio':
            audio_codec = stream.get('codec_name')

    # 处理帧率（如果存在的话，将分数格式的帧率转为浮点数）
    if r_frame_rate:
        try:
            num, denom = map(int, r_frame_rate.split('/'))
            r_frame_rate = num / denom
        except ValueError:
            r_frame_rate = None
    
    return video_codec, audio_codec, bit_rate, r_frame_rate, w, h

def convert_to_encrypted_hls(input_video, output_dir, key_info):
    # 检查输出目录是否存在
    if not os.path.isdir(output_dir):
        raise FileNotFoundError(f"输出目录未找到: {output_dir}")

    # 获取视频和音频的编码信息
    video_codec, audio_codec, bit_rate, r_frame_rate, w, h = get_codec_info(input_video)
    
    # 构建 FFmpeg 命令
    ffmpeg_command = ['ffmpeg', '-i', input_video]
    
    # 检查视频是否符合 HLS 要求
    if video_codec == 'h264':
        ffmpeg_command.extend(['-c:v', 'copy'])  # 视频编码符合，直接复制
    else:
        ffmpeg_command.extend(['-c:v', 'libx264'])  # 视频编码不符合，进行转换
        if bit_rate:
            ffmpeg_command.extend(['-b:v', f"{bit_rate}k"])  # 设置视频比特率
        if r_frame_rate:
            ffmpeg_command.extend(['-r', f"{r_frame_rate}"])  # 设置视频帧率
    
    if audio_codec == 'aac':
        ffmpeg_command.extend(['-c:a', 'copy'])  # 音频编码符合，直接复制
    else:
        ffmpeg_command.extend(['-c:a', 'aac'])  # 音频编码不符合，进行转换
    
    # 设置 HLS 和加密参数
    ffmpeg_command.extend([
        '-hls_time', '10',  # 每个切片的时长（秒）
        '-hls_key_info_file', key_info,  # 加密密钥信息文件
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', os.path.join(output_dir, f"{str(uuid.uuid4())}%05d.ts"),  # 输出的切片文件
        os.path.join(output_dir, 'playlist.m3u8')  # 输出的播放列表文件
    ])
    
    # 运行 FFmpeg 命令
    try:
        # 使用 subprocess.run 运行 FFmpeg 命令，并捕获错误输出
        subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, timeout=3600)
        return w, h, os.path.join(output_dir, 'playlist.m3u8')
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg 处理失败: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise TimeoutError("FFmpeg 处理超时")
    


# 测试代码：仅在直接运行此脚本时执行
if __name__ == "__main__":
    
    input_video = "/Users/cc/Downloads/【VIP】奶昔 - 绿背心 [169P1V-29.3G]/b7ca1f22beb80d6b027b16fa25ceae15/奶昔 - 绿背心.mp4"
    output_dir = os.path.dirname(input_video)
    
    key_info = "/Users/cc/Documents/CC_Self/CCFiles/Files/VKey/ALL/key.keyinfo"
    
    convert_to_encrypted_hls(input_video, output_dir, key_info)