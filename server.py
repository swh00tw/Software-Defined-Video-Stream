import os
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

# queue = mp.Queue(maxsize=300)

# def gstreamer_camera(queue):
#     # Use the provided pipeline to construct the video capture in opencv
#     pipeline = (
#         "nvarguscamerasrc ! "
#             "video/x-raw(memory:NVMM), "
#             "width=(int)1920, height=(int)1080, "
#             "format=(string)NV12, framerate=(fraction)30/1 ! "
#         "queue ! "
#         "nvvidconv flip-method=2 ! "
#             "video/x-raw, "
#             "width=(int)1920, height=(int)1080, "
#             "format=(string)BGRx, framerate=(fraction)30/1 ! "
#         "videoconvert ! "
#             "video/x-raw, format=(string)BGR ! "
#         "appsink"
#     )
#     # Complete the function body
#     cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 print('error')
#                 print(frame)
#                 break
#             print('receive frame')
#             queue.put(frame)
#     except KeyboardInterrupt as e:
#         cap.release()

# def gstreamer_rtmpstream(queue):
#     # Use the provided pipeline to construct the video writer in opencv
#     pipeline = (
#         "appsrc ! "
#             "video/x-raw, format=(string)BGR ! "
#         "queue ! "
#         "videoconvert ! "
#             "video/x-raw, format=RGBA ! "
#         "nvvidconv ! "
#         "nvv4l2h264enc bitrate=8000000 ! "
#         "h264parse ! "
#         "flvmux ! "
#         'rtmpsink location="rtmp://localhost/rtmp/live live=1"'
#     )
#     # Complete the function body
#     # You can apply some simple computer vision algorithm here
#     #pass
#     out = cv2.VideoWriter(pipeline, 0, 25, (1920, 1080))
#     try:
#         while True:
#             frame = queue.get()
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             print('process frame')
#             try:
#                 out.write(frame)
#             except:
#                 print('err')
#     except KeyboardInterrupt as e:
#         out.release()

# p1 = mp.Process(target=gstreamer_camera, args=(queue,))
# p2 = mp.Process(target=gstreamer_rtmpstream, args=(queue,))

class FibCalculatorServicer(fib_pb2_grpc.FibCalculatorServicer):

    def __init__(self):
        pass

    def Compute(self, request, context):
        n = request.order
        if (n==10):
            print("start streaming")
            value = 1
            self.stream_process = subprocess.Popen(['python', 'template.py'])
        elif n==9:
            print("stop streaming")
            value = 0
            subprocess.terminate(self.stream_process)

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
        server.add_insecure_port(f"{args['ip']}:{args['port']}")
        server.start()
        print(f"Run gRPC Server at {args['ip']}:{args['port']}")
        server.wait_for_termination()
        cv2.waitKey()
    except KeyboardInterrupt:
        cv2.waitKey()
        pass
