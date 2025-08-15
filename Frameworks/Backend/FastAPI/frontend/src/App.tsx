import { Toaster } from 'react-hot-toast'
import { useSelector } from 'react-redux'
import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Profile from './pages/Profile'
import Register from './pages/Register'
import { RootState } from './store/store'

function App() {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth)

  return (
    <div className="min-h-screen bg-gray-50">
      <Layout>
        <Routes>
          <Route
            path="/"
            element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
          />
          <Route
            path="/profile"
            element={isAuthenticated ? <Profile /> : <Navigate to="/login" />}
          />
        </Routes>
      </Layout>
      <Toaster position="top-right" />
    </div>
  )
}

export default App
