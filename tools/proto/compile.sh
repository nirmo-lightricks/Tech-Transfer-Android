#!/bin/bash

DIR=`git rev-parse --show-toplevel`

cd $DIR/app/proto
mkdir -p ../jni/protobuf
../../third_party/protobuf/bin/protoc *.proto --cpp_out=../jni/protobuf
