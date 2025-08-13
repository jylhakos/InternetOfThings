import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '../components/Layout';

export default function Home({ posts }) {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Example of client-side data fetching
    fetch('/api/hello')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => console.error('Failed to fetch message:', err));
  }, []);

  return (
    <Layout>
      <Head>
        <title>Next.js Full-Stack App</title>
        <meta name="description" content="Example Next.js application with SSR and API routes" />
      </Head>

      <div className="container">
        <h1 className="title">Welcome to Next.js Full-Stack App</h1>
        
        <p className="description">
          This example demonstrates Server-Side Rendering (SSR), Static Site Generation (SSG), 
          and API Routes in Next.js.
        </p>

        {message && (
          <div className="message-box">
            <strong>API Message:</strong> {message}
          </div>
        )}

        <div className="grid">
          <Link href="/products" className="card">
            <h2>Products &rarr;</h2>
            <p>Browse products with SSR and client-side filtering.</p>
          </Link>

          <Link href="/blog" className="card">
            <h2>Blog &rarr;</h2>
            <p>Static blog posts generated at build time (SSG).</p>
          </Link>

          <Link href="/dashboard" className="card">
            <h2>Dashboard &rarr;</h2>
            <p>Interactive dashboard with real-time data.</p>
          </Link>

          <a href="/api/hello" className="card" target="_blank" rel="noopener noreferrer">
            <h2>API Routes &rarr;</h2>
            <p>Test the built-in API endpoints.</p>
          </a>
        </div>

        {posts && posts.length > 0 && (
          <section className="recent-posts">
            <h2>Recent Blog Posts</h2>
            <div className="posts-grid">
              {posts.slice(0, 3).map(post => (
                <div key={post.id} className="post-card">
                  <h3>
                    <Link href={`/blog/${post.slug}`}>
                      {post.title}
                    </Link>
                  </h3>
                  <p>{post.excerpt}</p>
                  <small>Published: {new Date(post.date).toLocaleDateString()}</small>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      <style jsx>{`
        .container {
          min-height: 100vh;
          padding: 0 0.5rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          max-width: 1200px;
          margin: 0 auto;
        }

        .title {
          margin: 0;
          line-height: 1.15;
          font-size: 4rem;
          text-align: center;
          color: #0070f3;
        }

        .description {
          text-align: center;
          line-height: 1.5;
          font-size: 1.5rem;
          margin: 2rem 0;
        }

        .message-box {
          background: #f0f8ff;
          border: 1px solid #0070f3;
          border-radius: 8px;
          padding: 1rem;
          margin: 1rem 0;
          color: #0070f3;
        }

        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin: 3rem 0;
          width: 100%;
        }

        .card {
          padding: 1.5rem;
          text-decoration: none;
          color: inherit;
          border: 1px solid #eaeaea;
          border-radius: 10px;
          transition: color 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
        }

        .card:hover {
          color: #0070f3;
          border-color: #0070f3;
          transform: translateY(-2px);
        }

        .card h2 {
          margin: 0 0 1rem 0;
          font-size: 1.5rem;
        }

        .card p {
          margin: 0;
          font-size: 1.25rem;
          line-height: 1.5;
        }

        .recent-posts {
          width: 100%;
          margin: 3rem 0;
        }

        .posts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-top: 2rem;
        }

        .post-card {
          border: 1px solid #eaeaea;
          border-radius: 8px;
          padding: 1.5rem;
          background: #fafafa;
        }

        .post-card h3 {
          margin: 0 0 1rem 0;
        }

        .post-card h3 a {
          color: inherit;
          text-decoration: none;
        }

        .post-card h3 a:hover {
          color: #0070f3;
        }
      `}</style>
    </Layout>
  );
}

// This function runs at build time for SSG
export async function getStaticProps() {
  // Simulate fetching blog posts
  const posts = [
    {
      id: 1,
      title: 'Getting Started with Next.js',
      slug: 'getting-started-nextjs',
      excerpt: 'Learn the basics of Next.js and how to build modern web applications.',
      date: '2023-01-15'
    },
    {
      id: 2,
      title: 'Server-Side Rendering Explained',
      slug: 'ssr-explained',
      excerpt: 'Understanding the benefits and implementation of SSR in Next.js.',
      date: '2023-01-20'
    },
    {
      id: 3,
      title: 'API Routes in Next.js',
      slug: 'api-routes',
      excerpt: 'Building backend functionality with Next.js API routes.',
      date: '2023-01-25'
    }
  ];

  return {
    props: {
      posts
    },
    // Regenerate the page at most once every hour
    revalidate: 3600
  };
}
