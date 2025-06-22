<?php

namespace App\Models;

use PDO;

class Task 
{
    private PDO $db;
    
    public function __construct() 
    {
        global $pdo;
        $this->db = $pdo;
    }
    
    public function create(array $data): int 
    {
        $sql = "INSERT INTO tasks (title, description, priority, due_date, user_id, completed, created_at, updated_at) 
                VALUES (:title, :description, :priority, :due_date, :user_id, :completed, :created_at, :updated_at)";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($data);
        
        return (int) $this->db->lastInsertId();
    }
    
    public function findById(int $id): ?array 
    {
        $sql = "SELECT * FROM tasks WHERE id = :id";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute(['id' => $id]);
        
        $task = $stmt->fetch(PDO::FETCH_ASSOC);
        return $task ?: null;
    }
    
    public function findByIdAndUser(int $id, int $userId): ?array 
    {
        $sql = "SELECT * FROM tasks WHERE id = :id AND user_id = :user_id";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute(['id' => $id, 'user_id' => $userId]);
        
        $task = $stmt->fetch(PDO::FETCH_ASSOC);
        return $task ?: null;
    }
    
    public function findByUser(int $userId, array $filters = []): array 
    {
        $sql = "SELECT * FROM tasks WHERE user_id = :user_id";
        $params = ['user_id' => $userId];
        
        if (isset($filters['completed']) && $filters['completed'] !== null) {
            $sql .= " AND completed = :completed";
            $params['completed'] = $filters['completed'] === 'true' ? 1 : 0;
        }
        
        if (isset($filters['priority']) && !empty($filters['priority'])) {
            $sql .= " AND priority = :priority";
            $params['priority'] = $filters['priority'];
        }
        
        if (isset($filters['search']) && !empty($filters['search'])) {
            $sql .= " AND (title LIKE :search OR description LIKE :search)";
            $params['search'] = '%' . $filters['search'] . '%';
        }
        
        $sql .= " ORDER BY created_at DESC";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    public function update(int $id, array $data): bool 
    {
        $fields = [];
        foreach ($data as $key => $value) {
            $fields[] = "$key = :$key";
        }
        
        $sql = "UPDATE tasks SET " . implode(', ', $fields) . " WHERE id = :id";
        $data['id'] = $id;
        
        $stmt = $this->db->prepare($sql);
        return $stmt->execute($data);
    }
    
    public function delete(int $id): bool 
    {
        $sql = "DELETE FROM tasks WHERE id = :id";
        
        $stmt = $this->db->prepare($sql);
        return $stmt->execute(['id' => $id]);
    }
}
?>