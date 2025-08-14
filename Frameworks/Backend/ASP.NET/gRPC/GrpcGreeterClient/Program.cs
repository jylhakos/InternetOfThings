using Grpc.Net.Client;
using GrpcGreeterClient;

Console.WriteLine("🚀 gRPC Greeter Client Starting...");
Console.WriteLine("=====================================");

// Create gRPC channel
using var channel = GrpcChannel.ForAddress("https://localhost:7042");
var client = new Greeter.GreeterClient(channel);

try
{
    Console.WriteLine("📡 Testing gRPC Service Connection...\n");

    // Test 1: Simple unary call
    Console.WriteLine("🔹 Test 1: Simple Greeting");
    var reply = await client.SayHelloAsync(new HelloRequest 
    { 
        Name = "World", 
        Message = "Hello from gRPC Client!" 
    });
    Console.WriteLine($"✅ Server Response: {reply.Message}");
    Console.WriteLine($"⏰ Timestamp: {DateTimeOffset.FromUnixTimeSeconds(reply.Timestamp)}\n");

    // Test 2: Get server info
    Console.WriteLine("🔹 Test 2: Server Information");
    var serverInfo = await client.GetServerInfoAsync(new Empty());
    Console.WriteLine($"📊 Server Version: {serverInfo.Version}");
    Console.WriteLine($"🌐 Environment: {serverInfo.Environment}");
    Console.WriteLine($"🚀 Startup Time: {DateTimeOffset.FromUnixTimeSeconds(serverInfo.StartupTime)}\n");

    // Test 3: Multiple greetings
    Console.WriteLine("🔹 Test 3: Multiple Greetings");
    var names = new[] { "Alice", "Bob", "Charlie" };
    
    foreach (var name in names)
    {
        var greeting = await client.SayHelloAsync(new HelloRequest
        {
            Name = name,
            Message = $"Greetings from {name}!"
        });
        Console.WriteLine($"👋 {greeting.Message}");
    }

    Console.WriteLine("\n✅ All tests completed successfully!");
}
catch (Exception ex)
{
    Console.WriteLine($"❌ Error calling gRPC service: {ex.Message}");
    Console.WriteLine("\n💡 Make sure the gRPC server is running on https://localhost:7042");
    Console.WriteLine("   You can start it by running: dotnet run --project ../GrpcGreeterService");
}

Console.WriteLine("\n🎯 Press any key to exit...");
Console.ReadKey();
