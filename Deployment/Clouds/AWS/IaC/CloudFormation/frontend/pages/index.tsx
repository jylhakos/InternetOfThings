import Head from 'next/head'
import Link from 'next/link'
import { useAuth } from '../contexts/AuthContext'
import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Home() {
  const { user, logout, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Microservices App - Home</title>
        <meta name="description" content="Microservices application with React and Node.js" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="container mx-auto px-4 py-6">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Microservices App
              </h1>
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user.username}!</span>
                <button
                  onClick={logout}
                  className="btn-secondary"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            {/* Welcome Section */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Dashboard
              </h2>
              <p className="text-gray-600 mb-6">
                Welcome to your microservices application dashboard. This app demonstrates
                a modern architecture with React frontend and Node.js microservices backend.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Link href="/profile" className="block">
                  <div className="border border-gray-200 rounded-lg p-4 hover:border-primary-500 transition-colors cursor-pointer">
                    <h3 className="font-medium text-gray-900 mb-2">User Profile</h3>
                    <p className="text-sm text-gray-600">
                      View and update your personal information
                    </p>
                  </div>
                </Link>
                
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">API Status</h3>
                  <p className="text-sm text-gray-600">
                    All microservices are running properly
                  </p>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Healthy
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* User Info Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Your Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">Username</label>
                  <div className="p-2 bg-gray-50 rounded">{user.username}</div>
                </div>
                <div>
                  <label className="form-label">Email</label>
                  <div className="p-2 bg-gray-50 rounded">{user.email}</div>
                </div>
                <div>
                  <label className="form-label">Phone</label>
                  <div className="p-2 bg-gray-50 rounded">
                    {user.phone || 'Not provided'}
                  </div>
                </div>
                <div>
                  <label className="form-label">Member Since</label>
                  <div className="p-2 bg-gray-50 rounded">
                    {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
              </div>
              <div className="mt-6">
                <Link href="/profile" className="btn-primary">
                  Edit Profile
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
