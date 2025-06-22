<?php
/**
 * RESTful API Entry Point
 * User:  
 * Date: 2025-06-22 09:49:23 UTC
 */

declare(strict_types=1);

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/../vendor/autoload.php';
require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../src/Router.php';
require_once __DIR__ . '/../src/Controllers/AuthController.php';
require_once __DIR__ . '/../src/Controllers/TaskController.php';
require_once __DIR__ . '/../src/Controllers/UserController.php';
require_once __DIR__ . '/../src/Middleware/AuthMiddleware.php';
require_once __DIR__ . '/../src/Models/User.php';
require_once __DIR__ . '/../src/Models/Task.php';
require_once __DIR__ . '/../src/Utils/JwtHelper.php';
require_once __DIR__ . '/../src/Utils/ResponseHelper.php';

use App\Router;
use App\Controllers\AuthController;
use App\Controllers\TaskController;
use App\Controllers\UserController;

// Error handling
set_error_handler(function($severity, $message, $file, $line) {
    throw new ErrorException($message, 0, $severity, $file, $line);
});

set_exception_handler(function($exception) {
    error_log($exception->getMessage());
    http_response_code(500);
    echo json_encode([
        'error' => 'Internal server error',
        'message' => $_ENV['APP_ENV'] === 'development' ? $exception->getMessage() : 'Something went wrong'
    ]);
});

try {
    // Initialize router
    $router = new Router();
    
    // Initialize controllers
    $authController = new AuthController();
    $taskController = new TaskController();
    $userController = new UserController();
    
    // Health check endpoint
    $router->get('/health', function() {
        echo json_encode([
            'status' => 'healthy',
            'timestamp' => date('c'),
            'user' => ' ',
            'date' => '2025-06-22 09:49:23 UTC',
            'version' => '1.0.0',
            'php_version' => PHP_VERSION,
            'environment' => $_ENV['APP_ENV'] ?? 'production'
        ]);
    });
    
    // Root endpoint
    $router->get('/', function() {
        echo json_encode([
            'message' => 'PHP RESTful API Server',
            'user' => ' ',
            'timestamp' => date('c'),
            'endpoints' => [
                'health' => '/health',
                'auth' => '/api/auth/*',
                'tasks' => '/api/tasks/*',
                'users' => '/api/users/*'
            ]
        ]);
    });
    
    // Authentication routes
    $router->post('/api/auth/register', [$authController, 'register']);
    $router->post('/api/auth/login', [$authController, 'login']);
    $router->post('/api/auth/refresh', [$authController, 'refresh']);
    
    // User routes (protected)
    $router->get('/api/users/me', [$userController, 'getCurrentUser']);
    $router->put('/api/users/me', [$userController, 'updateCurrentUser']);
    
    // Task routes (protected)
    $router->get('/api/tasks', [$taskController, 'getAllTasks']);
    $router->post('/api/tasks', [$taskController, 'createTask']);
    $router->get('/api/tasks/{id}', [$taskController, 'getTask']);
    $router->put('/api/tasks/{id}', [$taskController, 'updateTask']);
    $router->delete('/api/tasks/{id}', [$taskController, 'deleteTask']);
    
    // Process the request
    $router->dispatch();
    
} catch (Exception $e) {
    error_log($e->getMessage());
    http_response_code(500);
    echo json_encode([
        'error' => 'Internal server error',
        'message' => $_ENV['APP_ENV'] === 'development' ? $e->getMessage() : 'Something went wrong'
    ]);
}
?>