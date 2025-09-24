<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';

	let { children } = $props();

	onMount(() => {
		// Initialize auth store on app start
		authStore.init();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>SvelteKit SPA</title>
</svelte:head>

<main>
	{@render children?.()}
</main>

<style>
	:global(html) {
		--font-mono: 'Fira Code', monospace;
		--color-bg-0: #fff;
		--color-bg-1: #f7f8fc;
		--color-bg-2: #eef2ff;
		--color-theme-1: #ff3e00;
		--color-theme-2: #4075a6;
		--color-text: rgba(0, 0, 0, 0.7);
		--column-width: 42rem;
		--column-margin-top: 4rem;
		font-family: Arial, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
			Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
	}

	:global(body) {
		margin: 0;
		background-attachment: fixed;
		background-color: var(--color-bg-1);
		background-size: 100vw 100vh;
		background-image: radial-gradient(
				50% 50% at 20% 30%,
				var(--color-bg-2) 0%,
				transparent 50%
			),
			radial-gradient(60% 60% at 80% 70%, var(--color-bg-2) 0%, transparent 50%);
	}

	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		width: 100%;
		margin: 0 auto;
		box-sizing: border-box;
		min-height: 100vh;
	}
</style>
