import argparse
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--algo", type=str, default="NONE")
    args = vars(parser.parse_args())
    print(args)
    try:
        while True:
            # send gRPC request to tell server process start streaming
            # run ffplay
            subprocess.run(['ffplay', '-fflags', 'nobuffer', 'rtmp://192.168.55.1/rtmp/live'])
    except KeyboardInterrupt as e:
        print("\nstop!!\n")
        # send gPRC request to tell server process terminate streaming