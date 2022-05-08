GRPC_DIR = service
GRPC_BUILD_DIR = build
GRPC_FILES = $(wildcard $(GRPC_DIR)/*.proto)
GRPC_PYTHON := $(GRPC_FILES:%.proto=$(GRPC_BUILD_DIR)/%_pb2.py)
GRPC_PROTO_PYTHON := $(GRPC_FILES:%.proto=$(GRPC_BUILD_DIR)/%_pb2_grpc.py)

all: grpc_generate

clean:
	echo "Clean get called"

grpc_generate: $(GRPC_PYTHON) $(GRPC_PROTO_PYTHON)
	$(info GRPC: Done generating python files based on *.proto files.)

$(GRPC_BUILD_DIR)/%_pb2.py: %.proto
	$(shell mkdir -p $(dir $@))
	python3 -m grpc_tools.protoc -I=$(GRPC_DIR) --python_out=$(dir $@) $<

$(GRPC_BUILD_DIR)/%_pb2_grpc.py: %.proto
	$(shell mkdir -p $(dir $@))
	python3 -m grpc_tools.protoc -I=$(GRPC_DIR) --grpc_python_out=$(dir $@) $<
