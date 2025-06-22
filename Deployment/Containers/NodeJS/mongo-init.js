// MongoDB initialization script
db = db.getSiblingDB('nodeapp');

// Create collections
db.createCollection('users');
db.createCollection('tasks');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.tasks.createIndex({ "userId": 1 });
db.tasks.createIndex({ "createdAt": -1 });

// Insert sample data (optional)
db.users.insertOne({
    name: "Test User",
    email: "test@example.com",
    password: "$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewwrzqNlxN5.i0r6", // password: testpass
    createdAt: new Date()
});

print("MongoDB initialized successfully for Node.js application");