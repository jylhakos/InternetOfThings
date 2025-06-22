<?php

namespace App\Controllers;

use App\Models\Task;
use App\Utils\ResponseHelper;
use App\Middleware\AuthMiddleware;

class TaskController 
{
    private Task $taskModel;
    
    public function __construct() 
    {
        $this->taskModel = new Task();
    }
    
    public function getAllTasks(): void 
    {
        $user = AuthMiddleware::authenticate();
        if (!$user) return;
        
        try {
            $filters = [
                'completed' => $_GET['completed'] ?? null,
                'priority' => $_GET['priority'] ?? null,
                'search' => $_GET['search'] ?? null
            ];
            
            $tasks = $this->taskModel->findByUser($user['id'], $filters);
            
            ResponseHelper::success([
                'tasks' => $tasks,
                'count' => count($tasks),
                'filters' => array_filter($filters)
            ]);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Failed to fetch tasks', 500);
        }
    }
    
    public function getTask(): void 
    {
        $user = AuthMiddleware::authenticate();
        if (!$user) return;
        
        try {
            $taskId = $_GET['id'] ?? null;
            
            if (!$taskId) {
                ResponseHelper::error('Task ID is required', 400);
                return;
            }
            
            $task = $this->taskModel->findByIdAndUser($taskId, $user['id']);
            
            if (!$task) {
                ResponseHelper::error('Task not found', 404);
                return;
            }
            
            ResponseHelper::success(['task' => $task]);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Failed to fetch task', 500);
        }
    }
    
    public function createTask(): void 
    {
        $user = AuthMiddleware::authenticate();
        if (!$user) return;
        
        try {
            $input = json_decode(file_get_contents('php://input'), true);
            
            if (!$this->validateTaskInput($input)) {
                ResponseHelper::error('Invalid task data', 400);
                return;
            }
            
            $taskData = [
                'title' => trim($input['title']),
                'description' => trim($input['description'] ?? ''),
                'priority' => $input['priority'] ?? 'medium',
                'due_date' => $input['due_date'] ?? null,
                'user_id' => $user['id'],
                'completed' => 0,
                'created_at' => date('Y-m-d H:i:s'),
                'updated_at' => date('Y-m-d H:i:s')
            ];
            
            $taskId = $this->taskModel->create($taskData);
            $task = $this->taskModel->findById($taskId);
            
            ResponseHelper::success([
                'message' => 'Task created successfully',
                'task' => $task
            ], 201);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Failed to create task', 500);
        }
    }
    
    public function updateTask(): void 
    {
        $user = AuthMiddleware::authenticate();
        if (!$user) return;
        
        try {
            $taskId = $_GET['id'] ?? null;
            
            if (!$taskId) {
                ResponseHelper::error('Task ID is required', 400);
                return;
            }
            
            $task = $this->taskModel->findByIdAndUser($taskId, $user['id']);
            
            if (!$task) {
                ResponseHelper::error('Task not found', 404);
                return;
            }
            
            $input = json_decode(file_get_contents('php://input'), true);
            
            $updateData = [
                'updated_at' => date('Y-m-d H:i:s')
            ];
            
            // Update only provided fields
            if (isset($input['title'])) {
                $updateData['title'] = trim($input['title']);
            }
            
            if (isset($input['description'])) {
                $updateData['description'] = trim($input['description']);
            }
            
            if (isset($input['priority'])) {
                $updateData['priority'] = $input['priority'];
            }
            
            if (isset($input['completed'])) {
                $updateData['completed'] = $input['completed'] ? 1 : 0;
            }
            
            if (isset($input['due_date'])) {
                $updateData['due_date'] = $input['due_date'];
            }
            
            $this->taskModel->update($taskId, $updateData);
            $updatedTask = $this->taskModel->findById($taskId);
            
            ResponseHelper::success([
                'message' => 'Task updated successfully',
                'task' => $updatedTask
            ]);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Failed to update task', 500);
        }
    }
    
    public function deleteTask(): void 
    {
        $user = AuthMiddleware::authenticate();
        if (!$user) return;
        
        try {
            $taskId = $_GET['id'] ?? null;
            
            if (!$taskId) {
                ResponseHelper::error('Task ID is required', 400);
                return;
            }
            
            $task = $this->taskModel->findByIdAndUser($taskId, $user['id']);
            
            if (!$task) {
                ResponseHelper::error('Task not found', 404);
                return;
            }
            
            $this->taskModel->delete($taskId);
            
            ResponseHelper::success([
                'message' => 'Task deleted successfully'
            ]);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Failed to delete task', 500);
        }
    }
    
    private function validateTaskInput(?array $input): bool 
    {
        if (!$input || !isset($input['title']) || empty(trim($input['title']))) {
            return false;
        }
        
        $validPriorities = ['low', 'medium', 'high', 'critical'];
        if (isset($input['priority']) && !in_array($input['priority'], $validPriorities)) {
            return false;
        }
        
        return true;
    }
}
?>