import os
import mediapipe
import cv2
import subprocess
import multiprocessing as mp
import os.path as osp
import sys
BUILD_DIR = osp.join(osp.dirname(osp.abspath(__file__)), "build/service/")
sys.path.insert(0, BUILD_DIR)
import argparse

import grpc
from concurrent import futures
import fib_pb2
import fib_pb2_grpc
print(cv2.__version__)

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
    # retval = cv2.VideoCapture.isOpened(cap)
    # print('retval: ', retval)
    # print(cap)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print('error')
                # print(frame)
            else:
                # print('receive frame')
                queue.put(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt as e:
        cap.release()

def algo1(image):
    # hand tracking
    mp_hands = mediapipe.solutions.hands
    mp_drawing_styles = mediapipe.solutions.drawing_styles
    mp_drawing = mediapipe.solutions.drawing_utils
    with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        return image

def algo2(image):
    # object detection
    mp_object_detection = mediapipe.solutions.object_detection
    mp_drawing = mediapipe.solutions.drawing_utils 
    with mp_object_detection.ObjectDetection(
        min_detection_confidence=0.1) as object_detection:

        results = object_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(image, detection)

        return image

def algo3(image):
    # pose estimation
    mp_drawing = mediapipe.solutions.drawing_utils
    mp_drawing_styles = mediapipe.solutions.drawing_styles
    mp_pose = mediapipe.solutions.pose

    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        # Flip the image horizontally for a selfie-view display.
        return image    

def gstreamer_rtmpstream(queue, algo):
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
    algo_number=1
    try:
        while True:
            frame = queue.get()
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # print('process frame')
            if not algo.empty():
                algo_idx = algo.get()
                print(f'algo: {algo_idx}')
                algo_number = algo_idx

            if algo_number==1:
                frame = algo1(frame)
            elif algo_number==2:
                frame = algo2(frame)
            elif algo_number==3:
                frame = algo3(frame)
            else:
                print('NO ALGO')
                    
            try:
                out.write(frame)
            except:
                print('err')
    except KeyboardInterrupt as e:
        out.release()

class FibCalculatorServicer(fib_pb2_grpc.FibCalculatorServicer):

    def __init__(self):
        self.subprocess = False

    def Compute(self, request, context):
        n = request.order
        value = 1
        if n==10:
            print("algo 1")
            algo.put(1)
        if n==11:
            print("algo 2")
            algo.put(2)
        if n==12:
            print("algo 3")
            algo.put(3)
        elif n==9:
            print("stop streaming")
            value = 0
            # self.stream_process.terminate()
            # p1.join()
            # p2.join()

        response = fib_pb2.FibResponse()
        response.value = value

        return response

    def _fibonacci(self, n):
        a = 0
        b = 1
        if n < 0:
            return 0
        elif n == 0:
            return 0
        elif n == 1:
            return b
        else:
            for i in range(1, n):
                c = a + b
                a = b
                b = c
            return b

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", type=str)
    parser.add_argument("--port", default=8080, type=int)
    args = vars(parser.parse_args())

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = FibCalculatorServicer()
    fib_pb2_grpc.add_FibCalculatorServicer_to_server(servicer, server)

    try:
        algo = mp.Queue(maxsize=1)
        queue = mp.Queue(maxsize=300)
        # default val
        algo.put(1)
        p1 = mp.Process(target=gstreamer_camera, args=(queue,))
        p2 = mp.Process(target=gstreamer_rtmpstream, args=(queue,algo))
        p1.start()
        p2.start()

        
        server.add_insecure_port(f"{args['ip']}:{args['port']}")
        server.start()
        print(f"Run gRPC Server at {args['ip']}:{args['port']}")
        server.wait_for_termination()
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        pass