import { Activity, Database, Users, Zap } from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { cacheAPI, healthAPI, performanceAPI } from '../services/api'
import { getUserProfile } from '../store/authSlice'
import { RootState } from '../store/store'

const Dashboard: React.FC = () => {
  const dispatch = useDispatch()
  const { user } = useSelector((state: RootState) => state.auth)
  const [healthStatus, setHealthStatus] = useState<any>(null)
  const [performanceData, setPerformanceData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!user) {
      dispatch(getUserProfile())
    }
    loadDashboardData()
  }, [dispatch, user])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      const [health, performance] = await Promise.all([
        healthAPI.check(),
        performanceAPI.heavyOperation()
      ])
      setHealthStatus(health)
      setPerformanceData(performance)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const testCache = async () => {
    try {
      const key = `test_${Date.now()}`
      const value = `value_${Math.random()}`
      
      // Set cache
      await cacheAPI.test(key, value)
      
      // Get cache
      const result = await cacheAPI.test(key)
      console.log('Cache test result:', result)
      
      alert(`Cache test successful! Key: ${key}, Value: ${result.value}`)
    } catch (error) {
      console.error('Cache test failed:', error)
      alert('Cache test failed')
    }
  }

  if (loading && !healthStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Dashboard
          </h2>
          <p className="text-gray-500">Welcome back, {user?.phone || 'User'}</p>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    System Health
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {healthStatus?.status || 'Unknown'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Database className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Redis Status
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {healthStatus?.services?.redis || 'Unknown'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Zap className="h-6 w-6 text-yellow-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Performance
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {performanceData?.processing_time 
                      ? `${(performanceData.processing_time * 1000).toFixed(2)}ms`
                      : 'N/A'
                    }
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    User Status
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    Authenticated
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Quick Actions
          </h3>
          <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <button
              onClick={loadDashboardData}
              disabled={loading}
              className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Refresh Data'}
            </button>
            
            <button
              onClick={testCache}
              className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Test Cache
            </button>
            
            <button
              onClick={() => window.open('/health', '_blank')}
              className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Health Check
            </button>
          </div>
        </div>
      </div>

      {/* System Information */}
      {healthStatus && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              System Information
            </h3>
            <div className="mt-5">
              <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
                {JSON.stringify(healthStatus, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
