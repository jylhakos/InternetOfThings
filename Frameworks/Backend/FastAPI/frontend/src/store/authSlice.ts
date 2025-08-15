import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit'
import { authAPI } from '../services/api'

export interface User {
  user_id: string
  phone: string
  email: string
}

export interface AuthState {
  isAuthenticated: boolean
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: localStorage.getItem('token'),
  loading: false,
  error: null,
}

// Async thunks
export const loginAsync = createAsyncThunk(
  'auth/login',
  async ({ phone, password }: { phone: string; password: string }) => {
    const response = await authAPI.login({ phone, password })
    return response
  }
)

export const registerAsync = createAsyncThunk(
  'auth/register',
  async ({ phone, password, email }: { phone: string; password: string; email: string }) => {
    const response = await authAPI.register({ phone, password, email })
    return response
  }
)

export const getUserProfile = createAsyncThunk(
  'auth/profile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getProfile()
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get profile')
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.isAuthenticated = false
      state.user = null
      state.token = null
      state.error = null
      localStorage.removeItem('token')
    },
    clearError: (state) => {
      state.error = null
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload
      state.isAuthenticated = true
      localStorage.setItem('token', action.payload)
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.loading = false
        state.isAuthenticated = true
        state.token = action.payload.access_token
        localStorage.setItem('token', action.payload.access_token)
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Login failed'
        state.isAuthenticated = false
        state.token = null
      })
      // Register
      .addCase(registerAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(registerAsync.fulfilled, (state, action) => {
        state.loading = false
        // Don't auto-login after registration
      })
      .addCase(registerAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Registration failed'
      })
      // Profile
      .addCase(getUserProfile.fulfilled, (state, action) => {
        state.user = action.payload
      })
      .addCase(getUserProfile.rejected, (state, action) => {
        state.error = action.payload as string
        // If profile fetch fails due to invalid token, logout
        if (action.payload === 'Invalid token' || action.payload === 'Token expired') {
          state.isAuthenticated = false
          state.token = null
          localStorage.removeItem('token')
        }
      })
  },
})

export const { logout, clearError, setToken } = authSlice.actions
export default authSlice.reducer
