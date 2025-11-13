<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';

    // Data anak dan pengukuran
    let anakList: any[] = [];
    let selectedAnak: any = null;
    
    // Objek untuk menyimpan detail setiap anak yang sudah di-preload
    let anakDetailsMap = new Map<string, any>();

    // State untuk data anak yang sedang ditampilkan
    let anak = {
        nama: '-',
        jenis_kelamin: '-',
        tanggal_lahir: '-',
        umur_bulan: '-'
    };

    let peng = {
        berat_badan: '-',
        tinggi_badan: '-',
        lingkar_kepala: '-',
        lingkar_lengan: '-',
        created_at: '-'
    };

    let hasil: Record<string, any> = {};
    let ai_analysis: Record<string, any> = {};

    let isLoading = true; // Untuk loading daftar anak awal
    let isInitialLoad = true; // Untuk preloading detail semua anak
    let id_orang_tua: string | null = null;
    let role = '';

    const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

    // ---------- UTIL FUNGI ----------
    function decodeJWT(token: string) {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch {
            return null;
        }
    }

    function cekToken() {
        const token = sessionStorage.getItem('token');
        if (!token) {
            alert('Anda belum login!');
            goto('/sign-in');
            return null;
        }
        const payload = decodeJWT(token);
        if (!payload || !payload.user_id) {
            alert('Sesi tidak valid, silakan login ulang.');
            goto('/sign-in');
            return null;
        }
        return token;
    }

    function hitungUmurBulan(tanggal_lahir: string) {
        if (!tanggal_lahir || tanggal_lahir === '-') return '-';
        const lahir = new Date(tanggal_lahir);
        if (isNaN(lahir.getTime())) return '-';
        const sekarang = new Date();
        return (
            (sekarang.getFullYear() - lahir.getFullYear()) * 12 +
            (sekarang.getMonth() - lahir.getMonth())
        );
    }

    function hitungUsia(tanggal_lahir: string) {
        if (!tanggal_lahir) return '-';
        const tglLahir = new Date(tanggal_lahir);
        const sekarang = new Date();
        let tahun = sekarang.getFullYear() - tglLahir.getFullYear();
        let bulan = sekarang.getMonth() - tglLahir.getMonth();
        if (bulan < 0) {
            tahun--;
            bulan += 12;
        }
        return `${tahun} th ${bulan} bln`;
    }

    // ---------- DATA LOAD ----------
    async function preloadAllAnakDetails() {
        if (anakList.length === 0) {
            isInitialLoad = false;
            return;
        }

        // Buat array promise untuk fetch detail setiap anak
        const detailPromises = anakList.map(async (anak) => {
            const res = await fetch(`${BACKEND_URL}/api/pengukuran/detail/${anak.id_anak}`);
            if (res.ok) {
                const data = await res.json();
                // Simpan detail ke map dengan key id_anak
                anakDetailsMap.set(anak.id_anak, data);
            }
            return anak.id_anak; // Kembalikan ID untuk tracking
        });

        try {
            // Tunggu semua promise selesai
            await Promise.all(detailPromises);
            
            // Setelah selesai, tampilkan data anak pertama
            if (anakList.length > 0) {
                selectedAnak = anakList[0];
                tampilkanDetailAnak(selectedAnak.id_anak);
            }
        } catch (error) {
            console.error("Gagal memuat detail anak:", error);
        } finally {
            // Matikan spinner loading
            isInitialLoad = false;
        }
    }

    async function loadAnakList() {
        const token = cekToken();
        if (!token) return;

        id_orang_tua = decodeJWT(token).user_id;

        try {
            const res = await fetch(`${BACKEND_URL}/api/anak-by-orangtua/${id_orang_tua}`, {
                headers: { Authorization: 'Bearer ' + token }
            });

            const data = await res.json();
            anakList = data;

            if (anakList.length > 0) {
                anakList.sort((a, b) => a.id_anak - b.id_anak);
                // Panggil fungsi preload setelah daftar anak didapat
                await preloadAllAnakDetails();
            } else {
                // Jika tidak ada anak, hentikan loading
                isInitialLoad = false;
            }
        } catch (err) {
            console.error('Gagal memuat data anak:', err);
            isInitialLoad = false;
        } finally {
            isLoading = false;
        }
    }

    // Fungsi untuk menampilkan detail anak dari data yang sudah di-preload
    function tampilkanDetailAnak(id_anak: string) {
        const detail = anakDetailsMap.get(id_anak);
        if (detail) {
            anak = {
                nama: detail?.anak?.nama ?? '-',
                jenis_kelamin: detail?.anak?.jenis_kelamin ?? '-',
                tanggal_lahir: detail?.anak?.tanggal_lahir ?? '-',
                umur_bulan: hitungUmurBulan(detail?.anak?.tanggal_lahir)
            };
            peng = {
                berat_badan: detail?.peng?.berat_badan ?? '-',
                tinggi_badan: detail?.peng?.tinggi_badan ?? '-',
                lingkar_kepala: detail?.peng?.lingkar_kepala ?? '-',
                lingkar_lengan: detail?.peng?.lingkar_lengan ?? '-',
                created_at: detail?.peng?.created_at
                    ? new Date(detail.peng.created_at).toLocaleDateString('id-ID', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                      })
                    : '-'
            };
            hasil = detail?.hasil ?? {};
            ai_analysis = detail?.ai_analysis ?? {};
        }
    }

    // ---------- HANDLER ----------
    function navigasiKe(url: string) {
        const token = cekToken();
        if (!token) return;
        goto(url);
    }

    function tampilkanGrafik(anakItem: any) {
        selectedAnak = anakItem;
        // Langsung tampilkan detail dari data preload, tidak perlu fetch ulang
        tampilkanDetailAnak(anakItem.id_anak);
    }

    function riwayatAnak(anakItem: any, e: Event) {
        e.stopPropagation();
        navigasiKe(`/anak-riwayat?id=${anakItem.id_anak}`);
    }

    function kelolaAnak() {
        navigasiKe(`/anak-daf?id_orangtua=${id_orang_tua}`);
    }

    function lihatDetail(anakItem: any) {
        navigasiKe(`/balita-det?id=${anakItem.id_anak}`);
    }

    function getStatusColor(status: string) {
        switch (status?.toLowerCase()) {
            case 'sangat baik':
            case 'baik':
            case 'normal':
                return 'text-green-600 bg-green-100';
            case 'perlu perhatian':
                return 'text-yellow-600 bg-yellow-100';
            case 'berisiko':
                return 'text-red-600 bg-red-100';
            default:
                return 'text-gray-600 bg-gray-100';
        }
    }

    onMount(async () => {
        const params = new URLSearchParams(window.location.search);
        role = params.get('role') || 'orangtua';
        await loadAnakList();
    });
</script>

<!-- Header Section -->
<div class="bg-gradient-to-r from-blue-500 to-cyan-400">
    <div class="container mx-auto px-4 py-8 sm:py-12">
        <div class="flex flex-col items-center justify-between gap-4 text-white sm:flex-row">
            <div class="text-center sm:text-left">
                <h1 class="mb-2 text-3xl font-bold sm:text-4xl">Dashboard Orangtua</h1>
                <p class="text-blue-50">Pantau tumbuh kembang anak Anda secara real-time</p>
            </div>
            <div
                class="rounded-xl border border-blue-400 bg-white/10 p-4 backdrop-blur-sm shadow-lg"
            >
                <div class="flex items-center gap-3">
                    <svg
                        class="h-8 w-8"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                        />
                    </svg>
                    <div>
                        <p class="text-sm text-blue-50">Total Anak</p>
                        <p class="text-2xl font-bold">{anakList.length}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="container mx-auto px-4 py-6">
    <!-- Header Actions -->
    <div class="mb-6 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
            <h2 class="text-2xl font-bold text-gray-900">Status Anak</h2>
            <p class="text-sm text-gray-500">Informasi pengukuran dan status gizi terkini</p>
        </div>
        <button
            on:click={kelolaAnak}
            class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white shadow-md transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300"
        >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
            </svg>
            Kelola Anak
        </button>
    </div>

    {#if isLoading}
        <!-- Loading State for the whole page initially -->
        <div class="space-y-4">
            <div class="h-12 w-full animate-pulse rounded-lg bg-gray-200"></div>
            <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div class="h-64 w-full animate-pulse rounded-lg bg-gray-200"></div>
                <div class="h-64 w-full animate-pulse rounded-lg bg-gray-200"></div>
                <div class="h-64 w-full animate-pulse rounded-lg bg-gray-200"></div>
            </div>
        </div>
    {:else if anakList.length === 0}
        <!-- Empty State -->
        <div class="rounded-xl border-2 border-dashed border-gray-300 bg-white p-12">
            <div class="flex flex-col items-center justify-center text-center">
                <svg class="mb-4 h-16 w-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                </svg>
                <h3 class="mb-2 text-lg font-semibold text-gray-900">Belum Ada Data Anak</h3>
                <p class="mb-4 text-sm text-gray-500">
                    Silakan tambahkan data anak untuk mulai memantau tumbuh kembang mereka
                </p>
                <button
                    on:click={kelolaAnak}
                    class="rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white transition hover:bg-blue-700"
                >
                    Tambah Anak
                </button>
            </div>
        </div>
    {:else}
        <!-- Mobile & Medium Dropdown -->
        <div class="mb-6 block lg:hidden">
            <select
                bind:value={selectedAnak}
                on:change={(e) => {
                    const id = parseInt(e.currentTarget.value);
                    const anakItem = anakList.find((a) => a.id_anak === id);
                    if (anakItem) tampilkanGrafik(anakItem);
                }}
                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
            >
                {#each anakList as anakItem}
                    <option value={anakItem.id_anak}>{anakItem.nama}</option>
                {/each}
            </select>
        </div>

        <!-- Main Content Grid -->
        <div class="grid gap-6 lg:grid-cols-3">
            <!-- Left Column: Child Details -->
            <div class="lg:col-span-2">
                {#if isInitialLoad}
                    <!-- Loading Spinner for initial data preload -->
                    <div class="flex h-64 items-center justify-center rounded-xl bg-white shadow-lg">
                        <div class="flex flex-col items-center">
                            <div class="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
                            <p class="mt-2 text-sm text-gray-500">Memuat data anak...</p>
                        </div>
                    </div>
                {:else if selectedAnak}
                    <div class="overflow-hidden rounded-xl bg-white shadow-lg">
                        <!-- Header -->
                        <div class="bg-gradient-to-r from-blue-50 to-cyan-50 p-6">
                            <div class="flex items-start justify-between">
                                <div>
                                    <h3 class="text-2xl font-bold text-gray-900">{anak.nama}</h3>
                                    <div class="mt-2 flex items-center gap-2 text-gray-600">
                                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                                            />
                                        </svg>
                                        <span class="text-sm">Usia: {hitungUsia(anak.tanggal_lahir)}</span>
                                    </div>
                                </div>
                                <span
                                    class="rounded-full border px-3 py-1 text-sm font-semibold {getStatusColor(
                                        hasil?.status || 'Normal'
                                    )}"
                                >
                                    {hasil?.status || 'Normal'}
                                </span>
                            </div>
                        </div>

                        <div class="p-6">
                            {#if peng.berat_badan === '-'}
                                <!-- State untuk anak yang belum memiliki pengukuran -->
                                <div class="rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center">
                                    <svg class="mx-auto mb-4 h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                        />
                                    </svg>
                                    <h3 class="mb-2 text-lg font-semibold text-gray-700">Belum Ada Data Pengukuran</h3>
                                    <p class="text-sm text-gray-500">
                                        Anak ini belum memiliki data pengukuran. Silakan tambahkan data untuk melihat analisis status gizi.
                                    </p>
                                </div>
                            {:else}
                                <!-- Pengukuran Terakhir -->
                                <div class="mb-6">
                                    <div class="mb-4 flex items-center gap-2">
                                        <svg class="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                                            />
                                        </svg>
                                        <h4 class="text-lg font-semibold text-gray-900">Pengukuran Terakhir</h4>
                                    </div>
                                    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
                                        <div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
                                            <p class="mb-1 text-xs text-gray-500">Tinggi Badan</p>
                                            <p class="text-xl font-bold text-blue-600">
                                                {peng.tinggi_badan}
                                            </p>
                                            <p class="text-xs text-gray-400">cm</p>
                                        </div>
                                        <div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
                                            <p class="mb-1 text-xs text-gray-500">Berat Badan</p>
                                            <p class="text-xl font-bold text-green-600">
                                                {peng.berat_badan}
                                            </p>
                                            <p class="text-xs text-gray-400">kg</p>
                                        </div>
                                        <div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
                                            <p class="mb-1 text-xs text-gray-500">Lingkar Kepala</p>
                                            <p class="text-xl font-bold text-purple-600">
                                                {peng.lingkar_kepala}
                                            </p>
                                            <p class="text-xs text-gray-400">cm</p>
                                        </div>
                                        <div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
                                            <p class="mb-1 text-xs text-gray-500">Lingkar Lengan</p>
                                            <p class="text-xl font-bold text-orange-600">
                                                {peng.lingkar_lengan}
                                            </p>
                                            <p class="text-xs text-gray-400">cm</p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Separator -->
                                <div class="my-6 border-t border-gray-200"></div>

                                <!-- Status Gizi -->
                                <div class="mb-6">
                                    <div class="mb-4 flex items-center gap-2">
                                        <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                                            />
                                        </svg>
                                        <h4 class="text-lg font-semibold text-gray-900">Hasil Analisis Status Gizi</h4>
                                    </div>
                                    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
                                        <div class="rounded-lg border border-green-200 bg-green-50 p-4">
                                            <p class="mb-1 text-xs font-medium text-gray-600">BB/U</p>
                                            <p class="text-sm font-semibold text-gray-900">
                                                {hasil['BB/U']?.kategori ?? '-'}
                                            </p>
                                        </div>
                                        <div class="rounded-lg border border-green-200 bg-green-50 p-4">
                                            <p class="mb-1 text-xs font-medium text-gray-600">IMT/U</p>
                                            <p class="text-sm font-semibold text-gray-900">
                                                {hasil['IMT/U']?.kategori ?? '-'}
                                            </p>
                                        </div>
                                        <div class="rounded-lg border border-green-200 bg-green-50 p-4">
                                            <p class="mb-1 text-xs font-medium text-gray-600">LILA/U</p>
                                            <p class="text-sm font-semibold text-gray-900">
                                                {hasil['LILA/U']?.kategori ?? '-'}
                                            </p>
                                        </div>
                                        <div class="rounded-lg border border-green-200 bg-green-50 p-4">
                                            <p class="mb-1 text-xs font-medium text-gray-600">LK/U</p>
                                            <p class="text-sm font-semibold text-gray-900">
                                                {hasil['LK/U']?.kategori ?? '-'}
                                            </p>
                                        </div>
                                        <div class="rounded-lg border border-green-200 bg-green-50 p-4">
                                            <p class="mb-1 text-xs font-medium text-gray-600">TB/U</p>
                                            <p class="text-sm font-semibold text-gray-900">
                                                {hasil['TB/U']?.kategori ?? '-'}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            {/if}

                            <!-- Action Buttons -->
                            <div class="flex flex-col gap-3 sm:flex-row">
                                <button
                                    on:click={() => lihatDetail(selectedAnak)}
                                    class="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white shadow-md transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300"
                                >
                                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                                        />
                                    </svg>
                                    Lihat Detail Lengkap
                                </button>
                                <button
                                    on:click={(e) => riwayatAnak(selectedAnak, e)}
                                    class="inline-flex flex-1 items-center justify-center gap-2 rounded-lg border-2 border-gray-300 bg-white px-6 py-3 font-semibold text-gray-700 transition hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-gray-200"
                                >
                                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                                        />
                                    </svg>
                                    Riwayat Pengukuran
                                </button>
                            </div>
                        </div>
                    </div>
                {:else}
                    <div class="rounded-xl bg-white p-12 text-center shadow-lg">
                        <p class="text-gray-500">Pilih anak untuk melihat detail</p>
                    </div>
                {/if}
            </div>

            <!-- Right Column: Child List (Desktop) -->
            <div class="hidden lg:block">
                <div class="h-full rounded-xl bg-white shadow-lg">
                    <div class="border-b p-6">
                        <h3 class="text-lg font-semibold text-gray-900">Daftar Anak</h3>
                        <p class="text-sm text-gray-500">Klik untuk melihat detail</p>
                    </div>
                    <div class="max-h-[calc(100vh-300px)] overflow-y-auto p-4">
                        <div class="space-y-2">
                            {#each anakList as anakItem}
                                <div
                                    class="cursor-pointer rounded-lg border-2 bg-white p-4 transition-all hover:shadow-md {selectedAnak?.id_anak ===
                                    anakItem.id_anak
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200'}"
                                    on:click={() => tampilkanGrafik(anakItem)}
                                    on:keydown={(e) => e.key === 'Enter' && tampilkanGrafik(anakItem)}
                                    role="button"
                                    tabindex="0"
                                >
                                    <div class="mb-2 flex items-start justify-between">
                                        <div>
                                            <p class="font-semibold text-gray-900">{anakItem.nama}</p>
                                            <p class="text-sm text-gray-500">
                                                {hitungUsia(anakItem.tanggal_lahir)}
                                            </p>
                                        </div>
                                    </div>
                                    <span
                                        class="inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold {getStatusColor(
                                            anakDetailsMap.get(anakItem.id_anak)?.hasil?.status || 'Normal'
                                        )}"
                                    >
                                        {anakDetailsMap.get(anakItem.id_anak)?.hasil?.status || 'Normal'}
                                    </span>
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>