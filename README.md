# stream-module
해양 데이터 해커톤을 위해 필요한 모듈 모음

## 사용예시
``` python
video_path = "C:\\Users\\seongjae\\Downloads\\Dji drone 비디오\\dji_fly_20241101_031840_7_1730398841244_video.mp4"  # 실제 파일 경로로 변경
ffmpeg_path = "C:\\Users\\seongjae\\Downloads\\ffmpeg-2024-10-31-git-87068b9600-full_build\\bin\\ffmpeg.exe"  # 실제 FFmpeg 경로로 변경
output_folder = "custom_directory"
target_time = 44  # 초 단위로 원하는 시간을 입력

process_drone_video(video_path, ffmpeg_path, target_time, output_folder)
```

## 유의 사항
ffmpeg는 별도로 다운 받을 것