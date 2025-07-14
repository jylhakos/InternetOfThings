'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import Cookies from 'js-cookie';
import { User, ApiResponse } from '@/types';
import { apiClient } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (userData: any) => Promise<void>;
  signout: () => void;
  updateUser: (userData: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = Cookies.get('token');
      const storedUser = Cookies.get('user');

      if (storedToken && storedUser) {
        try {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          
          // Verify token is still valid
          await apiClient.auth.verify();
        } catch (error) {
          // Token is invalid, clear storage
          Cookies.remove('token');
          Cookies.remove('user');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const signin = async (email: string, password: string) => {
    try {
      const response: ApiResponse = await apiClient.auth.signin({ email, password });
      
      if (response.success && response.data) {
        const { user: userData, token: userToken } = response.data;
        
        setUser(userData);
        setToken(userToken);
        
        // Store in cookies
        Cookies.set('token', userToken, { expires: 1 }); // 1 day
        Cookies.set('user', JSON.stringify(userData), { expires: 1 });
      } else {
        throw new Error(response.error || 'Sign in failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const signup = async (userData: any) => {
    try {
      const response: ApiResponse = await apiClient.auth.signup(userData);
      
      if (response.success && response.data) {
        const { user: newUser, token: userToken } = response.data;
        
        setUser(newUser);
        setToken(userToken);
        
        // Store in cookies
        Cookies.set('token', userToken, { expires: 1 });
        Cookies.set('user', JSON.stringify(newUser), { expires: 1 });
      } else {
        throw new Error(response.error || 'Sign up failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const signout = () => {
    setUser(null);
    setToken(null);
    Cookies.remove('token');
    Cookies.remove('user');
  };

  const updateUser = (userData: User) => {
    setUser(userData);
    Cookies.set('user', JSON.stringify(userData), { expires: 1 });
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    signin,
    signup,
    signout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
