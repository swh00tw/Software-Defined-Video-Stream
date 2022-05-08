import os
import subprocess
import multiprocessing as mp
import os.path as osp
import sys
BUILD_DIR = osp.join(osp.dirname(osp.abspath(__file__)), "build/service/")
sys.path.insert(0, BUILD_DIR)
import argparse

import grpc
import fib_pb2
import fib_pb2_grpc

def main(args):
    host = f"{args['ip']}:{args['port']}"
    print(host)
    with grpc.insecure_channel(host) as channel:
        stub = fib_pb2_grpc.FibCalculatorStub(channel)

        request = fib_pb2.FibRequest()
        request.order = args['order']

        response = stub.Compute(request)
        print(response.value)

# isStart = 10, start streaming
# isStart = 9, end streaming
def gRPC_request(ip, port, isStart, algo):
    host = f"{ip}:{port}"
    print(host)
    with grpc.insecure_channel(host) as channel:
        stub = fib_pb2_grpc.FibCalculatorStub(channel)

        request = fib_pb2.FibRequest()
        request.order = isStart

        response = stub.Compute(request)
        print(response.value)

def ffplay():
    subprocess.run(['ffplay', '-fflags', 'nobuffer', 'rtmp://192.168.55.1/rtmp/live'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--algo", type=str, default="NONE")
    args = vars(parser.parse_args())
    # subprocess.run(['ffplay', '-fflags', 'nobuffer', 'rtmp://192.168.55.1/rtmp/live'])
    print(args)
    p1 = mp.Process(target=ffplay)
    try:
        # send gRPC request to tell server process start streaming
        gRPC_request('192.168.55.1', 8080, 10, "NONE")
        p1.start()
    except KeyboardInterrupt as e:
        gRPC_request('192.168.55.1', 8080, 9, "NONE")
        p1.join()
        print("\nstop!!\n")
        # send gPRC request to tell server process terminate streaming