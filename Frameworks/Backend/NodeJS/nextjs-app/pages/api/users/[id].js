// Next.js dynamic API route
// Demonstrates parameterized routes and detailed error handling

const users = [
  { id: 1, name: 'Alice Johnson', email: 'alice@example.com', role: 'admin' },
  { id: 2, name: 'Bob Smith', email: 'bob@example.com', role: 'user' },
  { id: 3, name: 'Charlie Brown', email: 'charlie@example.com', role: 'user' },
];

export default function handler(req, res) {
  const { id } = req.query;
  
  // Validate ID parameter
  if (!id || isNaN(parseInt(id))) {
    return res.status(400).json({
      error: 'Invalid user ID parameter'
    });
  }
  
  const userId = parseInt(id);
  
  switch (req.method) {
    case 'GET':
      // Get user by ID
      const user = users.find(u => u.id === userId);
      
      if (!user) {
        return res.status(404).json({
          error: 'User not found'
        });
      }
      
      res.status(200).json({
        user,
        timestamp: new Date().toISOString()
      });
      break;

    case 'PUT':
      // Update user by ID
      const userIndex = users.findIndex(u => u.id === userId);
      
      if (userIndex === -1) {
        return res.status(404).json({
          error: 'User not found'
        });
      }
      
      const { name, email, role } = req.body;
      
      // Validate required fields
      if (!name || !email) {
        return res.status(400).json({
          error: 'Name and email are required'
        });
      }
      
      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return res.status(400).json({
          error: 'Invalid email format'
        });
      }
      
      // Update user
      users[userIndex] = {
        ...users[userIndex],
        name,
        email,
        role: role || users[userIndex].role
      };
      
      res.status(200).json({
        message: 'User updated successfully',
        user: users[userIndex]
      });
      break;

    case 'DELETE':
      // Delete user by ID
      const deleteIndex = users.findIndex(u => u.id === userId);
      
      if (deleteIndex === -1) {
        return res.status(404).json({
          error: 'User not found'
        });
      }
      
      const deletedUser = users.splice(deleteIndex, 1)[0];
      
      res.status(200).json({
        message: 'User deleted successfully',
        user: deletedUser
      });
      break;

    default:
      res.setHeader('Allow', ['GET', 'PUT', 'DELETE']);
      res.status(405).json({
        error: `Method ${req.method} not allowed`
      });
  }
}
