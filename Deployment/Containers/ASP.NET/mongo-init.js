// MongoDB initialization script for Task Management API
// User: 
// Date: 2025-06-22 09:28:27 UTC

db = db.getSiblingDB('TaskManagementDB');

// Create collections
db.createCollection('users');
db.createCollection('tasks');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true, name: "email_unique_index" });
db.users.createIndex({ "isActive": 1 }, { name: "is_active_index" });

db.tasks.createIndex({ "userId": 1 }, { name: "user_id_index" });
db.tasks.createIndex({ "isCompleted": 1 }, { name: "is_completed_index" });
db.tasks.createIndex({ "priority": 1 }, { name: "priority_index" });
db.tasks.createIndex({ "createdAt": -1 }, { name: "created_at_desc_index" });
db.tasks.createIndex({ "dueDate": 1 }, { name: "due_date_index" });
db.tasks.createIndex({ "tags": 1 }, { name: "tags_index" });

// Compound indexes
db.tasks.createIndex({ "userId": 1, "isCompleted": 1 }, { name: "user_completed_compound_index" });
db.tasks.createIndex({ "userId": 1, "priority": 1 }, { name: "user_priority_compound_index" });

// Insert sample user (password: testpassword123)
db.users.insertOne({
    name: "Test User",
    email: "test@example.com",
    passwordHash: "$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewwrzqNlxN5.i0r6",
    createdAt: new Date(),
    isActive: true,
    roles: ["User"]
});

// Insert sample user for 
db.users.insertOne({
    name: "",
    email: "@example.com",
    passwordHash: "$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewwrzqNlxN5.i0r6",
    createdAt: new Date(),
    isActive: true,
    roles: ["User", "Admin"]
});

print("✅ MongoDB initialized successfully for Task Management API");
print("👤 User: ");
print("📅 Date: 2025-06-22 09:28:27 UTC");
print("🗄️ Database: TaskManagementDB");
print("📊 Collections created: users, tasks");
print("📈 Indexes created for optimal performance");
print("👥 Sample users inserted");