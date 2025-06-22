<?php

namespace App\Controllers;

use App\Models\User;
use App\Utils\JwtHelper;
use App\Utils\ResponseHelper;

class AuthController 
{
    private User $userModel;
    
    public function __construct() 
    {
        $this->userModel = new User();
    }
    
    public function register(): void 
    {
        try {
            $input = json_decode(file_get_contents('php://input'), true);
            
            // Validate input
            if (!$this->validateRegisterInput($input)) {
                ResponseHelper::error('Invalid input data', 400);
                return;
            }
            
            // Check if user exists
            if ($this->userModel->findByEmail($input['email'])) {
                ResponseHelper::error('User already exists with this email', 409);
                return;
            }
            
            // Create user
            $userData = [
                'name' => trim($input['name']),
                'email' => strtolower(trim($input['email'])),
                'password' => password_hash($input['password'], PASSWORD_DEFAULT),
                'created_at' => date('Y-m-d H:i:s'),
                'is_active' => 1
            ];
            
            $userId = $this->userModel->create($userData);
            $user = $this->userModel->findById($userId);
            
            // Generate JWT token
            $token = JwtHelper::generateToken([
                'user_id' => $user['id'],
                'email' => $user['email']
            ]);
            
            ResponseHelper::success([
                'message' => 'User registered successfully',
                'token' => $token,
                'token_type' => 'Bearer',
                'expires_in' => 24 * 60 * 60, // 24 hours
                'user' => [
                    'id' => $user['id'],
                    'name' => $user['name'],
                    'email' => $user['email'],
                    'created_at' => $user['created_at']
                ]
            ], 201);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Registration failed', 500);
        }
    }
    
    public function login(): void 
    {
        try {
            $input = json_decode(file_get_contents('php://input'), true);
            
            // Validate input
            if (!isset($input['email']) || !isset($input['password'])) {
                ResponseHelper::error('Email and password are required', 400);
                return;
            }
            
            // Find user
            $user = $this->userModel->findByEmail($input['email']);
            
            if (!$user || !password_verify($input['password'], $user['password'])) {
                ResponseHelper::error('Invalid email or password', 401);
                return;
            }
            
            if (!$user['is_active']) {
                ResponseHelper::error('Account is deactivated', 401);
                return;
            }
            
            // Generate JWT token
            $token = JwtHelper::generateToken([
                'user_id' => $user['id'],
                'email' => $user['email']
            ]);
            
            ResponseHelper::success([
                'message' => 'Login successful',
                'token' => $token,
                'token_type' => 'Bearer',
                'expires_in' => 24 * 60 * 60, // 24 hours
                'user' => [
                    'id' => $user['id'],
                    'name' => $user['name'],
                    'email' => $user['email'],
                    'created_at' => $user['created_at']
                ]
            ]);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Login failed', 500);
        }
    }
    
    public function refresh(): void 
    {
        try {
            $authHeader = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
            
            if (!preg_match('/Bearer\s+(.*)$/i', $authHeader, $matches)) {
                ResponseHelper::error('Authorization token required', 401);
                return;
            }
            
            $token = $matches[1];
            $payload = JwtHelper::validateToken($token);
            
            if (!$payload) {
                ResponseHelper::error('Invalid or expired token', 401);
                return;
            }
            
            // Generate new token
            $newToken = JwtHelper::generateToken([
                'user_id' => $payload['user_id'],
                'email' => $payload['email']
            ]);
            
            ResponseHelper::success([
                'token' => $newToken,
                'token_type' => 'Bearer',
                'expires_in' => 24 * 60 * 60
            ]);
            
        } catch (Exception $e) {
            error_log($e->getMessage());
            ResponseHelper::error('Token refresh failed', 500);
        }
    }
    
    private function validateRegisterInput(?array $input): bool 
    {
        if (!$input) return false;
        
        $required = ['name', 'email', 'password'];
        foreach ($required as $field) {
            if (!isset($input[$field]) || empty(trim($input[$field]))) {
                return false;
            }
        }
        
        // Validate email format
        if (!filter_var($input['email'], FILTER_VALIDATE_EMAIL)) {
            return false;
        }
        
        // Validate password length
        if (strlen($input['password']) < 6) {
            return false;
        }
        
        return true;
    }
}
?>