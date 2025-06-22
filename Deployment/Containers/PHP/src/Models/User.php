<?php

namespace App\Models;

use PDO;

class User 
{
    private PDO $db;
    
    public function __construct() 
    {
        global $pdo;
        $this->db = $pdo;
    }
    
    public function create(array $data): int 
    {
        $sql = "INSERT INTO users (name, email, password, created_at, is_active) 
                VALUES (:name, :email, :password, :created_at, :is_active)";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($data);
        
        return (int) $this->db->lastInsertId();
    }
    
    public function findById(int $id): ?array 
    {
        $sql = "SELECT id, name, email, created_at, is_active FROM users WHERE id = :id";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute(['id' => $id]);
        
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        return $user ?: null;
    }
    
    public function findByEmail(string $email): ?array 
    {
        $sql = "SELECT * FROM users WHERE email = :email";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute(['email' => strtolower($email)]);
        
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        return $user ?: null;
    }
    
    public function update(int $id, array $data): bool 
    {
        $data['updated_at'] = date('Y-m-d H:i:s');
        
        $fields = [];
        foreach ($data as $key => $value) {
            $fields[] = "$key = :$key";
        }
        
        $sql = "UPDATE users SET " . implode(', ', $fields) . " WHERE id = :id";
        $data['id'] = $id;
        
        $stmt = $this->db->prepare($sql);
        return $stmt->execute($data);
    }
    
    public function delete(int $id): bool 
    {
        $sql = "DELETE FROM users WHERE id = :id";
        
        $stmt = $this->db->prepare($sql);
        return $stmt->execute(['id' => $id]);
    }
}
?>