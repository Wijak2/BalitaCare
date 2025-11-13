<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';
    import {
        Card,
        CardContent,
        CardDescription,
        CardHeader,
        CardTitle
    } from '$lib/components/ui/card';
    import * as Table from '$lib/components/ui/table';
    import { Skeleton } from '$lib/components/ui/skeleton';
    import { ArrowLeft } from 'lucide-svelte';

    const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

    let id_anak: string | null = null;
    let namaAnak = 'Memuat...'; // Variabel baru untuk nama anak
    let data: any[] = [];
    let loading = true;
    let role: string | null = null;

    onMount(async () => {
        // Pindahkan akses sessionStorage dan window ke dalam onMount
        role = sessionStorage.getItem('role');
        const params = new URLSearchParams(window.location.search);
        id_anak = params.get('id') || sessionStorage.getItem('selected_anak_id') || '1';

        // 1. Ambil nama anak terlebih dahulu
        try {
            const resAnak = await fetch(`${BACKEND_URL}/api/anak/${id_anak}`);
            if (resAnak.ok) {
                const dataAnak = await resAnak.json();
                namaAnak = dataAnak.nama;
            } else {
                namaAnak = 'Anak Tidak Diketahui';
            }
        } catch (err) {
            console.error('Gagal memuat nama anak:', err);
            namaAnak = 'Anak Tidak Diketahui';
        }

        // 2. Ambil data riwayat pengukuran
        try {
            const res = await fetch(`${BACKEND_URL}/api/pengukuran/riwayat/${id_anak}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const json = await res.json();
            data = Array.isArray(json) ? json : [];
        } catch (err) {
            console.error('🔥 Gagal memuat riwayat pengukuran:', err);
        } finally {
            loading = false;
        }
    });

    function kembali() {
        if (typeof window !== 'undefined' && window.history.length > 1) {
            window.history.back();
        } else {
            if (role === 'perawat') {
                const idPerawat = sessionStorage.getItem('id_perawat');
                goto(`/per-dash?id=${idPerawat}`);
            } else {
                const idOrangtua = sessionStorage.getItem('id_orangtua');
                goto(`/ortu-dash?id=${idOrangtua}`);
            }
        }
    }

    function formatTanggal(t: string | null) {
        if (!t) return '-';
        const d = new Date(t);
        if (isNaN(d.getTime())) return t;
        return d.toLocaleString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' });
    }
</script>

<!-- Perubahan: Gunakan wrapper baru -->
<div class="container mx-auto px-4 py-8 sm:py-12">
    <div class="w-full">
        <Card>
            <CardHeader class="flex flex-col items-center text-center space-y-3">
                <!-- Tombol kembali di atas - Perubahan: Gunakan button HTML standar -->
                <div class="w-full flex justify-start">
                    <button 
                        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 gap-2"
                        onclick={kembali}
                    >
                        <ArrowLeft class="h-4 w-4" />
                        Kembali
                    </button>
                </div>

                <!-- Header di tengah -->
                <div>
                    <CardTitle class="text-2xl font-bold">Riwayat Pengukuran</CardTitle>
                    <CardDescription>
                        Menampilkan riwayat untuk:
                        <span class="font-semibold text-foreground">{namaAnak}</span>
                    </CardDescription>
                </div>
            </CardHeader>

            <CardContent>
                {#if loading}
                    <!-- Tampilkan skeleton saat loading -->
                    <div class="space-y-2">
                        {#each Array(5) as _}
                            <div class="flex items-center space-x-4">
                                <Skeleton class="h-12 w-[150px]" />
                                <Skeleton class="h-12 w-[150px]" />
                                <Skeleton class="h-12 w-[150px]" />
                                <Skeleton class="h-12 w-[150px]" />
                                <Skeleton class="h-12 w-[200px]" />
                            </div>
                        {/each}
                    </div>
                {:else if data && data.length > 0}
                    <!-- Tampilkan tabel jika ada data -->
                    <Table.Root>
                        <Table.Header>
                            <Table.Row>
                                <Table.Head>Lingkar Kepala (cm)</Table.Head>
                                <Table.Head>Lingkar Lengan (cm)</Table.Head>
                                <Table.Head>Berat Badan (kg)</Table.Head>
                                <Table.Head>Tinggi Badan (cm)</Table.Head>
                                <Table.Head>Tanggal</Table.Head>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {#each data as item, i}
                                <Table.Row>
                                    <Table.Cell class="font-medium">{item.lingkar_kepala ?? '-'}</Table.Cell>
                                    <Table.Cell>{item.lingkar_lengan ?? '-'}</Table.Cell>
                                    <Table.Cell>{item.berat_badan ?? '-'}</Table.Cell>
                                    <Table.Cell>{item.tinggi_badan ?? '-'}</Table.Cell>
                                    <Table.Cell>{formatTanggal(item.tanggal ?? null)}</Table.Cell>
                                </Table.Row>
                            {/each}
                        </Table.Body>
                    </Table.Root>
                {:else}
                    <!-- Tampilkan pesan jika tidak ada data -->
                    <div class="flex flex-col items-center justify-center py-12 text-center">
                        <p class="text-muted-foreground">Belum ada data pengukuran untuk anak ini.</p>
                    </div>
                {/if}
            </CardContent>
        </Card>

        <!-- Perubahan: Pindahkan tombol kembali ke bawah card -->
        <div class="mt-6 flex justify-center"></div>
    </div>
</div>