<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { authApi, authStore, type LoginCredentials } from '$lib';

  const dispatch = createEventDispatcher();

  let email = '';
  let password = '';
  let isLoading = false;
  let error = '';

  async function handleSubmit() {
    if (!email || !password) {
      error = 'Please fill in all fields';
      return;
    }

    isLoading = true;
    error = '';
    authStore.setLoading(true);

    try {
      const credentials: LoginCredentials = { email, password };
      const response = await authApi.login(credentials);
      
      if (response.success && response.data) {
        authStore.login(response.data.user, response.data.token);
        dispatch('login-success');
      } else {
        error = response.message || 'Login failed';
      }
    } catch (err: any) {
      error = err.response?.data?.message || 'Login failed. Please try again.';
      console.error('Login error:', err);
    } finally {
      isLoading = false;
      authStore.setLoading(false);
    }
  }

  function goToRegister() {
    dispatch('switch-to-register');
  }
</script>

<div class="login-form">
  <h2>Login</h2>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}

  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="email">Email:</label>
      <input
        type="email"
        id="email"
        bind:value={email}
        required
        disabled={isLoading}
      />
    </div>

    <div class="form-group">
      <label for="password">Password:</label>
      <input
        type="password"
        id="password"
        bind:value={password}
        required
        disabled={isLoading}
      />
    </div>

    <button type="submit" disabled={isLoading}>
      {isLoading ? 'Logging in...' : 'Login'}
    </button>
  </form>

  <p class="switch-form">
    Don't have an account? 
    <button type="button" class="link-button" on:click={goToRegister}>
      Register here
    </button>
  </p>
</div>

<style>
  .login-form {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #333;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
    color: #555;
  }

  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  input:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
  }

  button {
    width: 100%;
    padding: 0.75rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover:not(:disabled) {
    background-color: #0056b3;
  }

  button:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }

  .error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .switch-form {
    text-align: center;
    margin-top: 1rem;
    color: #666;
  }

  .link-button {
    background: none;
    border: none;
    color: #007bff;
    text-decoration: underline;
    cursor: pointer;
    font-size: inherit;
    width: auto;
    padding: 0;
  }

  .link-button:hover {
    color: #0056b3;
  }
</style>