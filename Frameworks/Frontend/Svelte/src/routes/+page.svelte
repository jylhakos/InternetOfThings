<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import LoginForm from '$lib/components/LoginForm.svelte';
	import RegisterForm from '$lib/components/RegisterForm.svelte';
	import Dashboard from '$lib/components/Dashboard.svelte';

	let currentView: 'landing' | 'login' | 'register' | 'dashboard' = 'landing';
	let isAuthenticated = false;

	// Subscribe to auth store
	$: {
		isAuthenticated = $authStore.isAuthenticated;
		if (isAuthenticated) {
			currentView = 'dashboard';
		}
	}

	function showLogin() {
		currentView = 'login';
	}

	function showRegister() {
		currentView = 'register';
	}

	function showLanding() {
		if (!isAuthenticated) {
			currentView = 'landing';
		}
	}

	function handleLoginSuccess() {
		currentView = 'dashboard';
	}

	function handleRegisterSuccess() {
		currentView = 'dashboard';
	}

	function switchToRegister() {
		currentView = 'register';
	}

	function switchToLogin() {
		currentView = 'login';
	}
</script>

<svelte:head>
	<title>SvelteKit SPA - Home</title>
	<meta name="description" content="SvelteKit SPA with Node.js backend and PostgreSQL" />
</svelte:head>

<div class="container page-transition">
	{#if currentView === 'landing'}
		<div class="landing-page">
			<header class="hero">
				<h1>Welcome to SvelteKit SPA</h1>
				<p class="hero-description">
					A modern single-page application built with SvelteKit, Node.js, and PostgreSQL.
					Experience seamless authentication and data management with a beautiful, responsive interface.
				</p>
				<div class="hero-actions">
					<button class="btn btn-primary" on:click={showLogin}>
						Login
					</button>
					<button class="btn btn-secondary" on:click={showRegister}>
						Register
					</button>
				</div>
			</header>

			<section class="features">
				<h2>Features</h2>
				<div class="features-grid">
					<div class="feature-card">
						<h3>🚀 Fast & Modern</h3>
						<p>Built with SvelteKit for lightning-fast performance and optimal user experience.</p>
					</div>
					<div class="feature-card">
						<h3>🔐 Secure Authentication</h3>
						<p>JWT-based authentication with secure password hashing and session management.</p>
					</div>
					<div class="feature-card">
						<h3>📱 Mobile Ready</h3>
						<p>Responsive design that works perfectly on all devices, ready for Android deployment with Capacitor.</p>
					</div>
					<div class="feature-card">
						<h3>🛡️ RESTful API</h3>
						<p>Robust Node.js backend with Express.js and PostgreSQL database integration.</p>
					</div>
				</div>
			</section>
		</div>
	{:else if currentView === 'login'}
		<div class="auth-container">
			<LoginForm 
				on:login-success={handleLoginSuccess}
				on:switch-to-register={switchToRegister}
			/>
			<button class="back-link" on:click={showLanding}>
				← Back to Home
			</button>
		</div>
	{:else if currentView === 'register'}
		<div class="auth-container">
			<RegisterForm 
				on:register-success={handleRegisterSuccess}
				on:switch-to-login={switchToLogin}
			/>
			<button class="back-link" on:click={showLanding}>
				← Back to Home
			</button>
		</div>
	{:else if currentView === 'dashboard'}
		<Dashboard />
	{/if}
</div>

<style>
	.container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.landing-page {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.hero {
		text-align: center;
		padding: 4rem 2rem;
		background: linear-gradient(135deg, var(--color-bg-0) 0%, var(--color-bg-1) 100%);
		border-bottom: 1px solid #e0e0e0;
	}

	.hero h1 {
		font-size: 3rem;
		margin: 0 0 1rem 0;
		color: var(--color-theme-1);
		font-weight: 700;
	}

	.hero-description {
		font-size: 1.2rem;
		color: var(--color-text);
		max-width: 600px;
		margin: 0 auto 2rem auto;
		line-height: 1.6;
	}

	.hero-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.btn {
		padding: 0.75rem 2rem;
		border: none;
		border-radius: 50px;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		text-decoration: none;
		display: inline-block;
		min-width: 120px;
	}

	.btn-primary {
		background: var(--color-theme-1);
		color: white;
		box-shadow: 0 4px 15px rgba(255, 62, 0, 0.3);
	}

	.btn-primary:hover {
		background: #e63900;
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(255, 62, 0, 0.4);
	}

	.btn-secondary {
		background: white;
		color: var(--color-theme-1);
		border: 2px solid var(--color-theme-1);
		box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
	}

	.btn-secondary:hover {
		background: var(--color-theme-1);
		color: white;
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(255, 62, 0, 0.3);
	}

	.features {
		padding: 4rem 2rem;
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
	}

	.features h2 {
		text-align: center;
		font-size: 2.5rem;
		margin-bottom: 3rem;
		color: var(--color-theme-2);
	}

	.features-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 2rem;
	}

	.feature-card {
		background: white;
		padding: 2rem;
		border-radius: 12px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
		transition: transform 0.3s ease, box-shadow 0.3s ease;
	}

	.feature-card:hover {
		transform: translateY(-5px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
	}

	.feature-card h3 {
		font-size: 1.3rem;
		margin: 0 0 1rem 0;
		color: var(--color-theme-2);
	}

	.feature-card p {
		color: var(--color-text);
		line-height: 1.6;
		margin: 0;
	}

	.auth-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 2rem;
		min-height: 100vh;
	}

	.back-link {
		background: none;
		border: none;
		color: var(--color-theme-1);
		text-decoration: underline;
		cursor: pointer;
		margin-top: 1rem;
		font-size: 1rem;
	}

	.back-link:hover {
		color: #e63900;
	}

	@media (max-width: 768px) {
		.hero h1 {
			font-size: 2rem;
		}

		.hero-description {
			font-size: 1rem;
		}

		.hero-actions {
			flex-direction: column;
			align-items: center;
		}

		.features {
			padding: 2rem 1rem;
		}

		.features h2 {
			font-size: 2rem;
		}

		.feature-card {
			padding: 1.5rem;
		}
	}
</style>
