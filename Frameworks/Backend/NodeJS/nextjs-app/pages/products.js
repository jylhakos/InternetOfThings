import { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import ProductCard from '../components/ProductCard';

export default function Products({ initialProducts }) {
  const [products, setProducts] = useState(initialProducts);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const categories = ['all', 'electronics', 'clothing', 'books', 'home'];

  // Filter products based on category and search
  const filteredProducts = products.filter(product => {
    const matchesCategory = filter === 'all' || product.category === filter;
    const matchesSearch = product.name.toLowerCase().includes(search.toLowerCase()) ||
                         product.description.toLowerCase().includes(search.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Handle client-side filtering
  const handleFilterChange = async (newFilter) => {
    setFilter(newFilter);
    setLoading(true);
    
    // Simulate API call for filtered data
    setTimeout(() => {
      setLoading(false);
    }, 500);
  };

  return (
    <Layout>
      <Head>
        <title>Products - Next.js App</title>
        <meta name="description" content="Browse our product catalog with server-side rendering" />
      </Head>

      <div className="container">
        <h1>Product Catalog</h1>
        <p>Server-side rendered products with client-side filtering</p>

        {/* Search and Filter Controls */}
        <div className="controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-tabs">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => handleFilterChange(category)}
                className={`filter-tab ${filter === category ? 'active' : ''}`}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="loading">Loading products...</div>
        ) : (
          <div className="products-grid">
            {filteredProducts.length > 0 ? (
              filteredProducts.map(product => (
                <ProductCard key={product.id} product={product} />
              ))
            ) : (
              <div className="no-products">
                No products found matching your criteria.
              </div>
            )}
          </div>
        )}

        {/* Product Stats */}
        <div className="stats">
          <p>Showing {filteredProducts.length} of {products.length} products</p>
          <p>Data fetched at build time: {new Date().toLocaleString()}</p>
        </div>
      </div>

      <style jsx>{`
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        h1 {
          color: #333;
          margin-bottom: 0.5rem;
        }

        .controls {
          margin: 2rem 0;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .search-input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 1rem;
        }

        .filter-tabs {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .filter-tab {
          padding: 0.5rem 1rem;
          border: 1px solid #ddd;
          background: white;
          border-radius: 20px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .filter-tab:hover {
          background: #f0f0f0;
        }

        .filter-tab.active {
          background: #0070f3;
          color: white;
          border-color: #0070f3;
        }

        .products-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 2rem;
          margin: 2rem 0;
        }

        .loading {
          text-align: center;
          padding: 3rem;
          font-size: 1.2rem;
          color: #666;
        }

        .no-products {
          grid-column: 1 / -1;
          text-align: center;
          padding: 3rem;
          color: #666;
          border: 1px dashed #ddd;
          border-radius: 8px;
        }

        .stats {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid #eee;
          color: #666;
          font-size: 0.9rem;
        }

        @media (min-width: 768px) {
          .controls {
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
          }

          .search-box {
            flex: 1;
            max-width: 300px;
          }
        }
      `}</style>
    </Layout>
  );
}

// Server-side rendering
export async function getServerSideProps() {
  // Simulate fetching products from an API
  const products = [
    {
      id: 1,
      name: 'Smartphone Pro',
      description: 'Latest flagship smartphone with advanced features',
      price: 999.99,
      category: 'electronics',
      image: '/images/smartphone.jpg',
      inStock: true
    },
    {
      id: 2,
      name: 'Wireless Headphones',
      description: 'Premium noise-cancelling wireless headphones',
      price: 299.99,
      category: 'electronics',
      image: '/images/headphones.jpg',
      inStock: true
    },
    {
      id: 3,
      name: 'Cotton T-Shirt',
      description: 'Comfortable 100% cotton t-shirt',
      price: 29.99,
      category: 'clothing',
      image: '/images/tshirt.jpg',
      inStock: true
    },
    {
      id: 4,
      name: 'JavaScript Guide',
      description: 'Comprehensive guide to modern JavaScript',
      price: 49.99,
      category: 'books',
      image: '/images/book.jpg',
      inStock: true
    },
    {
      id: 5,
      name: 'Coffee Maker',
      description: 'Automatic drip coffee maker with timer',
      price: 89.99,
      category: 'home',
      image: '/images/coffee-maker.jpg',
      inStock: false
    }
  ];

  return {
    props: {
      initialProducts: products
    }
  };
}
