<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let role: string | null = null;
	let id_orang_tua: string | null = null;
	let isOpen = false;

	// Ambil data user dari sessionStorage
	if (typeof window !== 'undefined') {
		const token = sessionStorage.getItem('token');
		if (token) {
			const payload = decodeJWT(token);
			if (payload) {
				role = payload.role;
				if (role === 'orang_tua') id_orang_tua = payload.user_id;
			}
		}
	}

	function decodeJWT(token: string) {
		try {
			const base64Payload = token.split('.')[1];
			return JSON.parse(atob(base64Payload));
		} catch {
			return null;
		}
	}

	function logout() {
		sessionStorage.clear();
		goto('/login');
	}

	// Navigasi untuk orang tua
	function goToDashboardOrtu() {
		goto(`/dashboard-orangtua`);
	}
	function goToListAnak() {
		goto(`/list-anak?id_orangtua=${id_orang_tua}`);
	}
	function goToTambahAnak() {
		goto(`/crud-anak?id_orangtua=${id_orang_tua}`);
	}

	// Navigasi untuk perawat
	function goToDashboardPerawat() {
		goto(`/dashboard-perawat`);
	}
	function goToListOrangtua() {
		goto(`/list-orangtua`);
	}
	function goToTambahPengukuran() {
		goto(`/form-pengukuran-step1`);
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if $page.url.pathname !== '/login' && $page.url.pathname !== '/register'}
	<nav
		class="sticky top-0 z-50 flex items-center justify-between bg-gradient-to-r from-[#029ae2] to-[#6ed3ff] px-6 py-3 text-white"
	>
		<!-- LEFT -->
		<div class="flex items-center">
			<h1
				class="cursor-pointer text-lg font-bold"
				on:click={() => (role === 'perawat' ? goToDashboardPerawat() : goToDashboardOrtu())}
			>
				BalitaCare
			</h1>
		</div>

		<!-- HAMBURGER (mobile) -->
		<button class="flex flex-col gap-1 sm:hidden" on:click={() => (isOpen = !isOpen)}>
			<div class="h-0.5 w-6 bg-white"></div>
			<div class="h-0.5 w-6 bg-white"></div>
			<div class="h-0.5 w-6 bg-white"></div>
		</button>

		<!-- MENU DESKTOP -->
		<div class="hidden items-center gap-6 text-sm font-medium sm:flex">
			{#if role === 'perawat'}
				<button class="hover:underline" on:click={goToDashboardPerawat}>Dashboard</button>
				<button class="hover:underline" on:click={goToTambahPengukuran}>Tambah Pengukuran</button>
			{:else if role === 'orang_tua'}
				<button class="hover:underline" on:click={goToDashboardOrtu}>Dashboard</button>
				<button class="hover:underline" on:click={goToListAnak}>Daftar Anak</button>
				<button class="hover:underline" on:click={goToTambahAnak}>Tambah Anak</button>
			{/if}

			<button
				class="rounded-md bg-white px-3 py-1 font-semibold text-[#2d6cdf] hover:bg-gray-100"
				on:click={logout}
			>
				Logout
			</button>
		</div>
	</nav>

	<!-- MENU MOBILE -->
	{#if isOpen}
		<div class="flex flex-col gap-4 bg-[#4ec6ff] px-6 py-4 text-white sm:hidden">
			{#if role === 'perawat'}
				<button on:click={goToDashboardPerawat}>Dashboard</button>
				<button on:click={goToTambahPengukuran}>Tambah Pengukuran</button>
			{:else if role === 'orang_tua'}
				<button on:click={goToDashboardOrtu}>Dashboard</button>
				<button on:click={goToListAnak}>Daftar Anak</button>
				<button on:click={goToTambahAnak}>Tambah Anak</button>
			{/if}

			<button class="rounded-md bg-white px-3 py-1 font-semibold text-[#2d6cdf]" on:click={logout}>
				Logout
			</button>
		</div>
	{/if}
{/if}

<slot />
