import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { postsApi } from '@/lib/api';
import { ComponentLoader } from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import Link from 'next/link';

export default function Blog() {
  const [posts, setPosts] = useState([]);
  const [featuredPosts, setFeaturedPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    tag: '',
    sortBy: 'publishedAt',
    sortOrder: 'desc'
  });
  const [pagination, setPagination] = useState({
    limit: 12,
    offset: 0,
    total: 0,
    hasMore: false
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadPosts();
  }, [filters]);

  const loadInitialData = async () => {
    try {
      const [postsRes, featuredRes] = await Promise.all([
        postsApi.getAll({ limit: 12, offset: 0 }),
        postsApi.getFeatured({ limit: 3 })
      ]);

      setPosts(postsRes.data);
      setPagination({
        limit: 12,
        offset: 0,
        total: postsRes.pagination.total,
        hasMore: postsRes.pagination.hasMore
      });
      setFeaturedPosts(featuredRes.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const loadPosts = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        ...filters,
        limit: pagination.limit,
        offset: pagination.offset
      };

      const response = await postsApi.getAll(params);
      setPosts(response.data);
      setPagination(prev => ({
        ...prev,
        total: response.pagination.total,
        hasMore: response.pagination.hasMore
      }));
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setPagination(prev => ({
      ...prev,
      offset: 0
    }));
  };

  const handleLoadMore = async () => {
    const newOffset = pagination.offset + pagination.limit;
    
    try {
      const params = {
        ...filters,
        limit: pagination.limit,
        offset: newOffset
      };

      const response = await postsApi.getAll(params);
      setPosts(prev => [...prev, ...response.data]);
      setPagination(prev => ({
        ...prev,
        offset: newOffset,
        hasMore: response.pagination.hasMore
      }));
    } catch (err) {
      setError(err);
    }
  };

  const resetFilters = () => {
    setFilters({
      search: '',
      tag: '',
      sortBy: 'publishedAt',
      sortOrder: 'desc'
    });
    setPagination(prev => ({
      ...prev,
      offset: 0
    }));
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Our Blog</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Stay updated with the latest insights, tutorials, and industry news
          </p>
        </div>

        {/* Featured Posts */}
        {featuredPosts.length > 0 && (
          <div className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Featured Posts</h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {featuredPosts.map((post, index) => (
                <article
                  key={post.id}
                  className={`${
                    index === 0 ? 'lg:col-span-2 lg:row-span-2' : ''
                  } bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow`}
                >
                  <div className={`${index === 0 ? 'aspect-w-16 aspect-h-9' : 'aspect-w-16 aspect-h-9'} bg-gray-200`}>
                    {post.featuredImage ? (
                      <img
                        src={post.featuredImage}
                        alt={post.title}
                        className={`w-full object-cover ${index === 0 ? 'h-64 lg:h-96' : 'h-48'}`}
                      />
                    ) : (
                      <div className={`w-full bg-gray-200 flex items-center justify-center ${index === 0 ? 'h-64 lg:h-96' : 'h-48'}`}>
                        <svg className="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <div className="p-6">
                    <div className="flex items-center text-sm text-gray-500 mb-3">
                      <time dateTime={post.publishedAt}>
                        {new Date(post.publishedAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </time>
                      <span className="mx-2">•</span>
                      <span>{post.author?.name || 'Anonymous'}</span>
                      <span className="mx-2">•</span>
                      <span>{post.readTime || '5'} min read</span>
                    </div>
                    <h3 className={`font-bold text-gray-900 mb-3 ${index === 0 ? 'text-2xl lg:text-3xl' : 'text-xl'}`}>
                      {post.title}
                    </h3>
                    <p className={`text-gray-600 mb-4 ${index === 0 ? 'text-lg line-clamp-3' : 'line-clamp-2'}`}>
                      {post.excerpt}
                    </p>
                    <div className="flex items-center justify-between">
                      <Link
                        href={`/blog/${post.slug}`}
                        className="text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Read more →
                      </Link>
                      <div className="flex items-center text-sm text-gray-500">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                        </svg>
                        {post.likes || 0}
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* Search */}
            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                type="text"
                id="search"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Search posts..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Tag */}
            <div>
              <label htmlFor="tag" className="block text-sm font-medium text-gray-700 mb-2">
                Tag
              </label>
              <select
                id="tag"
                value={filters.tag}
                onChange={(e) => handleFilterChange('tag', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Tags</option>
                <option value="technology">Technology</option>
                <option value="tutorial">Tutorial</option>
                <option value="news">News</option>
                <option value="tips">Tips</option>
                <option value="review">Review</option>
              </select>
            </div>

            {/* Sort */}
            <div>
              <label htmlFor="sort" className="block text-sm font-medium text-gray-700 mb-2">
                Sort By
              </label>
              <select
                id="sort"
                value={`${filters.sortBy}-${filters.sortOrder}`}
                onChange={(e) => {
                  const [sortBy, sortOrder] = e.target.value.split('-');
                  handleFilterChange('sortBy', sortBy);
                  handleFilterChange('sortOrder', sortOrder);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="publishedAt-desc">Latest First</option>
                <option value="publishedAt-asc">Oldest First</option>
                <option value="title-asc">Title A-Z</option>
                <option value="title-desc">Title Z-A</option>
                <option value="likes-desc">Most Popular</option>
              </select>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              {pagination.total} posts found
            </div>
            <button
              onClick={resetFilters}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Reset Filters
            </button>
          </div>
        </div>

        {/* Posts Grid */}
        {loading ? (
          <ComponentLoader message="Loading posts..." />
        ) : error ? (
          <ErrorMessage error={error} onRetry={loadPosts} />
        ) : (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {posts.map((post) => (
                <article
                  key={post.id}
                  className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
                >
                  <div className="aspect-w-16 aspect-h-9 bg-gray-200">
                    {post.featuredImage ? (
                      <img
                        src={post.featuredImage}
                        alt={post.title}
                        className="w-full h-48 object-cover"
                      />
                    ) : (
                      <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                        <svg className="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <div className="p-6">
                    <div className="flex items-center text-sm text-gray-500 mb-3">
                      <time dateTime={post.publishedAt}>
                        {new Date(post.publishedAt).toLocaleDateString()}
                      </time>
                      <span className="mx-2">•</span>
                      <span>{post.author?.name || 'Anonymous'}</span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3 line-clamp-2">
                      {post.title}
                    </h3>
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {post.excerpt}
                    </p>
                    <div className="flex items-center justify-between">
                      <Link
                        href={`/blog/${post.slug}`}
                        className="text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Read more →
                      </Link>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                          </svg>
                          {post.likes || 0}
                        </div>
                        <div className="flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                          </svg>
                          {post.comments || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {/* Load More */}
            {pagination.hasMore && (
              <div className="text-center">
                <button
                  onClick={handleLoadMore}
                  className="bg-gray-100 text-gray-800 px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Load More Posts
                </button>
              </div>
            )}

            {posts.length === 0 && (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No posts found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your filters to see more results.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
