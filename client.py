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

# algo = 10, use 1st algorithm
# algo = 11, use 1st algorithm
# algo = 12, use 1st algorithm
# isStart = 9, end streaming
def gRPC_request(ip, port, algo):
    host = f"{ip}:{port}"
    print(host)
    with grpc.insecure_channel(host) as channel:
        stub = fib_pb2_grpc.FibCalculatorStub(channel)

        request = fib_pb2.FibRequest()
        request.order = algo

        response = stub.Compute(request)
        print(response.value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--order", type=int, default=0)
    args = vars(parser.parse_args())

    print(args)
    try:
        # send gRPC request to tell server process start streaming
        gRPC_request('192.168.55.1', 8080, args["order"])
    except KeyboardInterrupt as e:
        # gRPC_request('192.168.55.1', 8080, 9)
        print("\nstop!!\n")
        # send gPRC request to tell server process terminate streaming