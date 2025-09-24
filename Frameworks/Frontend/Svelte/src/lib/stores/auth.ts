import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const defaultAuthState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false
};

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>(defaultAuthState);

  return {
    subscribe,
    login: (user: User, token: string) => {
      const authState: AuthState = {
        user,
        token,
        isAuthenticated: true,
        isLoading: false
      };
      set(authState);
      if (browser) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
      }
    },
    logout: () => {
      set(defaultAuthState);
      if (browser) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    },
    setLoading: (isLoading: boolean) => {
      update(state => ({ ...state, isLoading }));
    },
    init: () => {
      if (browser) {
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        if (token && userStr) {
          try {
            const user = JSON.parse(userStr);
            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false
            });
          } catch (error) {
            console.error('Error parsing stored user data:', error);
            set(defaultAuthState);
          }
        }
      }
    }
  };
}

export const authStore = createAuthStore();