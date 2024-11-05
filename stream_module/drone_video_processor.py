import subprocess
import re
import cv2
from datetime import timedelta, datetime
import os

def extract_subtitle(video_path, ffmpeg_path, output_folder, subtitle_output=None):
    """FFmpeg를 사용하여 자막을 추출하고 지정된 폴더에 저장"""
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    subtitle_output = subtitle_output or f"{video_name}_subtitle.srt"
    subtitle_path = os.path.join(output_folder, subtitle_output)

    command = [
        ffmpeg_path,
        "-y",
        "-fflags", "+genpts",
        "-i", video_path,
        "-map", "0:s:0",
        subtitle_path
    ]
    subprocess.run(command, check=True)
    return subtitle_path

def parse_gps_from_subtitle(subtitle_file, target_time):
    """자막 파일에서 특정 시간에 해당하는 GPS 정보를 추출하고 `n/a` 처리합니다."""
    with open(subtitle_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    target_timecode = str(timedelta(seconds=target_time))
    gps_data = None
    previous_gps = None
    next_gps = None

    for i in range(len(lines)):
        if target_timecode in lines[i]:
            gps_line = lines[i + 1] if (i + 1) < len(lines) else ""
            match = re.search(r"GPS\s*\(([^)]+)\)", gps_line)
            if match:
                gps_data = match.group(1)
            break

    if gps_data and 'n/a' in gps_data:
        for j in range(i - 1, -1, -1):
            match = re.search(r"GPS\s*\(([^)]+)\)", lines[j])
            if match and 'n/a' not in match.group(1):
                previous_gps = match.group(1)
                break

        for k in range(i + 1, len(lines)):
            match = re.search(r"GPS\s*\(([^)]+)\)", lines[k])
            if match and 'n/a' not in match.group(1):
                next_gps = match.group(1)
                break

        if previous_gps and next_gps:
            prev_lat, prev_lon = map(float, previous_gps.split(",")[:2])
            next_lat, next_lon = map(float, next_gps.split(",")[:2])
            latitude = (prev_lat + next_lat) / 2
            longitude = (prev_lon + next_lon) / 2
        elif previous_gps:
            latitude, longitude = map(float, previous_gps.split(",")[:2])
        elif next_gps:
            latitude, longitude = map(float, next_gps.split(",")[:2])
        else:
            latitude, longitude = None, None
    else:
        if gps_data:
            gps_values = gps_data.split(",")
            latitude = gps_values[0].strip() if gps_values[0].strip() != "n/a" else None
            longitude = gps_values[1].strip() if gps_values[1].strip() != "n/a" else None
        else:
            latitude, longitude = None, None

    return latitude, longitude

def capture_frame(video_path, target_time, output_folder, output_image=None):
    """OpenCV를 사용하여 특정 시간의 프레임을 캡처하고 지정된 폴더에 저장"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("비디오 파일을 열 수 없습니다.")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(fps * target_time)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_image = output_image or f"{video_name}_capture_{target_time}s_{timestamp}.jpg"
    output_image_path = os.path.join(output_folder, output_image)

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_image_path, frame)
        print(f"{output_image_path}에 프레임 저장 완료")
    else:
        print("프레임을 읽을 수 없습니다.")

    cap.release()
    return output_image_path

def process_drone_video(video_path, ffmpeg_path, target_time, output_folder):
    """전체 프로세스: 자막 추출, GPS 정보 파싱, 프레임 캡처"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    subtitle_file = extract_subtitle(video_path, ffmpeg_path, output_folder)
    latitude, longitude = parse_gps_from_subtitle(subtitle_file, target_time)

    if latitude is not None and longitude is not None:
        print(f"GPS 좌표: 위도 {latitude}, 경도 {longitude}")
    else:
        print("GPS 정보를 찾을 수 없습니다.")

    capture_frame(video_path, target_time, output_folder)