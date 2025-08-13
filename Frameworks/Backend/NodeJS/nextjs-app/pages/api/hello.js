// Next.js API route example
// This demonstrates how to create backend functionality within Next.js

export default function handler(req, res) {
  // Handle different HTTP methods
  if (req.method === 'GET') {
    // GET request
    res.status(200).json({
      message: 'Hello from Next.js API Route!',
      timestamp: new Date().toISOString(),
      method: req.method,
      userAgent: req.headers['user-agent'],
      examples: {
        posts: '/api/posts',
        users: '/api/users/[id]',
        upload: '/api/upload'
      }
    });
  } else if (req.method === 'POST') {
    // POST request
    const { name, email } = req.body;
    
    if (!name || !email) {
      return res.status(400).json({
        error: 'Name and email are required'
      });
    }
    
    res.status(201).json({
      message: 'Data received successfully',
      data: { name, email },
      timestamp: new Date().toISOString()
    });
  } else {
    // Method not allowed
    res.setHeader('Allow', ['GET', 'POST']);
    res.status(405).json({
      error: `Method ${req.method} not allowed`
    });
  }
}
