using MongoDB.Driver;
using TaskAPI.Data;
using TaskAPI.Models;

namespace TaskAPI.Services;

public class TaskService : ITaskService
{
    private readonly IMongoCollection<TaskItem> _tasks;

    public TaskService(MongoDbContext context)
    {
        _tasks = context.Tasks;
    }

    public async Task<List<TaskItem>> GetAllAsync(string userId)
    {
        return await _tasks
            .Find(task => task.UserId == userId)
            .SortByDescending(task => task.CreatedAt)
            .ToListAsync();
    }

    public async Task<TaskItem?> GetByIdAsync(string id, string userId)
    {
        return await _tasks
            .Find(task => task.Id == id && task.UserId == userId)
            .FirstOrDefaultAsync();
    }

    public async Task<TaskItem> CreateAsync(TaskItem task)
    {
        task.CreatedAt = DateTime.UtcNow;
        task.UpdatedAt = DateTime.UtcNow;
        await _tasks.InsertOneAsync(task);
        return task;
    }

    public async Task<TaskItem?> UpdateAsync(string id, string userId, TaskItem task)
    {
        task.UpdatedAt = DateTime.UtcNow;
        
        var result = await _tasks.ReplaceOneAsync(
            t => t.Id == id && t.UserId == userId, 
            task
        );

        return result.ModifiedCount > 0 ? task : null;
    }

    public async Task<bool> DeleteAsync(string id, string userId)
    {
        var result = await _tasks.DeleteOneAsync(task => task.Id == id && task.UserId == userId);
        return result.DeletedCount > 0;
    }

    public async Task<List<TaskItem>> GetByFiltersAsync(string userId, bool? isCompleted = null, TaskPriority? priority = null)
    {
        var filterBuilder = Builders<TaskItem>.Filter;
        var filter = filterBuilder.Eq(task => task.UserId, userId);

        if (isCompleted.HasValue)
        {
            filter &= filterBuilder.Eq(task => task.IsCompleted, isCompleted.Value);
        }

        if (priority.HasValue)
        {
            filter &= filterBuilder.Eq(task => task.Priority, priority.Value);
        }

        return await _tasks
            .Find(filter)
            .SortByDescending(task => task.CreatedAt)
            .ToListAsync();
    }
}