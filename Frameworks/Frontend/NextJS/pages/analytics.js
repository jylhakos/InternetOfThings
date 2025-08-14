import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { analyticsApi } from '@/lib/api';
import { ComponentLoader } from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

export default function Analytics() {
  const [overview, setOverview] = useState(null);
  const [traffic, setTraffic] = useState(null);
  const [pages, setPages] = useState([]);
  const [realtime, setRealtime] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  useEffect(() => {
    // Set up real-time data refresh
    const interval = setInterval(loadRealtimeData, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [overviewRes, trafficRes, pagesRes, realtimeRes] = await Promise.all([
        analyticsApi.getOverview({ period: selectedPeriod }),
        analyticsApi.getTraffic({ period: selectedPeriod }),
        analyticsApi.getPages({ period: selectedPeriod, limit: 10 }),
        analyticsApi.getRealtime()
      ]);

      setOverview(overviewRes.data);
      setTraffic(trafficRes.data);
      setPages(pagesRes.data.pages);
      setRealtime(realtimeRes.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const loadRealtimeData = async () => {
    try {
      const realtimeRes = await analyticsApi.getRealtime();
      setRealtime(realtimeRes.data);
    } catch (err) {
      console.error('Failed to load real-time data:', err);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatPercentage = (num) => {
    return num > 0 ? `+${num.toFixed(1)}%` : `${num.toFixed(1)}%`;
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
              <p className="mt-2 text-gray-600">Track your website performance and user behavior</p>
            </div>
            <div className="mt-4 sm:mt-0">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="1d">Last 24 hours</option>
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <ComponentLoader message="Loading analytics data..." />
        ) : error ? (
          <ErrorMessage error={error} onRetry={loadAnalyticsData} />
        ) : (
          <div className="space-y-8">
            {/* Overview Cards */}
            {overview && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                      <p className="text-3xl font-bold text-gray-900">
                        {formatNumber(overview.overview.totalSessions)}
                      </p>
                    </div>
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className={`text-sm font-medium ${
                      overview.overview.growth.sessions >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(overview.overview.growth.sessions)}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">vs previous period</span>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Unique Users</p>
                      <p className="text-3xl font-bold text-gray-900">
                        {formatNumber(overview.overview.totalUsers)}
                      </p>
                    </div>
                    <div className="p-3 bg-green-100 rounded-lg">
                      <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className={`text-sm font-medium ${
                      overview.overview.growth.users >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(overview.overview.growth.users)}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">vs previous period</span>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Page Views</p>
                      <p className="text-3xl font-bold text-gray-900">
                        {formatNumber(overview.overview.totalPageViews)}
                      </p>
                    </div>
                    <div className="p-3 bg-purple-100 rounded-lg">
                      <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm6 2a1 1 0 100 2h4a1 1 0 100-2h-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className={`text-sm font-medium ${
                      overview.overview.growth.pageViews >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(overview.overview.growth.pageViews)}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">vs previous period</span>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Bounce Rate</p>
                      <p className="text-3xl font-bold text-gray-900">
                        {overview.overview.bounceRate}%
                      </p>
                    </div>
                    <div className="p-3 bg-orange-100 rounded-lg">
                      <svg className="w-6 h-6 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className={`text-sm font-medium ${
                      overview.overview.growth.bounceRate <= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(overview.overview.growth.bounceRate)}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">vs previous period</span>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Real-time Data */}
              {realtime && (
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                      <div className="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                      Real-time Activity
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">Live data from the last 30 minutes</p>
                  </div>
                  <div className="p-6">
                    <div className="mb-6">
                      <div className="text-3xl font-bold text-gray-900 mb-2">
                        {realtime.activeUsers} users online
                      </div>
                      <div className="text-sm text-gray-600">
                        {realtime.currentPageViews} page views in progress
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium text-gray-900">Top Active Pages</h4>
                      {realtime.topActivePages.map((page, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="text-sm text-gray-600">{page.page}</div>
                          <div className="text-sm font-medium text-gray-900">
                            {page.activeUsers} users
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Traffic Sources */}
              {traffic && (
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">Traffic Sources</h3>
                  </div>
                  <div className="p-6">
                    <div className="space-y-4">
                      {traffic.referralSources.map((source, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="text-sm font-medium text-gray-900 capitalize">
                              {source.source}
                            </div>
                          </div>
                          <div className="flex items-center">
                            <div className="text-sm text-gray-600 mr-4">
                              {formatNumber(source.sessions)}
                            </div>
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${source.percentage}%` }}
                              ></div>
                            </div>
                            <div className="text-sm text-gray-500 ml-2 w-12">
                              {source.percentage}%
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Top Pages */}
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Top Pages</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {pages.map((page, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">
                            {page.title}
                          </div>
                          <div className="text-xs text-gray-500">{page.page}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900">
                            {formatNumber(page.views)}
                          </div>
                          <div className="text-xs text-gray-500">
                            {formatNumber(page.uniqueViews)} unique
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Device Types */}
              {traffic && (
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">Device Types</h3>
                  </div>
                  <div className="p-6">
                    <div className="space-y-4">
                      {traffic.deviceTypes.map((device, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="text-sm font-medium text-gray-900">
                              {device.type}
                            </div>
                          </div>
                          <div className="flex items-center">
                            <div className="text-sm text-gray-600 mr-4">
                              {formatNumber(device.sessions)}
                            </div>
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-green-600 h-2 rounded-full"
                                style={{ width: `${device.percentage}%` }}
                              ></div>
                            </div>
                            <div className="text-sm text-gray-500 ml-2 w-12">
                              {device.percentage}%
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
