# Example: Greeter Service with gRPC

This directory contains gRPC service and client examples.
- Protocol Buffers (protobuf) definitions
- gRPC server implementation with ASP.NET Core
- gRPC client implementation
- Automated testing

## Project Structure

```
gRPC/
├── test-grpc.sh                    # Automated test script
├── GrpcGreeterService/             # gRPC Server
│   ├── GrpcGreeterService.csproj   # Project file
│   ├── Program.cs                  # Server configuration
│   ├── Dockerfile                  # Container configuration
│   ├── Protos/
│   │   └── greet.proto             # Protocol Buffer definitions
│   └── Services/
│       └── GreeterService.cs       # Service implementation
└── GrpcGreeterClient/              # gRPC Client
    ├── GrpcGreeterClient.csproj    # Project file
    ├── Program.cs                  # Client application
    └── Protos/
        └── greet.proto             # Protocol Buffer definitions (client copy)
```

## Quick Start

### 1. Test Everything (Recommended)
```bash
# Run automated test (builds and tests both service and client)
./test-grpc.sh
```

### 2. Manual Testing

#### Start the gRPC Service
```bash
cd GrpcGreeterService
dotnet run
# Service will start on https://localhost:7042
```

#### Run the gRPC Client (in another terminal)
```bash
cd GrpcGreeterClient
dotnet run
```

## Service Features

The gRPC service implements three methods:

1. **SayHello** - Simple unary call
   ```protobuf
   rpc SayHello (HelloRequest) returns (HelloReply);
   ```

2. **SayHelloToMany** - Bi-directional streaming
   ```protobuf
   rpc SayHelloToMany (stream HelloRequest) returns (stream HelloReply);
   ```

3. **GetServerInfo** - Server metadata
   ```protobuf
   rpc GetServerInfo (Empty) returns (ServerInfo);
   ```

## Protocol Buffer Definition

The `greet.proto` file defines:

```protobuf
syntax = "proto3";

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply);
  rpc SayHelloToMany (stream HelloRequest) returns (stream HelloReply);
  rpc GetServerInfo (Empty) returns (ServerInfo);
}

message HelloRequest {
  string name = 1;
  string message = 2;
}

message HelloReply {
  string message = 1;
  int32 timestamp = 2;
}

message ServerInfo {
  string version = 1;
  string environment = 2;
  int64 startup_time = 3;
}
```

## Testing with grpcurl

If you have `grpcurl` installed, you can test the service directly:

```bash
# Install grpcurl (Ubuntu/Debian)
sudo apt install grpcurl

# Test SayHello method
grpcurl -plaintext -d '{"name":"World","message":"Hello"}' \
  localhost:7042 greet.Greeter/SayHello

# Get server info
grpcurl -plaintext -d '{}' \
  localhost:7042 greet.Greeter/GetServerInfo
```

## Docker Deployment

Build and run the gRPC service in a container:

```bash
cd GrpcGreeterService

# Build the Docker image
docker build -t grpc-greeter-service .

# Run the container
docker run -p 7042:8080 grpc-greeter-service
```

## Development Notes

### Client Project Configuration

The client project includes the necessary NuGet packages:
- `Grpc.Net.Client` - gRPC client library
- `Google.Protobuf` - Protocol Buffers runtime
- `Grpc.Tools` - Code generation tools

### Code Generation

The proto files are automatically compiled into C# classes during build:
- Server: `GrpcServices="Server"` generates server base classes
- Client: `GrpcServices="Client"` generates client stub classes

### Troubleshooting

1. **SSL Certificate Issues**
   ```bash
   # Trust the development certificate
   dotnet dev-certs https --trust
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port 7042
   sudo lsof -i :7042
   # Kill the process if needed
   sudo kill -9 <PID>
   ```

3. **Connection Refused**
   - Ensure the service is running before starting the client
   - Check firewall settings
   - Verify the correct URL and port

## Next

1. **Add Authentication**: Implement JWT or certificate-based authentication
2. **Add Interceptors**: For logging, metrics, or cross-cutting concerns
3. **Health Checks**: Implement gRPC health checking protocol
4. **Service Discovery**: Integrate with Consul or similar
5. **Load Balancing**: Configure client-side or server-side load balancing
