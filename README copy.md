# gRPC-with-protobuf

## How to run
- Install project dependencies
```bash
# Install protobuf compiler
$ sudo apt-get install protobuf-compiler

# Install buildtools
$ sudo apt-get install build-essential make

# Install grpc packages
$ pip3 install -r requirements.txt
```
- Compile protobuf schema to python wrapper
```bash
$ make
```
- Start the gRPC service
```bash
$ python3 server.py --ip 0.0.0.0 --port 8080
```
- Start the gRPC client
```bash
# You will get 55 value computed by the grpc service
$ python3 client.py --ip localhost --port 8080 --order 10
```
