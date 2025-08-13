// Next.js API route for posts
// Demonstrates CRUD operations and data validation

let posts = [
  { id: 1, title: 'First Post', content: 'This is the first post', createdAt: '2024-01-01T00:00:00Z' },
  { id: 2, title: 'Second Post', content: 'This is the second post', createdAt: '2024-01-02T00:00:00Z' },
];

export default function handler(req, res) {
  switch (req.method) {
    case 'GET':
      // Get all posts with optional filtering
      const { limit = 10, offset = 0 } = req.query;
      const limitNum = parseInt(limit);
      const offsetNum = parseInt(offset);
      
      const paginatedPosts = posts.slice(offsetNum, offsetNum + limitNum);
      
      res.status(200).json({
        posts: paginatedPosts,
        total: posts.length,
        limit: limitNum,
        offset: offsetNum,
        hasMore: offsetNum + limitNum < posts.length
      });
      break;

    case 'POST':
      // Create a new post
      const { title, content } = req.body;
      
      if (!title || !content) {
        return res.status(400).json({
          error: 'Title and content are required'
        });
      }
      
      const newPost = {
        id: Math.max(...posts.map(p => p.id), 0) + 1,
        title,
        content,
        createdAt: new Date().toISOString()
      };
      
      posts.push(newPost);
      
      res.status(201).json({
        message: 'Post created successfully',
        post: newPost
      });
      break;

    case 'DELETE':
      // Delete all posts (demo purposes)
      posts = [];
      res.status(200).json({
        message: 'All posts deleted successfully'
      });
      break;

    default:
      res.setHeader('Allow', ['GET', 'POST', 'DELETE']);
      res.status(405).json({
        error: `Method ${req.method} not allowed`
      });
  }
}
