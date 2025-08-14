using GrpcGreeterService.Services;

var builder = WebApplication.CreateBuilder(args);

// Add gRPC services
builder.Services.AddGrpc();

// Add health checks
builder.Services.AddGrpcHealthChecks();

var app = builder.Build();

// Configure gRPC pipeline
app.MapGrpcService<GreeterService>();
app.MapGrpcHealthChecksService();

// Enable gRPC reflection in development
if (app.Environment.IsDevelopment())
{
    app.MapGrpcReflectionService();
}

app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
