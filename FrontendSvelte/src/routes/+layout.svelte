<script lang="ts">
    import { onMount } from 'svelte';
    import '../app.css';
    import favicon from '$lib/assets/favicon.svg';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { browser } from '$app/environment';

    let role: string | null = null;
    let id_orang_tua: string | null = null;
    let isOpen = false;

    // Ambil data user dari sessionStorage
    onMount(() => {
        if (!browser) return;

        const token = sessionStorage.getItem('token');
        if (token) {
            const payload = decodeJWT(token);
            if (payload) {
                role = payload.role;
                if (role === 'orang_tua') id_orang_tua = payload.user_id;
            }
        }
    });

    function decodeJWT(token: string) {
        try {
            const base64Payload = token.split('.')[1];
            return JSON.parse(atob(base64Payload));
        } catch (error) {
            console.error('Error decoding JWT:', error);
            return null;
        }
    }

    async function logout() {
        if (!browser) return;

        try {
            // Ambil token sebelum menghapusnya
            const token = sessionStorage.getItem('token');

            // Hapus token dari sessionStorage
            sessionStorage.removeItem('token');

            // Jika ada API untuk logout di backend, panggil di sini
            if (token) {
                // Contoh: await fetch('/api/logout', {
                //   method: 'POST',
                //   headers: {
                //     'Authorization': `Bearer ${token}`
                //   }
                // });
                // Ini opsional, tergantung pada implementasi backend Anda
            }

            // Reset variabel lokal
            role = null;
            id_orang_tua = null;

            // Arahkan ke halaman login
            goto('/sign-in');
        } catch (error) {
            console.error('Error during logout:', error);
            // Jika terjadi kesalahan, tetap arahkan ke halaman login
            goto('/sign-in');
        }
    }

    // Navigasi untuk orang tua
    function goToDashboardOrtu() {
        goto(`/ortu-dash`);
    }
    function goToListAnak() {
        goto(`/anak-daf?id_orangtua=${id_orang_tua}`);
    }
    function goToTambahAnak() {
        goto(`/anak-kel?id_orangtua=${id_orang_tua}`);
    }

    // Navigasi untuk perawat
    function goToDashboardPerawat() {
        goto(`/per-dash`);
    }
    function goToListOrangtua() {
        goto(`/list-orangtua`);
    }
    function goToTambahPengukuran() {
        goto(`/peng1`);
    }
</script>


<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

{#if $page.url.pathname !== '/sign-in' && $page.url.pathname !== '/sign-up' && $page.url.pathname !== '/'}
    <nav
        class="sticky top-0 z-50 flex items-center justify-between bg-gradient-to-r from-[#2b7fff] to-[#00d3f3] px-6 py-3 text-white"
    >

        <div class="flex items-center">
            <h1
                class="cursor-pointer text-lg font-bold"
                on:click={() => (role === 'perawat' ? goToDashboardPerawat() : goToDashboardOrtu())}
            >
                BalitaCare
            </h1>
        </div>

        <!-- Menu toggle untuk mobile -->
        <button class="flex flex-col gap-1 sm:hidden" on:click={() => (isOpen = !isOpen)}>
            <div class="h-0.5 w-6 bg-white"></div>
            <div class="h-0.5 w-6 bg-white"></div>
            <div class="h-0.5 w-6 bg-white"></div>
        </button>

        <!-- Menu untuk desktop -->
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

    <!-- Menu untuk mobile -->
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