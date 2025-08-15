#!/bin/bash
# generate_grpc.sh - Generate Python gRPC code from Protocol Buffer files

set -e

echo "🔧 Generating gRPC Python Code from Protocol Buffers"
echo "=================================================="

# Create output directory for generated code
PROTO_DIR="protos"
OUTPUT_DIR="protos"

# Create __init__.py files to make it a Python package
touch "$OUTPUT_DIR/__init__.py"

# Check if protoc is installed
if ! command -v python -m grpc_tools.protoc &> /dev/null; then
    echo "❌ grpcio-tools not found. Installing..."
    pip install grpcio-tools
fi

# Generate Python code from proto files
echo "📦 Generating code from auth.proto..."
python -m grpc_tools.protoc \
    -I${PROTO_DIR} \
    --python_out=${OUTPUT_DIR} \
    --grpc_python_out=${OUTPUT_DIR} \
    ${PROTO_DIR}/auth.proto

echo "📦 Generating code from user.proto..."
python -m grpc_tools.protoc \
    -I${PROTO_DIR} \
    --python_out=${OUTPUT_DIR} \
    --grpc_python_out=${OUTPUT_DIR} \
    ${PROTO_DIR}/user.proto

echo "📦 Generating code from common.proto..."
python -m grpc_tools.protoc \
    -I${PROTO_DIR} \
    --python_out=${OUTPUT_DIR} \
    --grpc_python_out=${OUTPUT_DIR} \
    ${PROTO_DIR}/common.proto

# Fix imports in generated files (common issue with protobuf)
echo "🔧 Fixing import paths..."

# Fix auth_pb2_grpc.py imports
if [ -f "${OUTPUT_DIR}/auth_pb2_grpc.py" ]; then
    sed -i 's/import auth_pb2 as auth__pb2/from . import auth_pb2 as auth__pb2/g' "${OUTPUT_DIR}/auth_pb2_grpc.py"
fi

# Fix user_pb2_grpc.py imports
if [ -f "${OUTPUT_DIR}/user_pb2_grpc.py" ]; then
    sed -i 's/import user_pb2 as user__pb2/from . import user_pb2 as user__pb2/g' "${OUTPUT_DIR}/user_pb2_grpc.py"
fi

# Fix common_pb2_grpc.py imports
if [ -f "${OUTPUT_DIR}/common_pb2_grpc.py" ]; then
    sed -i 's/import common_pb2 as common__pb2/from . import common_pb2 as common__pb2/g' "${OUTPUT_DIR}/common_pb2_grpc.py"
fi

# List generated files
echo "✅ Generated files:"
ls -la ${OUTPUT_DIR}/*_pb2.py ${OUTPUT_DIR}/*_pb2_grpc.py 2>/dev/null || echo "No files generated"

echo ""
echo "🎉 gRPC code generation completed!"
echo ""
echo "Generated files:"
echo "  - auth_pb2.py       : Auth service message classes"
echo "  - auth_pb2_grpc.py  : Auth service gRPC stub and servicer"
echo "  - user_pb2.py       : User service message classes" 
echo "  - user_pb2_grpc.py  : User service gRPC stub and servicer"
echo "  - common_pb2.py     : Common message classes"
echo "  - common_pb2_grpc.py: Common service gRPC stub and servicer"
echo ""
echo "Usage in Python:"
echo "  from protos import auth_pb2, auth_pb2_grpc"
echo "  from protos import user_pb2, user_pb2_grpc"
echo "  from protos import common_pb2, common_pb2_grpc"
