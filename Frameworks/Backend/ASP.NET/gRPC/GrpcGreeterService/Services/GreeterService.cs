using Grpc.Core;
using GrpcGreeterService;

namespace GrpcGreeterService.Services;

public class GreeterService : Greeter.GreeterBase
{
    private readonly ILogger<GreeterService> _logger;
    private static readonly DateTime _startupTime = DateTime.UtcNow;

    public GreeterService(ILogger<GreeterService> logger)
    {
        _logger = logger;
    }

    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
    {
        _logger.LogInformation("Received greeting request from {Name}", request.Name);
        
        return Task.FromResult(new HelloReply
        {
            Message = $"Hello {request.Name}! {request.Message}",
            Timestamp = (int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()
        });
    }

    public override async Task SayHelloToMany(IAsyncStreamReader<HelloRequest> requestStream,
        IServerStreamWriter<HelloReply> responseStream, ServerCallContext context)
    {
        await foreach (var request in requestStream.ReadAllAsync())
        {
            _logger.LogInformation("Streaming greeting to {Name}", request.Name);
            
            await responseStream.WriteAsync(new HelloReply
            {
                Message = $"Hello {request.Name}! {request.Message}",
                Timestamp = (int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            });
        }
    }

    public override Task<ServerInfo> GetServerInfo(Empty request, ServerCallContext context)
    {
        return Task.FromResult(new ServerInfo
        {
            Version = "1.0.0",
            Environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Unknown",
            StartupTime = ((DateTimeOffset)_startupTime).ToUnixTimeSeconds()
        });
    }
}
