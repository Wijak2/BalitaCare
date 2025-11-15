<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { writable, derived } from 'svelte/store';
    import { goto } from '$app/navigation';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';
    import * as Table from '$lib/components/ui/table';
    import * as Dialog from '$lib/components/ui/dialog';
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
    import { Badge } from '$lib/components/ui/badge';
    import { Trash, Edit, Plus, ArrowLeft, X, Search, Users, Baby, Calendar, AlertTriangle } from 'lucide-svelte';

    type Anak = {
        id: number;
        nama: string;
        jenis_kelamin: string;
        tanggal_lahir: string;
    };

    const anakList = writable<Anak[]>([]);
    const search = writable('');

    const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

    const notification = writable<{ message: string; type: 'success' | 'error' | '' }>({
        message: '',
        type: ''
    });

    function showNotification(message: string, type: 'success' | 'error') {
        notification.set({ message, type });
        setTimeout(() => notification.set({ message: '', type: '' }), 3000);
    }

    let showConfirmModal = false;
    let anakToDelete: number | null = null;
    let anakToDeleteName: string = '';
    let isDeleting = false;
    let isLoading = true;

    function konfirmasiHapus(id: number, nama: string) {
        anakToDelete = id;
        anakToDeleteName = nama;
        showConfirmModal = true;
    }

    async function hapusAnak() {
        if (!anakToDelete) return;

        showConfirmModal = false;
        isDeleting = true;

        try {
            const res = await fetch(`${BACKEND_URL}/anak/delete/${anakToDelete}`, {
                method: 'POST'
            });

            if (res.ok) {
                anakList.update((list) => list.filter((a) => a.id !== anakToDelete));
                showNotification('Data anak berhasil dihapus', 'success');
            } else {
                showNotification('Gagal menghapus data anak', 'error');
            }
        } catch (err) {
            showNotification('Terjadi kesalahan saat menghapus data', 'error');
        } finally {
            isDeleting = false;
            anakToDelete = null;
            anakToDeleteName = '';
        }
    }

    const filteredList = derived([anakList, search], ([$anakList, $search]) =>
        $anakList.filter((a) => a.nama.toLowerCase().includes($search.toLowerCase()))
    );

    let idOrangtua: string | null = null;
    $: idOrangtua = $page.url.searchParams.get('id_orangtua');

    async function loadAnak() {
        isLoading = true;
        try {
            let urlAnak = `${BACKEND_URL}/api/anak`;
            if (idOrangtua) urlAnak = `${BACKEND_URL}/api/anak-by-orangtua/${idOrangtua}`;

            const resAnak = await fetch(urlAnak);
            const dataAnak = await resAnak.json();

            anakList.set(
                dataAnak.map((a: any) => ({
                    id: a.id_anak,
                    nama: a.nama,
                    jenis_kelamin: a.jenis_kelamin,
                    tanggal_lahir: a.tanggal_lahir
                }))
            );
        } catch (err) {
            showNotification('Gagal memuat data anak dari server', 'error');
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        loadAnak();
    });

    function tambahAnak() {
        goto(`/anak-kel?id_orangtua=${idOrangtua}`);
    }

    function editAnak(id: number) {
        goto(`/anak-kel?id_anak=${id}&id_orangtua=${idOrangtua}`);
    }

    function kembali() {
        goto('/ortu-dash');
    }

    function getJenisKelaminBadge(jk: string) {
        if (jk === 'L' || jk === 'Laki-laki') return { text: 'Laki-laki', class: 'bg-blue-100 text-blue-700 border-blue-200' };
        if (jk === 'P' || jk === 'Perempuan') return { text: 'Perempuan', class: 'bg-pink-100 text-pink-700 border-pink-200' };
        return { text: '-', class: 'bg-gray-100 text-gray-600' };
    }

    function formatTanggal(tgl: string) {
        if (!tgl) return '-';
        const date = new Date(tgl);
        return new Intl.DateTimeFormat('id-ID', { 
            day: 'numeric', 
            month: 'long', 
            year: 'numeric' 
        }).format(date);
    }
</script>

<section class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <!-- Notification Toast -->
        {#if $notification.message}
            <div
                role="alert"
                class="fixed right-4 top-4 z-50 flex w-full max-w-sm items-center justify-between rounded-xl p-4 shadow-2xl transition-all duration-300 animate-in slide-in-from-top-5"
                class:bg-green-600={$notification.type === 'success'}
                class:bg-red-600={$notification.type === 'error'}
                class:text-white
            >
                <div class="flex items-center gap-3">
                    {#if $notification.type === 'success'}
                        <div class="rounded-full bg-white/20 p-1">
                            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                    {:else}
                        <div class="rounded-full bg-white/20 p-1">
                            <AlertTriangle class="h-5 w-5" />
                        </div>
                    {/if}
                    <span class="text-sm font-medium">{$notification.message}</span>
                </div>
                <button onclick={() => notification.set({ message: '', type: '' })} class="ml-4 rounded-full p-1 hover:bg-white/20 transition">
                    <X class="h-4 w-4" />
                </button>
            </div>
        {/if}

        <!-- Confirmation Modal -->
        <Dialog.Root bind:open={showConfirmModal}>
            <Dialog.Content class="sm:max-w-md">
                <Dialog.Header>
                    <div class="flex items-center gap-3 mb-2">
                        <div class="rounded-full bg-red-100 p-3">
                            <AlertTriangle class="h-6 w-6 text-red-600" />
                        </div>
                        <Dialog.Title class="text-xl">Konfirmasi Hapus</Dialog.Title>
                    </div>
                    <Dialog.Description class="text-base pt-2">
                        Apakah Anda yakin ingin menghapus data <strong class="text-foreground">{anakToDeleteName}</strong>? 
                        <br/><br/>
                        <span class="text-red-600 font-medium">Tindakan ini tidak dapat dibatalkan.</span>
                    </Dialog.Description>
                </Dialog.Header>
                <Dialog.Footer class="gap-2 sm:gap-2">
                    <button 
                        class="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border-2 border-gray-300 bg-white hover:bg-gray-50 h-11 px-6"
                        onclick={() => (showConfirmModal = false)}
                    >
                        Batal
                    </button>
                    <button 
                        class="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all hover:scale-105 focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50 bg-red-600 text-white hover:bg-red-700 h-11 px-6 shadow-lg shadow-red-600/30"
                        onclick={hapusAnak}
                        disabled={isDeleting}
                    >
                        {#if isDeleting}
                            <svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Menghapus...
                        {:else}
                            <Trash class="mr-2 h-4 w-4" />
                            Ya, Hapus
                        {/if}
                    </button>
                </Dialog.Footer>
            </Dialog.Content>
        </Dialog.Root>

        <!-- Back Button -->
        <div class="mb-6">
            <button 
                class="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all hover:bg-white hover:shadow-md border border-gray-200"
                onclick={kembali}
            >
                <ArrowLeft class="h-4 w-4" />
                Kembali ke Dashboard
            </button>
        </div>

        <!-- Main Card -->
        <Card class="shadow-xl border-0 overflow-hidden">
            <div class="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div class="text-white">
                        <div class="flex items-center gap-3 mb-2">
                            <div class="rounded-full bg-white/20 p-2 backdrop-blur-sm">
                                <Users class="h-6 w-6" />
                            </div>
                            <h1 class="text-2xl font-bold">Daftar Anak</h1>
                        </div>
                        <p class="text-blue-100 text-sm">Kelola dan pantau data anak-anak Anda</p>
                    </div>
                    <button 
                        class="inline-flex items-center justify-center gap-2 rounded-lg text-sm font-semibold transition-all hover:scale-105 bg-white text-blue-600 hover:shadow-lg h-11 px-6 shadow-xl"
                        onclick={tambahAnak}
                    >
                        <Plus class="h-5 w-5" />
                        Tambah Anak
                    </button>
                </div>
            </div>

            <CardContent class="p-6">
                <!-- Search Bar -->
                <div class="mb-6">
                    <div class="relative">
                        <Search class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                        <Input 
                            placeholder="Cari nama anak..." 
                            bind:value={$search}
                            class="pl-10 h-12 text-base border-2 focus:border-blue-500 rounded-lg"
                        />
                    </div>
                    {#if $search}
                        <p class="mt-2 text-sm text-gray-600">
                            Menampilkan {$filteredList.length} dari {$anakList.length} anak
                        </p>
                    {/if}
                </div>

                <!-- Loading State -->
                {#if isLoading}
                    <div class="flex flex-col items-center justify-center py-16">
                        <div class="h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent mb-4"></div>
                        <p class="text-gray-600">Memuat data anak...</p>
                    </div>
                {:else}
                    <!-- Table -->
                    <div class="rounded-lg border-2 border-gray-100 overflow-hidden">
                        <Table.Root>
                            <Table.Header>
                                <Table.Row class="bg-gray-50 hover:bg-gray-50">
                                    <Table.Head class="font-semibold text-gray-700">
                                        <div class="flex items-center gap-2">
                                            <Baby class="h-4 w-4" />
                                            Nama Anak
                                        </div>
                                    </Table.Head>
                                    <Table.Head class="font-semibold text-gray-700">Jenis Kelamin</Table.Head>
                                    <Table.Head class="font-semibold text-gray-700">
                                        <div class="flex items-center gap-2">
                                            <Calendar class="h-4 w-4" />
                                            Tanggal Lahir
                                        </div>
                                    </Table.Head>
                                    <Table.Head class="text-center font-semibold text-gray-700">Aksi</Table.Head>
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {#if $filteredList.length > 0}
                                    {#each $filteredList as a (a.id)}
                                        <Table.Row class="hover:bg-blue-50/50 transition-colors">
                                            <Table.Cell class="font-semibold text-gray-900">
                                                <div class="flex items-center gap-3">
                                                    <div class="rounded-full bg-gradient-to-br from-blue-400 to-purple-400 p-2">
                                                        <Baby class="h-4 w-4 text-white" />
                                                    </div>
                                                    {a.nama}
                                                </div>
                                            </Table.Cell>
                                            <Table.Cell>
                                                <Badge variant="outline" class={getJenisKelaminBadge(a.jenis_kelamin).class + ' font-medium'}>
                                                    {getJenisKelaminBadge(a.jenis_kelamin).text}
                                                </Badge>
                                            </Table.Cell>
                                            <Table.Cell class="text-gray-700">
                                                {formatTanggal(a.tanggal_lahir)}
                                            </Table.Cell>
                                            <Table.Cell>
                                                <div class="flex justify-center gap-2">
                                                    <button 
                                                        class="inline-flex items-center justify-center gap-1.5 rounded-lg text-sm font-medium transition-all hover:scale-105 border-2 border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 h-9 px-4"
                                                        onclick={() => editAnak(a.id)}
                                                    >
                                                        <Edit class="h-3.5 w-3.5" />
                                                        Edit
                                                    </button>
                                                    <button 
                                                        class="inline-flex items-center justify-center gap-1.5 rounded-lg text-sm font-medium transition-all hover:scale-105 bg-red-600 text-white hover:bg-red-700 h-9 px-4 shadow-lg shadow-red-600/20"
                                                        onclick={() => konfirmasiHapus(a.id, a.nama)}
                                                        disabled={isDeleting}
                                                    >
                                                        <Trash class="h-3.5 w-3.5" />
                                                        Hapus
                                                    </button>
                                                </div>
                                            </Table.Cell>
                                        </Table.Row>
                                    {/each}
                                {:else}
                                    <Table.Row>
                                        <Table.Cell colspan="4" class="h-40">
                                            <div class="flex flex-col items-center justify-center text-center">
                                                <div class="rounded-full bg-gray-100 p-4 mb-4">
                                                    <Users class="h-8 w-8 text-gray-400" />
                                                </div>
                                                <p class="text-gray-600 font-medium mb-1">
                                                    {$search ? 'Tidak ada hasil pencarian' : 'Belum ada data anak'}
                                                </p>
                                                <p class="text-sm text-gray-500">
                                                    {$search ? 'Coba kata kunci lain' : 'Klik tombol "Tambah Anak" untuk mulai menambahkan data'}
                                                </p>
                                            </div>
                                        </Table.Cell>
                                    </Table.Row>
                                {/if}
                            </Table.Body>
                        </Table.Root>
                    </div>

                    <!-- Stats Footer -->
                    {#if $anakList.length > 0}
                        <div class="mt-4 flex items-center justify-between text-sm">
                            <div class="flex items-center gap-2 text-gray-600">
                                <div class="rounded-full bg-blue-100 px-3 py-1">
                                    <span class="font-semibold text-blue-700">{$anakList.length}</span>
                                </div>
                                <span>total anak terdaftar</span>
                            </div>
                        </div>
                    {/if}
                {/if}
            </CardContent>
        </Card>
    </div>
</section>