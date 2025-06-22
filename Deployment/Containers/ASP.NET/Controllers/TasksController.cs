using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using TaskAPI.Models;
using TaskAPI.Services;

namespace TaskAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TasksController : ControllerBase
{
    private readonly ITaskService _taskService;
    private readonly ILogger<TasksController> _logger;

    public TasksController(ITaskService taskService, ILogger<TasksController> logger)
    {
        _taskService = taskService;
        _logger = logger;
    }

    private string GetUserId()
    {
        return User.FindFirst("userId")?.Value ?? 
               User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? 
               string.Empty;
    }

    /// <summary>
    /// Get all tasks for the authenticated user
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<TaskResponse>>> GetTasks(
        [FromQuery] bool? isCompleted = null,
        [FromQuery] TaskPriority? priority = null)
    {
        try
        {
            var userId = GetUserId();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized();
            }

            List<TaskItem> tasks;
            
            if (isCompleted.HasValue || priority.HasValue)
            {
                tasks = await _taskService.GetByFiltersAsync(userId, isCompleted, priority);
            }
            else
            {
                tasks = await _taskService.GetAllAsync(userId);
            }

            var response = tasks.Select(task => new TaskResponse
            {
                Id = task.Id,
                Title = task.Title,
                Description = task.Description,
                IsCompleted = task.IsCompleted,
                Priority = task.Priority,
                DueDate = task.DueDate,
                UserId = task.UserId,
                CreatedAt = task.CreatedAt,
                UpdatedAt = task.UpdatedAt,
                Tags = task.Tags
            }).ToList();

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving tasks for user {UserId}", GetUserId());
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    /// <summary>
    /// Get a specific task by ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<TaskResponse>> GetTask(string id)
    {
        try
        {
            var userId = GetUserId();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized();
            }

            var task = await _taskService.GetByIdAsync(id, userId);
            
            if (task == null)
            {
                return NotFound(new { message = "Task not found" });
            }

            var response = new TaskResponse
            {
                Id = task.Id,
                Title = task.Title,
                Description = task.Description,
                IsCompleted = task.IsCompleted,
                Priority = task.Priority,
                DueDate = task.DueDate,
                UserId = task.UserId,
                CreatedAt = task.CreatedAt,
                UpdatedAt = task.UpdatedAt,
                Tags = task.Tags
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving task {TaskId} for user {UserId}", id, GetUserId());
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    /// <summary>
    /// Create a new task
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<TaskResponse>> CreateTask([FromBody] TaskCreateRequest request)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var userId = GetUserId();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized();
            }

            var task = new TaskItem
            {
                Title = request.Title,
                Description = request.Description,
                Priority = request.Priority,
                DueDate = request.DueDate,
                UserId = userId,
                Tags = request.Tags ?? new List<string>()
            };

            var createdTask = await _taskService.CreateAsync(task);

            var response = new TaskResponse
            {
                Id = createdTask.Id,
                Title = createdTask.Title,
                Description = createdTask.Description,
                IsCompleted = createdTask.IsCompleted,
                Priority = createdTask.Priority,
                DueDate = createdTask.DueDate,
                UserId = createdTask.UserId,
                CreatedAt = createdTask.CreatedAt,
                UpdatedAt = createdTask.UpdatedAt,
                Tags = createdTask.Tags
            };

            _logger.LogInformation("Task created successfully: {TaskId} for user {UserId}", createdTask.Id, userId);
            return CreatedAtAction(nameof(GetTask), new { id = createdTask.Id }, response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating task for user {UserId}", GetUserId());
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    /// <summary>
    /// Update a task
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<TaskResponse>> UpdateTask(string id, [FromBody] TaskUpdateRequest request)
    {
        try
        {
            var userId = GetUserId();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized();
            }

            var existingTask = await _taskService.GetByIdAsync(id, userId);
            if (existingTask == null)
            {
                return NotFound(new { message = "Task not found" });
            }

            // Update only provided fields
            if (!string.IsNullOrEmpty(request.Title))
                existingTask.Title = request.Title;
            
            if (request.Description != null)
                existingTask.Description = request.Description;
            
            if (request.IsCompleted.HasValue)
                existingTask.IsCompleted = request.IsCompleted.Value;
            
            if (request.Priority.HasValue)
                existingTask.Priority = request.Priority.Value;
            
            if (request.DueDate.HasValue)
                existingTask.DueDate = request.DueDate.Value;
            
            if (request.Tags != null)
                existingTask.Tags = request.Tags;

            var updatedTask = await _taskService.UpdateAsync(id, userId, existingTask);
            
            if (updatedTask == null)
            {
                return NotFound(new { message = "Task not found" });
            }

            var response = new TaskResponse
            {
                Id = updatedTask.Id,
                Title = updatedTask.Title,
                Description = updatedTask.Description,
                IsCompleted = updatedTask.IsCompleted,
                Priority = updatedTask.Priority,
                DueDate = updatedTask.DueDate,
                UserId = updatedTask.UserId,
                CreatedAt = updatedTask.CreatedAt,
                UpdatedAt = updatedTask.UpdatedAt,
                Tags = updatedTask.Tags
            };

            _logger.LogInformation("Task updated successfully: {TaskId} for user {UserId}", id, userId);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating task {TaskId} for user {UserId}", id, GetUserId());
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    /// <summary>
    /// Delete a task
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteTask(string id)
    {
        try
        {
            var userId = GetUserId();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized();
            }

            var deleted = await _taskService.DeleteAsync(id, userId);
            
            if (!deleted)
            {
                return NotFound(new { message = "Task not found" });
            }

            _logger.LogInformation("Task deleted successfully: {TaskId} for user {UserId}", id, userId);
            return Ok(new { message = "Task deleted successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting task {TaskId} for user {UserId}", id, GetUserId());
            return StatusCode(500, new { message = "Internal server error" });
        }
    }
}