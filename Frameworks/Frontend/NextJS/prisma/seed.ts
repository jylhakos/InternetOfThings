import { PrismaClient } from '../lib/generated/prisma/index.js';
import { QuoteKind, UserRole, PostStatus, ProductStatus, OrderStatus, PaymentStatus } from '../lib/generated/prisma/index.js';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Clean existing data (in development)
  if (process.env.NODE_ENV !== 'production') {
    await prisma.analytics.deleteMany();
    await prisma.review.deleteMany();
    await prisma.orderItem.deleteMany();
    await prisma.order.deleteMany();
    await prisma.product.deleteMany();
    await prisma.category.deleteMany();
    await prisma.like.deleteMany();
    await prisma.comment.deleteMany();
    await prisma.post.deleteMany();
    await prisma.profile.deleteMany();
    await prisma.user.deleteMany();
    await prisma.quote.deleteMany();
    await prisma.tag.deleteMany();
  }

  // Seed Users
  const users = await Promise.all([
    prisma.user.create({
      data: {
        id: 'user1',
        email: 'john.doe@example.com',
        name: 'John Doe',
        role: UserRole.ADMIN,
        profiles: {
          create: {
            bio: 'Full-stack developer passionate about modern web technologies',
            website: 'https://johndoe.dev',
            location: 'San Francisco, CA',
            company: 'Tech Corp',
            skills: ['TypeScript', 'React', 'Node.js', 'PostgreSQL'],
            socialLinks: {
              github: 'https://github.com/johndoe',
              twitter: 'https://twitter.com/johndoe',
              linkedin: 'https://linkedin.com/in/johndoe'
            }
          }
        }
      }
    }),
    prisma.user.create({
      data: {
        id: 'user2',
        email: 'jane.smith@example.com',
        name: 'Jane Smith',
        role: UserRole.USER,
        profiles: {
          create: {
            bio: 'UI/UX Designer with a love for clean, user-centered design',
            website: 'https://janesmith.design',
            location: 'New York, NY',
            company: 'Design Studio',
            skills: ['Figma', 'Adobe Creative Suite', 'Prototyping', 'User Research']
          }
        }
      }
    }),
    prisma.user.create({
      data: {
        id: 'user3',
        email: 'mike.johnson@example.com',
        name: 'Mike Johnson',
        role: UserRole.USER,
        profiles: {
          create: {
            bio: 'DevOps engineer focused on cloud infrastructure and automation',
            location: 'Austin, TX',
            company: 'Cloud Solutions Inc',
            skills: ['AWS', 'Docker', 'Kubernetes', 'Terraform']
          }
        }
      }
    })
  ]);

  console.log('✅ Created users:', users.length);

  // Seed Tags
  const tags = await Promise.all([
    prisma.tag.create({
      data: {
        name: 'Technology',
        slug: 'technology',
        description: 'Posts about latest technology trends and insights',
        color: '#3B82F6'
      }
    }),
    prisma.tag.create({
      data: {
        name: 'Web Development',
        slug: 'web-development',
        description: 'Frontend and backend web development topics',
        color: '#10B981'
      }
    }),
    prisma.tag.create({
      data: {
        name: 'Design',
        slug: 'design',
        description: 'UI/UX design and creative topics',
        color: '#F59E0B'
      }
    }),
    prisma.tag.create({
      data: {
        name: 'DevOps',
        slug: 'devops',
        description: 'DevOps, CI/CD, and infrastructure topics',
        color: '#EF4444'
      }
    })
  ]);

  console.log('✅ Created tags:', tags.length);

  // Seed Posts
  const posts = await Promise.all([
    prisma.post.create({
      data: {
        title: 'Getting Started with Next.js 15 and Prisma',
        slug: 'getting-started-nextjs-15-prisma',
        content: `# Getting Started with Next.js 15 and Prisma

Next.js 15 brings exciting new features and improvements that make building full-stack React applications even more enjoyable. When combined with Prisma as your ORM, you get a powerful, type-safe development experience.

## Key Features

- **App Router**: The new app directory structure provides better organization
- **Server Components**: Improved performance with server-side rendering
- **Type Safety**: End-to-end type safety with Prisma and TypeScript

## Setting Up Your Project

1. Initialize your Next.js project
2. Install and configure Prisma
3. Set up your database schema
4. Generate your Prisma client

This combination provides an excellent developer experience for building modern web applications.`,
        excerpt: 'Learn how to combine Next.js 15 with Prisma for a powerful full-stack development experience.',
        published: true,
        featured: true,
        status: PostStatus.PUBLISHED,
        publishedAt: new Date('2024-01-15'),
        authorId: 'user1',
        tags: {
          connect: [
            { id: tags[0].id }, // Technology
            { id: tags[1].id }  // Web Development
          ]
        }
      }
    }),
    prisma.post.create({
      data: {
        title: 'Modern UI/UX Design Principles',
        slug: 'modern-ui-ux-design-principles',
        content: `# Modern UI/UX Design Principles

Creating exceptional user experiences requires understanding both design principles and user psychology. Here are key principles every designer should know.

## Core Principles

1. **Clarity**: Make your interface clear and understandable
2. **Consistency**: Maintain consistent patterns throughout
3. **Feedback**: Provide clear feedback for user actions
4. **Accessibility**: Design for all users

## Design Systems

Modern design systems help maintain consistency and speed up development. Tools like Figma make collaboration between designers and developers seamless.

Remember: good design is invisible to the user but makes their experience delightful.`,
        excerpt: 'Essential design principles for creating modern, user-friendly interfaces.',
        published: true,
        status: PostStatus.PUBLISHED,
        publishedAt: new Date('2024-01-20'),
        authorId: 'user2',
        tags: {
          connect: [
            { id: tags[2].id } // Design
          ]
        }
      }
    }),
    prisma.post.create({
      data: {
        title: 'Docker and Kubernetes Best Practices',
        slug: 'docker-kubernetes-best-practices',
        content: `# Docker and Kubernetes Best Practices

Containerization has revolutionized how we deploy and scale applications. Here are best practices for Docker and Kubernetes.

## Docker Best Practices

- Use multi-stage builds
- Minimize layer count
- Use specific base images
- Don't run as root

## Kubernetes Tips

- Use resource limits
- Implement health checks
- Use namespaces for organization
- Monitor your clusters

These practices will help you build robust, scalable containerized applications.`,
        excerpt: 'Best practices for containerizing and orchestrating your applications.',
        published: true,
        status: PostStatus.PUBLISHED,
        publishedAt: new Date('2024-01-25'),
        authorId: 'user3',
        tags: {
          connect: [
            { id: tags[3].id }, // DevOps
            { id: tags[0].id }  // Technology
          ]
        }
      }
    })
  ]);

  console.log('✅ Created posts:', posts.length);

  // Seed Comments
  const comments = await Promise.all([
    prisma.comment.create({
      data: {
        content: 'Great article! The combination of Next.js and Prisma is indeed powerful.',
        postId: posts[0].id,
        authorId: 'user2'
      }
    }),
    prisma.comment.create({
      data: {
        content: 'Thanks for sharing these insights. Very helpful for beginners.',
        postId: posts[1].id,
        authorId: 'user3'
      }
    }),
    prisma.comment.create({
      data: {
        content: 'Docker multi-stage builds are a game changer for reducing image size.',
        postId: posts[2].id,
        authorId: 'user1'
      }
    })
  ]);

  console.log('✅ Created comments:', comments.length);

  // Seed Quotes
  const quotes = await Promise.all([
    prisma.quote.create({
      data: {
        text: 'The best time to plant a tree was 20 years ago. The second best time is now.',
        author: 'Chinese Proverb',
        category: 'Motivation',
        kind: QuoteKind.INSPIRATIONAL
      }
    }),
    prisma.quote.create({
      data: {
        text: 'Code is like humor. When you have to explain it, it\'s bad.',
        author: 'Cory House',
        category: 'Programming',
        kind: QuoteKind.HUMOROUS
      }
    }),
    prisma.quote.create({
      data: {
        text: 'The only way to do great work is to love what you do.',
        author: 'Steve Jobs',
        category: 'Career',
        kind: QuoteKind.MOTIVATIONAL
      }
    }),
    prisma.quote.create({
      data: {
        text: 'First, solve the problem. Then, write the code.',
        author: 'John Johnson',
        category: 'Programming',
        kind: QuoteKind.WISDOM
      }
    }),
    prisma.quote.create({
      data: {
        text: 'Simplicity is the ultimate sophistication.',
        author: 'Leonardo da Vinci',
        category: 'Design',
        kind: QuoteKind.PHILOSOPHICAL
      }
    })
  ]);

  console.log('✅ Created quotes:', quotes.length);

  // Seed Categories
  const categories = await Promise.all([
    prisma.category.create({
      data: {
        name: 'Electronics',
        slug: 'electronics',
        description: 'Latest electronic gadgets and devices'
      }
    }),
    prisma.category.create({
      data: {
        name: 'Books',
        slug: 'books',
        description: 'Books across various genres and topics'
      }
    }),
    prisma.category.create({
      data: {
        name: 'Clothing',
        slug: 'clothing',
        description: 'Fashion and clothing items'
      }
    })
  ]);

  console.log('✅ Created categories:', categories.length);

  // Seed Products
  const products = await Promise.all([
    prisma.product.create({
      data: {
        name: 'Wireless Bluetooth Headphones',
        slug: 'wireless-bluetooth-headphones',
        description: 'High-quality wireless headphones with noise cancellation',
        price: 99.99,
        comparePrice: 129.99,
        sku: 'WBH-001',
        quantity: 50,
        status: ProductStatus.ACTIVE,
        images: ['/images/headphones-1.jpg', '/images/headphones-2.jpg'],
        tags: ['wireless', 'bluetooth', 'audio'],
        categoryId: categories[0].id
      }
    }),
    prisma.product.create({
      data: {
        name: 'JavaScript: The Definitive Guide',
        slug: 'javascript-definitive-guide',
        description: 'Comprehensive guide to JavaScript programming',
        price: 39.99,
        comparePrice: 49.99,
        sku: 'BOOK-001',
        quantity: 25,
        status: ProductStatus.ACTIVE,
        images: ['/images/js-book.jpg'],
        tags: ['programming', 'javascript', 'education'],
        categoryId: categories[1].id
      }
    }),
    prisma.product.create({
      data: {
        name: 'Premium Cotton T-Shirt',
        slug: 'premium-cotton-tshirt',
        description: 'Comfortable premium cotton t-shirt available in multiple colors',
        price: 24.99,
        sku: 'SHIRT-001',
        quantity: 100,
        status: ProductStatus.ACTIVE,
        images: ['/images/tshirt-1.jpg', '/images/tshirt-2.jpg'],
        tags: ['clothing', 'cotton', 'casual'],
        categoryId: categories[2].id
      }
    })
  ]);

  console.log('✅ Created products:', products.length);

  // Seed Reviews
  const reviews = await Promise.all([
    prisma.review.create({
      data: {
        rating: 5,
        title: 'Excellent sound quality!',
        comment: 'These headphones exceeded my expectations. Great bass and crystal clear highs.',
        verified: true,
        helpful: 12,
        productId: products[0].id,
        reviewerName: 'Alex Thompson',
        reviewerEmail: 'alex@example.com'
      }
    }),
    prisma.review.create({
      data: {
        rating: 4,
        title: 'Comprehensive and well-written',
        comment: 'Perfect for learning JavaScript. Covers everything from basics to advanced topics.',
        verified: true,
        helpful: 8,
        productId: products[1].id,
        reviewerName: 'Sarah Wilson',
        reviewerEmail: 'sarah@example.com'
      }
    }),
    prisma.review.create({
      data: {
        rating: 5,
        title: 'Super comfortable!',
        comment: 'Love the fit and feel of this t-shirt. Will definitely buy more colors.',
        verified: true,
        helpful: 5,
        productId: products[2].id,
        reviewerName: 'David Lee',
        reviewerEmail: 'david@example.com'
      }
    })
  ]);

  console.log('✅ Created reviews:', reviews.length);

  // Add some likes to posts
  const likes = await Promise.all([
    prisma.like.create({
      data: {
        postId: posts[0].id,
        userId: 'user2'
      }
    }),
    prisma.like.create({
      data: {
        postId: posts[0].id,
        userId: 'user3'
      }
    }),
    prisma.like.create({
      data: {
        postId: posts[1].id,
        userId: 'user1'
      }
    })
  ]);

  console.log('✅ Created likes:', likes.length);

  // Sample analytics data
  const analytics = await Promise.all([
    prisma.analytics.create({
      data: {
        event: 'page_view',
        path: '/',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ip: '192.168.1.100',
        country: 'US',
        city: 'New York',
        device: 'Desktop',
        browser: 'Chrome',
        os: 'Windows'
      }
    }),
    prisma.analytics.create({
      data: {
        event: 'post_view',
        path: '/posts/getting-started-nextjs-15-prisma',
        data: {
          postId: posts[0].id,
          timeSpent: 120
        }
      }
    })
  ]);

  console.log('✅ Created analytics entries:', analytics.length);

  // Update post view counts
  await prisma.post.update({
    where: { id: posts[0].id },
    data: { viewCount: 45 }
  });

  await prisma.post.update({
    where: { id: posts[1].id },
    data: { viewCount: 32 }
  });

  await prisma.post.update({
    where: { id: posts[2].id },
    data: { viewCount: 28 }
  });

  console.log('✅ Updated post view counts');

  const stats = {
    users: await prisma.user.count(),
    profiles: await prisma.profile.count(),
    posts: await prisma.post.count(),
    comments: await prisma.comment.count(),
    likes: await prisma.like.count(),
    tags: await prisma.tag.count(),
    quotes: await prisma.quote.count(),
    categories: await prisma.category.count(),
    products: await prisma.product.count(),
    reviews: await prisma.review.count(),
    analytics: await prisma.analytics.count()
  };

  console.log('\n🎉 Seeding completed successfully!');
  console.log('📊 Database statistics:', stats);
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error('❌ Seeding failed:', e);
    await prisma.$disconnect();
    process.exit(1);
  });
