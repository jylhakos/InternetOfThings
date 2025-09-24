// Main entry point for $lib alias - exports commonly used utilities and components

// Export authentication store
export { authStore } from './stores/auth.js';

// Export API utilities and types
export { default as api, authApi, dataApi } from './api.js';
export type { LoginCredentials, RegisterCredentials, ApiResponse } from './api.js';

// Export utility functions
export * from './utils.js';

// Export Svelte components for easier importing
export { default as LoginForm } from './components/LoginForm.svelte';
export { default as RegisterForm } from './components/RegisterForm.svelte';
export { default as Dashboard } from './components/Dashboard.svelte';

// Example of how to use these exports in other files:
// import { authStore, LoginForm, authApi } from '$lib';
// instead of:
// import { authStore } from '$lib/stores/auth';
// import LoginForm from '$lib/components/LoginForm.svelte';
// import { authApi } from '$lib/api';
