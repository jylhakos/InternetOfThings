import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { quotesApi } from '@/lib/api';
import { ComponentLoader } from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

export default function Quotes() {
  const [quotes, setQuotes] = useState([]);
  const [stats, setStats] = useState(null);
  const [randomQuote, setRandomQuote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    kind: '',
    sortBy: 'createdAt',
    sortOrder: 'desc'
  });
  const [pagination, setPagination] = useState({
    limit: 20,
    offset: 0,
    total: 0,
    hasMore: false
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadQuotes();
  }, [filters]);

  const loadInitialData = async () => {
    try {
      const [quotesRes, statsRes, randomRes] = await Promise.all([
        quotesApi.getAll({ limit: 20, offset: 0 }),
        quotesApi.getStats(),
        quotesApi.getRandom()
      ]);

      setQuotes(quotesRes.data);
      setPagination({
        limit: 20,
        offset: 0,
        total: quotesRes.pagination.total,
        hasMore: quotesRes.pagination.hasMore
      });
      setStats(statsRes.data);
      setRandomQuote(randomRes.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const loadQuotes = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        ...filters,
        limit: pagination.limit,
        offset: pagination.offset
      };

      const response = await quotesApi.getAll(params);
      setQuotes(response.data);
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

      const response = await quotesApi.getAll(params);
      setQuotes(prev => [...prev, ...response.data]);
      setPagination(prev => ({
        ...prev,
        offset: newOffset,
        hasMore: response.pagination.hasMore
      }));
    } catch (err) {
      setError(err);
    }
  };

  const getRandomQuote = async () => {
    try {
      const response = await quotesApi.getRandom();
      setRandomQuote(response.data);
    } catch (err) {
      console.error('Failed to get random quote:', err);
    }
  };

  const resetFilters = () => {
    setFilters({
      search: '',
      category: '',
      kind: '',
      sortBy: 'createdAt',
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
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Inspiring Quotes</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover wisdom, motivation, and inspiration from great minds throughout history
          </p>
        </div>

        {/* Random Quote Section */}
        {randomQuote && (
          <div className="bg-gradient-to-r from-blue-600 to-purple-700 rounded-lg p-8 mb-12 text-center">
            <blockquote className="text-2xl md:text-3xl font-medium text-white italic mb-6">
              "{randomQuote.text}"
            </blockquote>
            <p className="text-xl text-blue-100 mb-6">
              — {randomQuote.author}
            </p>
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              {randomQuote.tags?.map((tag, index) => (
                <span
                  key={index}
                  className="bg-white bg-opacity-20 text-white px-3 py-1 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
            <button
              onClick={getRandomQuote}
              className="bg-white text-blue-600 px-6 py-2 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              Get Another Quote
            </button>
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{stats.totalQuotes}</div>
              <div className="text-gray-600">Total Quotes</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">{stats.totalAuthors}</div>
              <div className="text-gray-600">Authors</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">{stats.totalCategories}</div>
              <div className="text-gray-600">Categories</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <div className="text-3xl font-bold text-red-600 mb-2">{stats.totalKinds}</div>
              <div className="text-gray-600">Kinds</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
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
                placeholder="Search quotes..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Category */}
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                id="category"
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Categories</option>
                <option value="motivational">Motivational</option>
                <option value="wisdom">Wisdom</option>
                <option value="life">Life</option>
                <option value="success">Success</option>
                <option value="love">Love</option>
                <option value="philosophy">Philosophy</option>
              </select>
            </div>

            {/* Kind */}
            <div>
              <label htmlFor="kind" className="block text-sm font-medium text-gray-700 mb-2">
                Kind
              </label>
              <select
                id="kind"
                value={filters.kind}
                onChange={(e) => handleFilterChange('kind', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Kinds</option>
                <option value="famous">Famous</option>
                <option value="inspirational">Inspirational</option>
                <option value="funny">Funny</option>
                <option value="thought-provoking">Thought-provoking</option>
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
                <option value="createdAt-desc">Newest First</option>
                <option value="createdAt-asc">Oldest First</option>
                <option value="author-asc">Author A-Z</option>
                <option value="author-desc">Author Z-A</option>
              </select>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              {pagination.total} quotes found
            </div>
            <button
              onClick={resetFilters}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Reset Filters
            </button>
          </div>
        </div>

        {/* Quotes List */}
        {loading ? (
          <ComponentLoader message="Loading quotes..." />
        ) : error ? (
          <ErrorMessage error={error} onRetry={loadQuotes} />
        ) : (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {quotes.map((quote) => (
                <div
                  key={quote.id}
                  className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
                >
                  <blockquote className="text-lg text-gray-800 mb-4 leading-relaxed">
                    "{quote.text}"
                  </blockquote>
                  
                  <div className="flex items-center justify-between mb-4">
                    <cite className="text-sm font-medium text-gray-600">
                      — {quote.author}
                    </cite>
                    <div className="flex flex-wrap gap-1">
                      {quote.tags?.slice(0, 2).map((tag, index) => (
                        <span
                          key={index}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                      {quote.tags?.length > 2 && (
                        <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                          +{quote.tags.length - 2}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div>
                      {quote.category && (
                        <span className="capitalize">{quote.category}</span>
                      )}
                      {quote.category && quote.kind && <span className="mx-1">•</span>}
                      {quote.kind && (
                        <span className="capitalize">{quote.kind}</span>
                      )}
                    </div>
                    <div>
                      Added {new Date(quote.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Load More */}
            {pagination.hasMore && (
              <div className="text-center">
                <button
                  onClick={handleLoadMore}
                  className="bg-gray-100 text-gray-800 px-8 py-3 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Load More Quotes
                </button>
              </div>
            )}

            {quotes.length === 0 && (
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
                    d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No quotes found</h3>
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
