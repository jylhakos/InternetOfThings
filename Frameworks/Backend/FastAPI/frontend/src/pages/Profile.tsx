import { Mail, Phone, User } from 'lucide-react'
import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { getUserProfile } from '../store/authSlice'
import { RootState } from '../store/store'

const Profile: React.FC = () => {
  const dispatch = useDispatch()
  const { user, loading } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    if (!user) {
      dispatch(getUserProfile())
    }
  }, [dispatch, user])

  if (loading) {
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
            Profile
          </h2>
          <p className="text-gray-500">Manage your account information</p>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="space-y-6">
            {/* Avatar */}
            <div className="flex items-center space-x-6">
              <div className="flex-shrink-0">
                <div className="h-20 w-20 rounded-full bg-blue-100 flex items-center justify-center">
                  <User className="h-10 w-10 text-blue-600" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  {user?.phone || 'Unknown User'}
                </h3>
                <p className="text-sm text-gray-500">User Profile</p>
              </div>
            </div>

            {/* Profile Information */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Phone Number
                </label>
                <div className="mt-1 flex items-center space-x-3">
                  <Phone className="h-5 w-5 text-gray-400" />
                  <span className="text-sm text-gray-900">
                    {user?.phone || 'Not provided'}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <div className="mt-1 flex items-center space-x-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                  <span className="text-sm text-gray-900">
                    {user?.email || 'Not provided'}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  User ID
                </label>
                <div className="mt-1 flex items-center space-x-3">
                  <User className="h-5 w-5 text-gray-400" />
                  <span className="text-sm text-gray-900 font-mono">
                    {user?.user_id || 'Not available'}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Account Status
                </label>
                <div className="mt-1">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="border-t border-gray-200 pt-6">
              <div className="flex space-x-3">
                <button
                  type="button"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Edit Profile
                </button>
                <button
                  type="button"
                  className="bg-white hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-md text-sm font-medium border border-gray-300"
                >
                  Change Password
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
