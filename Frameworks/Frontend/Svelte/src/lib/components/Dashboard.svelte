<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore, dataApi } from '$lib';

  let items: any[] = [];
  let isLoading = false;
  let error = '';
  let newItemName = '';

  onMount(async () => {
    await loadItems();
  });

  async function loadItems() {
    isLoading = true;
    error = '';
    
    try {
      const response = await dataApi.getItems();
      if (response.success && response.data) {
        items = response.data;
      } else {
        error = response.message || 'Failed to load items';
      }
    } catch (err: any) {
      error = err.response?.data?.message || 'Failed to load items';
      console.error('Error loading items:', err);
    } finally {
      isLoading = false;
    }
  }

  async function addItem() {
    if (!newItemName.trim()) return;

    try {
      const response = await dataApi.createItem({ name: newItemName.trim() });
      if (response.success && response.data) {
        items = [...items, response.data];
        newItemName = '';
      } else {
        error = response.message || 'Failed to add item';
      }
    } catch (err: any) {
      error = err.response?.data?.message || 'Failed to add item';
      console.error('Error adding item:', err);
    }
  }

  function logout() {
    authStore.logout();
  }

  $: user = $authStore.user;
</script>

<div class="dashboard">
  <header class="dashboard-header">
    <h1>Dashboard</h1>
    <div class="user-info">
      <span>Welcome, {user?.name || 'User'}!</span>
      <button class="logout-button" on:click={logout}>Logout</button>
    </div>
  </header>

  <main class="dashboard-content">
    <section class="add-item-section">
      <h2>Add New Item</h2>
      <div class="add-item-form">
        <input
          type="text"
          bind:value={newItemName}
          placeholder="Enter item name"
          on:keydown={(e) => e.key === 'Enter' && addItem()}
        />
        <button on:click={addItem} disabled={!newItemName.trim()}>
          Add Item
        </button>
      </div>
    </section>

    <section class="items-section">
      <h2>Items</h2>
      
      {#if error}
        <div class="error">{error}</div>
      {/if}

      {#if isLoading}
        <div class="loading">Loading items...</div>
      {:else if items.length === 0}
        <div class="no-items">No items found. Add some items to get started!</div>
      {:else}
        <div class="items-grid">
          {#each items as item (item.id)}
            <div class="item-card">
              <h3>{item.name}</h3>
              <p>ID: {item.id}</p>
              {#if item.createdAt}
                <p class="created-at">Created: {new Date(item.createdAt).toLocaleDateString()}</p>
              {/if}
            </div>
          {/each}
        </div>
      {/if}

      <button class="refresh-button" on:click={loadItems} disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Refresh'}
      </button>
    </section>
  </main>
</div>

<style>
  .dashboard {
    min-height: 100vh;
    background-color: #f5f5f5;
  }

  .dashboard-header {
    background: white;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .dashboard-header h1 {
    margin: 0;
    color: #333;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .logout-button {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .logout-button:hover {
    background-color: #c82333;
  }

  .dashboard-content {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .add-item-section, .items-section {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }

  .add-item-section h2, .items-section h2 {
    margin-top: 0;
    color: #333;
  }

  .add-item-form {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .add-item-form input {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .add-item-form button {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .add-item-form button:hover:not(:disabled) {
    background-color: #218838;
  }

  .add-item-form button:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }

  .items-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .item-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid #e9ecef;
  }

  .item-card h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
  }

  .item-card p {
    margin: 0.25rem 0;
    color: #666;
    font-size: 0.9rem;
  }

  .created-at {
    font-style: italic;
  }

  .refresh-button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .refresh-button:hover:not(:disabled) {
    background-color: #0056b3;
  }

  .refresh-button:disabled {
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

  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .no-items {
    text-align: center;
    padding: 2rem;
    color: #666;
    font-style: italic;
  }
</style>