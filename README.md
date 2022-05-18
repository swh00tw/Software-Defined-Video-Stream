# Software-Defined-Video-Stream

NTUEE NMLAB-2022-spring homework

# Setup

Clone repo first
```
cd Software-Defined-Video-Stream
```

Compile
```
# Install protobuf compiler
$ sudo apt-get install protobuf-compiler

# Install buildtools
$ sudo apt-get install build-essential make

# Install grpc packages
$ pip3 install -r requirements.txt

# compile
$ make
```

# Run server on Nano

```
$ python3 server.py
```

# Run client on your host

Use different image processing algorithms:

ALGO_NUMBER 10 --> hand tracking

ALGO_NUMBER 11 --> object detection

ALGO_NUMBER 12 --> pose estimation

```
$ python3 client.py --order ${ALGO_NUMBER_YOU_WANT}
$ ffplay -fflags nobuffer rtmp://192.168.55.1/rtmp/live
```
