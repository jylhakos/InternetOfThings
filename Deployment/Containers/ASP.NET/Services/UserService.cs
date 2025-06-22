using MongoDB.Driver;
using TaskAPI.Data;
using TaskAPI.Models;

namespace TaskAPI.Services;

public class UserService : IUserService
{
    private readonly IMongoCollection<User> _users;

    public UserService(MongoDbContext context)
    {
        _users = context.Users;
    }

    public async Task<List<User>> GetAllAsync()
    {
        return await _users.Find(_ => true).ToListAsync();
    }

    public async Task<User?> GetByIdAsync(string id)
    {
        return await _users.Find(user => user.Id == id).FirstOrDefaultAsync();
    }

    public async Task<User?> GetByEmailAsync(string email)
    {
        return await _users.Find(user => user.Email == email.ToLowerInvariant()).FirstOrDefaultAsync();
    }

    public async Task<User> CreateAsync(User user)
    {
        user.Email = user.Email.ToLowerInvariant();
        user.CreatedAt = DateTime.UtcNow;
        await _users.InsertOneAsync(user);
        return user;
    }

    public async Task<User?> UpdateAsync(string id, User user)
    {
        user.Email = user.Email.ToLowerInvariant();
        await _users.ReplaceOneAsync(u => u.Id == id, user);
        return user;
    }

    public async Task<bool> DeleteAsync(string id)
    {
        var result = await _users.DeleteOneAsync(user => user.Id == id);
        return result.DeletedCount > 0;
    }
}