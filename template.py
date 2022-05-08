import cv2
import argparse
import multiprocessing as mp

queue = mp.Queue(maxsize=300)

def gstreamer_camera(queue):
    # Use the provided pipeline to construct the video capture in opencv
    pipeline = (
        "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)1920, height=(int)1080, "
            "format=(string)NV12, framerate=(fraction)30/1 ! "
        "queue ! "
        "nvvidconv flip-method=2 ! "
            "video/x-raw, "
            "width=(int)1920, height=(int)1080, "
            "format=(string)BGRx, framerate=(fraction)30/1 ! "
        "videoconvert ! "
            "video/x-raw, format=(string)BGR ! "
        "appsink"
    )
    # Complete the function body
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print('error')
                break
            print('receive frame')
            queue.put(frame)
    except KeyboardInterrupt as e:
        cap.release()



def gstreamer_rtmpstream(queue):
    # Use the provided pipeline to construct the video writer in opencv
    pipeline = (
        "appsrc ! "
            "video/x-raw, format=(string)BGR ! "
        "queue ! "
        "videoconvert ! "
            "video/x-raw, format=RGBA ! "
        "nvvidconv ! "
        "nvv4l2h264enc bitrate=8000000 ! "
        "h264parse ! "
        "flvmux ! "
        'rtmpsink location="rtmp://localhost/rtmp/live live=1"'
    )
    # Complete the function body
    # You can apply some simple computer vision algorithm here
    #pass
    out = cv2.VideoWriter(pipeline, 0, 25, (1920, 1080))
    try:
        while True:
            frame = queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print('process frame')
            try:
                out.write(frame)
            except:
                print('err')
    except KeyboardInterrupt as e:
        out.release()



# Complelte the code
if __name__ == '__main__':
    p1 = mp.Process(target=gstreamer_camera, args=(queue,))
    p2 = mp.Process(target=gstreamer_rtmpstream, args=(queue,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
