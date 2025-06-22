using MongoDB.Driver;
using Microsoft.Extensions.Options;
using TaskAPI.Models;

namespace TaskAPI.Data;

public class MongoDbContext
{
    private readonly IMongoDatabase _database;

    public MongoDbContext(IOptions<MongoDbSettings> settings)
    {
        var client = new MongoClient(settings.Value.ConnectionString);
        _database = client.GetDatabase(settings.Value.DatabaseName);
    }

    public IMongoCollection<User> Users => 
        _database.GetCollection<User>("users");

    public IMongoCollection<TaskItem> Tasks => 
        _database.GetCollection<TaskItem>("tasks");
}