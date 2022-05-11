# Software-Defined-Video-Stream
NTUEE NMLAB-2022-spring homework

# Setup

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

# Run server
```
$ python3 server.py --ip 0.0.0.0 --port 8080
```

# Run client
```
$ python3 client.py
```
