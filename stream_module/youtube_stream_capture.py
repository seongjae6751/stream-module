import cv2
import time
import streamlink


def capture_stream(youtube_url, capture_interval):
    # streamlink로 유튜브 스트림 URL을 가져옴
    streams = streamlink.streams(youtube_url)
    if "best" not in streams:
        print("스트림을 찾을 수 없습니다.")
        return

    # 가장 좋은 품질의 스트림 선택
    stream_url = streams["best"].url

    # OpenCV 비디오 캡처 객체 생성
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        print("스트림에 연결할 수 없습니다.")
        return

    frame_count = 0  # 캡처된 프레임 수를 추적

    try:
        while True:
            # 프레임 읽기
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            # 캡처된 프레임을 파일로 저장
            filename = f"capture_{frame_count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"{filename} 저장 완료")

            frame_count += 1
            time.sleep(capture_interval)  # 설정한 시간 간격 동안 대기
    except KeyboardInterrupt:
        print("캡처를 중단합니다.")
    finally:
        # 스트림 해제
        cap.release()
        cv2.destroyAllWindows()
