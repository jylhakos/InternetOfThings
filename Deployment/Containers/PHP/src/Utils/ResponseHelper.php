<?php

namespace App\Utils;

class ResponseHelper 
{
    public static function success(array $data, int $statusCode = 200): void 
    {
        http_response_code($statusCode);
        echo json_encode($data);
        exit;
    }
    
    public static function error(string $message, int $statusCode = 400, array $details = []): void 
    {
        http_response_code($statusCode);
        
        $response = [
            'error' => true,
            'message' => $message,
            'timestamp' => date('c')
        ];
        
        if (!empty($details)) {
            $response['details'] = $details;
        }
        
        echo json_encode($response);
        exit;
    }
    
    public static function notFound(string $message = 'Resource not found'): void 
    {
        self::error($message, 404);
    }
    
    public static function unauthorized(string $message = 'Unauthorized'): void 
    {
        self::error($message, 401);
    }
    
    public static function forbidden(string $message = 'Forbidden'): void 
    {
        self::error($message, 403);
    }
    
    public static function validationError(array $errors): void 
    {
        self::error('Validation failed', 422, $errors);
    }
}
?>