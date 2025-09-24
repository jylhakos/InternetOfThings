<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { authApi, authStore, type RegisterCredentials } from '$lib';

  const dispatch = createEventDispatcher();

  let name = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let isLoading = false;
  let error = '';

  async function handleSubmit() {
    if (!name || !email || !password || !confirmPassword) {
      error = 'Please fill in all fields';
      return;
    }

    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }

    if (password.length < 6) {
      error = 'Password must be at least 6 characters long';
      return;
    }

    isLoading = true;
    error = '';
    authStore.setLoading(true);

    try {
      const credentials: RegisterCredentials = { name, email, password };
      const response = await authApi.register(credentials);
      
      if (response.success && response.data) {
        authStore.login(response.data.user, response.data.token);
        dispatch('register-success');
      } else {
        error = response.message || 'Registration failed';
      }
    } catch (err: any) {
      error = err.response?.data?.message || 'Registration failed. Please try again.';
      console.error('Registration error:', err);
    } finally {
      isLoading = false;
      authStore.setLoading(false);
    }
  }

  function goToLogin() {
    dispatch('switch-to-login');
  }
</script>

<div class="register-form">
  <h2>Register</h2>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}

  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="name">Name:</label>
      <input
        type="text"
        id="name"
        bind:value={name}
        required
        disabled={isLoading}
      />
    </div>

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
        minlength="6"
      />
    </div>

    <div class="form-group">
      <label for="confirm-password">Confirm Password:</label>
      <input
        type="password"
        id="confirm-password"
        bind:value={confirmPassword}
        required
        disabled={isLoading}
        minlength="6"
      />
    </div>

    <button type="submit" disabled={isLoading}>
      {isLoading ? 'Registering...' : 'Register'}
    </button>
  </form>

  <p class="switch-form">
    Already have an account? 
    <button type="button" class="link-button" on:click={goToLogin}>
      Login here
    </button>
  </p>
</div>

<style>
  .register-form {
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
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover:not(:disabled) {
    background-color: #218838;
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