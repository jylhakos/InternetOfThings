<?php

namespace App\Middleware;

use App\Utils\JwtHelper;
use App\Utils\ResponseHelper;
use App\Models\User;

class AuthMiddleware 
{
    public static function authenticate(): ?array 
    {
        $authHeader = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
        
        if (!preg_match('/Bearer\s+(.*)$/i', $authHeader, $matches)) {
            ResponseHelper::unauthorized('Authorization token required');
            return null;
        }
        
        $token = $matches[1];
        $payload = JwtHelper::validateToken($token);
        
        if (!$payload) {
            ResponseHelper::unauthorized('Invalid or expired token');
            return null;
        }
        
        // Get user from database
        $userModel = new User();
        $user = $userModel->findById($payload['user_id']);
        
        if (!$user || !$user['is_active']) {
            ResponseHelper::unauthorized('User not found or inactive');
            return null;
        }
        
        return $user;
    }
}
?>