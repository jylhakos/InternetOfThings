<?php

namespace App;

class Router 
{
    private array $routes = [];
    private string $basePath = '';
    
    public function __construct(string $basePath = '') 
    {
        $this->basePath = $basePath;
    }
    
    public function get(string $path, callable $callback): void 
    {
        $this->addRoute('GET', $path, $callback);
    }
    
    public function post(string $path, callable $callback): void 
    {
        $this->addRoute('POST', $path, $callback);
    }
    
    public function put(string $path, callable $callback): void 
    {
        $this->addRoute('PUT', $path, $callback);
    }
    
    public function delete(string $path, callable $callback): void 
    {
        $this->addRoute('DELETE', $path, $callback);
    }
    
    private function addRoute(string $method, string $path, callable $callback): void 
    {
        $this->routes[] = [
            'method' => $method,
            'path' => $this->basePath . $path,
            'callback' => $callback
        ];
    }
    
    public function dispatch(): void 
    {
        $requestMethod = $_SERVER['REQUEST_METHOD'];
        $requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
        
        foreach ($this->routes as $route) {
            if ($route['method'] === $requestMethod) {
                $pattern = $this->convertToRegex($route['path']);
                
                if (preg_match($pattern, $requestUri, $matches)) {
                    array_shift($matches); // Remove full match
                    
                    // Extract named parameters
                    $params = [];
                    if (preg_match_all('/\{(\w+)\}/', $route['path'], $paramNames)) {
                        foreach ($paramNames[1] as $index => $name) {
                            $params[$name] = $matches[$index] ?? null;
                        }
                    }
                    
                    // Set route parameters globally
                    $_GET = array_merge($_GET, $params);
                    
                    call_user_func($route['callback']);
                    return;
                }
            }
        }
        
        // No route found
        http_response_code(404);
        echo json_encode([
            'error' => 'Not Found',
            'message' => 'Endpoint not found: ' . $requestMethod . ' ' . $requestUri
        ]);
    }
    
    private function convertToRegex(string $path): string 
    {
        $pattern = preg_replace('/\{(\w+)\}/', '([^/]+)', $path);
        return '#^' . $pattern . '$#';
    }
}
?>