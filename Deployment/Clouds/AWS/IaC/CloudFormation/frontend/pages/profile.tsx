import Head from 'next/head'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { useForm } from 'react-hook-form'
import { apiClient } from '../lib/api'
import toast from 'react-hot-toast'

interface ProfileForm {
  username: string
  phone: string
}

export default function Profile() {
  const { user, logout, loading, refreshUserProfile } = useAuth()
  const router = useRouter()
  const [isUpdating, setIsUpdating] = useState(false)
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<ProfileForm>()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
    
    if (user) {
      setValue('username', user.username)
      setValue('phone', user.phone || '')
    }
  }, [user, loading, router, setValue])

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

  const onSubmit = async (data: ProfileForm) => {
    setIsUpdating(true)
    try {
      await apiClient.put('/users/profile', {
        username: data.username,
        phone: data.phone || undefined,
      })
      
      await refreshUserProfile()
      toast.success('Profile updated successfully!')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to update profile'
      toast.error(message)
    } finally {
      setIsUpdating(false)
    }
  }

  return (
    <>
      <Head>
        <title>Profile - Microservices App</title>
        <meta name="description" content="Manage your profile" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="container mx-auto px-4 py-6">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <Link href="/" className="text-primary-600 hover:text-primary-700">
                  ← Back to Dashboard
                </Link>
                <h1 className="text-2xl font-bold text-gray-900">
                  User Profile
                </h1>
              </div>
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
          <div className="max-w-2xl mx-auto">
            {/* Profile Form */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Edit Profile Information
              </h2>
              
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div>
                  <label htmlFor="username" className="form-label">
                    Username
                  </label>
                  <input
                    {...register('username', {
                      required: 'Username is required',
                      minLength: {
                        value: 3,
                        message: 'Username must be at least 3 characters',
                      },
                      pattern: {
                        value: /^[a-zA-Z0-9]+$/,
                        message: 'Username can only contain letters and numbers',
                      },
                    })}
                    type="text"
                    className="form-input"
                  />
                  {errors.username && (
                    <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="email" className="form-label">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={user.email}
                    disabled
                    className="form-input bg-gray-100 cursor-not-allowed"
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Email cannot be changed
                  </p>
                </div>

                <div>
                  <label htmlFor="phone" className="form-label">
                    Phone Number (Optional)
                  </label>
                  <input
                    {...register('phone', {
                      pattern: {
                        value: /^\+?[1-9]\d{1,14}$/,
                        message: 'Invalid phone number format',
                      },
                    })}
                    type="tel"
                    className="form-input"
                    placeholder="+1234567890"
                  />
                  {errors.phone && (
                    <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
                  )}
                </div>

                <div className="flex space-x-4">
                  <button
                    type="submit"
                    disabled={isUpdating}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isUpdating ? 'Updating...' : 'Update Profile'}
                  </button>
                  <Link href="/" className="btn-secondary">
                    Cancel
                  </Link>
                </div>
              </form>
            </div>

            {/* Account Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Account Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">User ID</label>
                  <div className="p-2 bg-gray-50 rounded">{user.id}</div>
                </div>
                <div>
                  <label className="form-label">Member Since</label>
                  <div className="p-2 bg-gray-50 rounded">
                    {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
                <div>
                  <label className="form-label">Current Username</label>
                  <div className="p-2 bg-gray-50 rounded">{user.username}</div>
                </div>
                <div>
                  <label className="form-label">Current Phone</label>
                  <div className="p-2 bg-gray-50 rounded">
                    {user.phone || 'Not provided'}
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Security
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Your account is secured with JWT authentication. 
                  Tokens automatically expire for security.
                </p>
                <button
                  onClick={logout}
                  className="btn-secondary text-red-600 border-red-300 hover:bg-red-50"
                >
                  Sign Out of All Sessions
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
