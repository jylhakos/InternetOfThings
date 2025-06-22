using TaskAPI.Models;

namespace TaskAPI.Services;

public interface ITaskService
{
    Task<List<TaskItem>> GetAllAsync(string userId);
    Task<TaskItem?> GetByIdAsync(string id, string userId);
    Task<TaskItem> CreateAsync(TaskItem task);
    Task<TaskItem?> UpdateAsync(string id, string userId, TaskItem task);
    Task<bool> DeleteAsync(string id, string userId);
    Task<List<TaskItem>> GetByFiltersAsync(string userId, bool? isCompleted = null, TaskPriority? priority = null);
}