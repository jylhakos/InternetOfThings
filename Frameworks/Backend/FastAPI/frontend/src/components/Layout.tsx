import { Home, LogOut, User } from 'lucide-react'
import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link, useLocation } from 'react-router-dom'
import { logout } from '../store/authSlice'
import { RootState } from '../store/store'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth)
  const dispatch = useDispatch()
  const location = useLocation()

  const handleLogout = () => {
    dispatch(logout())
  }

  const isAuthPage = ['/login', '/register'].includes(location.pathname)

  if (isAuthPage) {
    return <div className="container mx-auto px-4">{children}</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {isAuthenticated && (
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/dashboard" className="flex items-center space-x-2">
                  <Home className="h-6 w-6 text-blue-600" />
                  <span className="text-xl font-semibold text-gray-900">
                    FastAPI Microservices
                  </span>
                </Link>
              </div>

              <div className="flex items-center space-x-4">
                <Link
                  to="/dashboard"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    location.pathname === '/dashboard'
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Dashboard
                </Link>

                <Link
                  to="/profile"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    location.pathname === '/profile'
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Profile
                </Link>

                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <User className="h-5 w-5 text-gray-400" />
                    <span className="text-sm text-gray-700">
                      {user?.phone || 'User'}
                    </span>
                  </div>
                  
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </nav>
      )}

      <main className="flex-1">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
