import subprocess
import re
import cv2
from datetime import timedelta, datetime
import os

def extract_subtitle(video_path, ffmpeg_path, subtitle_output="subtitle.srt"):
    """FFmpeg를 사용하여 자막을 추출하고 기존 파일을 덮어씀"""
    command = [
        ffmpeg_path,  # 사용자가 지정한 ffmpeg 경로
        "-y",  # 기존 파일 덮어씀
        "-fflags", "+genpts",
        "-i", video_path,
        "-map", "0:s:0",
        subtitle_output
    ]
    subprocess.run(command, check=True)
    return subtitle_output

def parse_gps_from_subtitle(subtitle_file, target_time):
    """자막 파일에서 특정 시간에 해당하는 GPS 정보를 추출하고 `n/a` 처리"""
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

def capture_frame(video_path, target_time, output_image="capture.jpg"):
    """OpenCV를 사용하여 특정 시간의 프레임을 캡처"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("비디오 파일을 열 수 없습니다.")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(fps * target_time)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_image, frame)
        print(f"{output_image}에 프레임 저장 완료")
    else:
        print("프레임을 읽을 수 없습니다.")

    cap.release()
    return output_image

def process_drone_video(video_path, ffmpeg_path, target_time):
    """전체 프로세스: 자막 추출, GPS 정보 파싱, 프레임 캡처"""
    subtitle_file = extract_subtitle(video_path, ffmpeg_path)

    latitude, longitude = parse_gps_from_subtitle(subtitle_file, target_time)

    if latitude is not None and longitude is not None:
        print(f"GPS 좌표: 위도 {latitude}, 경도 {longitude}")
    else:
        print("GPS 정보를 찾을 수 없습니다.")

    # 파일 이름 구분자 설정
    video_name = os.path.splitext(os.path.basename(video_path))[0]  # 파일명만 추출
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_image = f"{video_name}_capture_{target_time}s_{timestamp}.jpg"

    capture_frame(video_path, target_time, output_image)


# 예제 실행
# video_path = "C:\\Users\\seongjae\\Downloads\\dji_fly_20241101_031516_6_1730398858018_video\\dji_fly_20241101_031516_6_1730398858018_video.mp4"  # 실제 파일 경로로 변경
video_path = "C:\\Users\seongjae\Downloads\Dji drone 비디오\dji_fly_20241101_031840_7_1730398841244_video.mp4"
ffmpeg_path = "C:\\Users\\seongjae\\Downloads\\ffmpeg-2024-10-31-git-87068b9600-full_build\\bin\\ffmpeg.exe"  # 실제 FFmpeg 경로로 변경
target_time = 44  # 초 단위로 원하는 시간을 입력

process_drone_video(video_path, ffmpeg_path, target_time)
