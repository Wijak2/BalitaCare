<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { writable } from "svelte/store";
    import { PUBLIC_BACKEND_URL } from "$env/static/public";
    import { Button } from "$lib/components/ui/button";
    import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    // Tambahkan komponen Dialog
    import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "$lib/components/ui/dialog";

    const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

    // Ganti sistem notifikasi dengan Dialog
    const isAlertOpen = writable(false);
    let alertMessage = '';

    function showAlert(message: string) {
        alertMessage = message;
        isAlertOpen.set(true);
    }

    let idAnak: string | null = null;
    let idOrangtua: string | null = null;
    let nama = '';
    let jenis_kelamin = '';
    let tanggal_lahir = '';
    let role: string | null = null;

    $: idAnak = $page.url.searchParams.get('id_anak');

    onMount(async () => {
        role = sessionStorage.getItem('role');
        idOrangtua =
            $page.url.searchParams.get('id_orangtua') ||
            sessionStorage.getItem('selected_orangtua');

        if (idAnak) {
            try {
                const res = await fetch(`${BACKEND_URL}/api/anak/${idAnak}`);
                if (res.ok) {
                    const data = await res.json();
                    nama = data.nama;
                    jenis_kelamin = data.jenis_kelamin;
                    tanggal_lahir = data.tanggal_lahir;
                } else {
                    showAlert('Gagal mengambil data anak');
                }
            } catch (err) {
                showAlert('Terjadi kesalahan');
            }
        }
    });

    function kembali() {
        if (typeof window !== 'undefined' && window.history.length > 1) {
            window.history.back();
        } else {
            if (role === 'perawat') {
                goto('/dashboard-perawat');
            } else {
                goto('/dashboard-orangtua');
            }
        }
    }

    async function submitForm() {
        if (!idOrangtua) {
            showAlert('ID orang tua tidak ditemukan');
            return;
        }

        const formData = new FormData();
        formData.append('nama', nama);
        formData.append('jenis_kelamin', jenis_kelamin);
        formData.append('tanggal_lahir', tanggal_lahir);

        try {
            let url = `${BACKEND_URL}/anak/add-by-orangtua/${idOrangtua}`;
            if (idAnak) {
                url = `${BACKEND_URL}/anak/edit/${idAnak}`;
            }

            const res = await fetch(url, {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                showAlert('✅ Data berhasil disimpan');
                setTimeout(() => {
                    kembali();
                }, 1500); // Tunggu sebentar agar pengguna bisa membaca pesan
            } else {
                const text = await res.text();
                showAlert('Gagal menyimpan data: ' + text);
            }
        } catch (err) {
            showAlert('Terjadi kesalahan saat menyimpan data');
        }
    }
</script>

<section class="container mx-auto flex min-h-screen items-center justify-center p-4">
    <div class="w-full max-w-md">
        <Card class="shadow-xl">
            <CardHeader class="space-y-1 text-center">
                <CardTitle class="text-2xl font-bold">
                    {idAnak ? 'Edit Data Anak' : 'Tambah Data Anak'}
                </CardTitle>
                <CardDescription>
                    {idAnak ? 'Perbarui informasi data anak' : 'Isi informasi untuk menambahkan anak baru'}
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form on:submit|preventDefault={submitForm} class="space-y-5">
                    <div class="space-y-2">
                        <Label for="nama">Nama Lengkap</Label>
                        <Input
                            id="nama"
                            type="text"
                            bind:value={nama}
                            placeholder="Masukkan nama anak"
                            required
                        />
                    </div>

                    <div class="space-y-2">
                        <Label for="jenis_kelamin">Jenis Kelamin</Label>
                        <select
                            id="jenis_kelamin"
                            bind:value={jenis_kelamin}
                            required
                            class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <option value="">-- Pilih Jenis Kelamin --</option>
                            <option value="Laki-laki">Laki-laki</option>
                            <option value="Perempuan">Perempuan</option>
                        </select>
                    </div>

                    <div class="space-y-2">
                        <Label for="tanggal_lahir">Tanggal Lahir</Label>
                        <Input
                            id="tanggal_lahir"
                            type="date"
                            bind:value={tanggal_lahir}
                            required
                        />
                    </div>

                    <div class="flex justify-between pt-4">
                        <Button variant="outline" type="button" onclick={kembali}>
                            Batal
                        </Button>
                        <Button type="submit">
                            {idAnak ? 'Perbarui' : 'Simpan'}
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    </div>

    <!-- Dialog/Alert Baru -->
    <Dialog bind:open={$isAlertOpen}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Notifikasi</DialogTitle>
                <DialogDescription>
                    {alertMessage}
                </DialogDescription>
            </DialogHeader>
            <DialogFooter>
                <Button on:click={() => isAlertOpen.set(false)}>OK</Button>
            </DialogFooter>
        </DialogContent>
    </Dialog>
</section>