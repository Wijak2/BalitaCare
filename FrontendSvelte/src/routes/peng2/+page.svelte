<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import { goto } from '$app/navigation';
  import { writable } from 'svelte/store';
  import { PUBLIC_BACKEND_URL } from "$env/static/public";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  import { Separator } from "$lib/components/ui/separator";
  import { Brain, Ruler, Activity, Save, ArrowLeft, Eye, Wifi, WifiOff, User, CheckCircle2, AlertCircle, Scale, TrendingUp } from "lucide-svelte";

  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

  const notification = writable<{ message: string; type: 'success' | 'error' | '' }>({
    message: '',
    type: ''
  });

  function showNotification(message: string, type: 'success' | 'error') {
    notification.set({ message, type });
    setTimeout(() => {
      notification.set({ message: '', type: '' });
    }, 3000);
  }

  let idAnak = '';
  let idPengukuran = '';
  let activeForm = 'kepala';
  let iotKepala: number | null = null;
  let iotLengan: number | null = null;
  let tinggiBadan = '';
  let beratBadan = '';
  let anakNama = '';
  let isConnected = false;
  let isSaving = false;
  let isProcessing = false;

  let iotInterval: any = null;

  onMount(async () => {
    const currentPage = get(page);
    idAnak = currentPage.url.searchParams.get('id_anak') || '';
    idPengukuran = currentPage.url.searchParams.get('id_pengukuran') || '';

    if (idAnak) {
      try {
        const res = await fetch(`${BACKEND_URL}/api/anak/${idAnak}`);
        const data = await res.json();
        anakNama = data.nama || '(Nama tidak ditemukan)';
      } catch (err) {
        console.error('Gagal ambil data anak:', err);
      }
    }

    await loadLatestIoT();
    iotInterval = setInterval(loadLatestIoT, 2000);
  });

  onDestroy(() => {
    if (iotInterval) clearInterval(iotInterval);
  });

  async function loadLatestIoT() {
    try {
      const res = await fetch(`${BACKEND_URL}/latest-json`);
      const data = await res.json();

      if (data && data.nilai !== undefined && data.nilai !== null) {
        iotKepala = parseFloat(data.nilai);
        iotLengan = parseFloat(data.nilai);
        isConnected = true;
      } else {
        isConnected = false;
      }
    } catch (err) {
      console.error('Gagal ambil data IoT:', err);
      iotKepala = null;
      iotLengan = null;
      isConnected = false;
    }
  }

  async function saveData() {
    if (!idAnak || !idPengukuran) {
      showNotification('ID anak atau ID pengukuran tidak ditemukan', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('id_anak', idAnak);
    formData.append('id_pengukuran', idPengukuran);

    if (activeForm === 'kepala') {
      if (iotKepala === null) {
        showNotification('Belum ada data IoT untuk lingkar kepala', 'error');
        return;
      }
      formData.append('jenis', 'kepala');
      formData.append('nilai', iotKepala.toString());
    } else if (activeForm === 'lengan') {
      if (iotLengan === null) {
        showNotification('Belum ada data IoT untuk lingkar lengan', 'error');
        return;
      }
      formData.append('jenis', 'lengan');
      formData.append('nilai', iotLengan.toString());
    } else {
      if (!tinggiBadan || !beratBadan) {
        showNotification('Tinggi dan berat badan harus diisi', 'error');
        return;
      }
      formData.append('jenis', 'bbtb');
      formData.append('tinggi_badan', tinggiBadan);
      formData.append('berat_badan', beratBadan);
    }

    isSaving = true;
    try {
      const res = await fetch(`${BACKEND_URL}/save-current`, {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        showNotification('Data berhasil disimpan', 'success');
      } else {
        showNotification('Gagal menyimpan data', 'error');
      }
    } catch (err) {
      console.error(err);
      showNotification('Gagal menyimpan data', 'error');
    } finally {
      isSaving = false;
    }
  }

  async function processAnalisis() {
    if (!idPengukuran) {
      showNotification('ID pengukuran tidak ditemukan', 'error');
      return;
    }

    isProcessing = true;
    try {
      const res = await fetch(`${BACKEND_URL}/api/process/${idPengukuran}`, {
        method: 'POST'
      });
      const data = await res.json();

      if (!res.ok) {
        showNotification(data.error || 'Gagal memproses analisis', 'error');
        return;
      }

      showNotification('Analisis berhasil diproses', 'success');
      console.log('Hasil analisis:', data);

    } catch (err) {
      console.error(err);
      showNotification('Terjadi kesalahan saat memproses analisis', 'error');
    } finally {
      isProcessing = false;
    }
  }
</script>

{#if $notification.message}
  <div
    class="fixed top-4 right-4 z-50 rounded-lg px-6 py-4 text-white shadow-xl transition-all duration-300 animate-in slide-in-from-top-5"
    class:bg-green-600={$notification.type === 'success'}
    class:bg-red-600={$notification.type === 'error'}
  >
    <div class="flex items-center gap-2">
      {#if $notification.type === 'success'}
        <CheckCircle2 class="h-4 w-4" />
      {:else}
        <AlertCircle class="h-4 w-4" />
      {/if}
      <div class="text-sm font-medium">{$notification.message}</div>
    </div>
  </div>
{/if}

<div class="container mx-auto py-8 px-4 max-w-6xl">
  <!-- Header Card -->
  <Card class="mb-6">
    <CardHeader>
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <div class="rounded-full bg-primary/10 p-2">
              <Ruler class="h-6 w-6 text-primary" />
            </div>
            <Badge variant="outline" class="text-xs">Step 2 of 2</Badge>
          </div>
          <CardTitle class="text-2xl font-bold mb-1">Pengukuran Balita</CardTitle>
          <CardDescription class="flex items-center gap-2">
            <User class="h-4 w-4" />
            <span><strong>{anakNama}</strong></span>
          </CardDescription>
        </div>
        <div class="flex items-center gap-2 px-4 py-2 rounded-lg border {isConnected ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}">
          {#if isConnected}
            <Wifi class="h-5 w-5 text-green-600" />
            <div>
              <p class="text-xs text-green-600 font-medium">Perangkat Terhubung</p>
              <p class="text-xs text-green-500">Siap mengukur</p>
            </div>
          {:else}
            <WifiOff class="h-5 w-5 text-gray-400" />
            <div>
              <p class="text-xs text-gray-600 font-medium">Tidak Terhubung</p>
              <p class="text-xs text-gray-400">Cek koneksi perangkat</p>
            </div>
          {/if}
        </div>
      </div>
    </CardHeader>
  </Card>

  <!-- Main Content -->
  <div class="grid gap-6 lg:grid-cols-3">
    <!-- Measurement Cards -->
    <div class="lg:col-span-2 space-y-4">
      <!-- Lingkar Kepala -->
      <Card class="overflow-hidden transition-all {activeForm === 'kepala' ? 'ring-2 ring-blue-500' : ''}">
        <button
          onclick={() => activeForm = 'kepala'}
          class="w-full text-left"
        >
          <CardHeader class="pb-3 {activeForm === 'kepala' ? 'bg-blue-50' : ''}">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="rounded-full bg-blue-100 p-3">
                  <Brain class="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle class="text-lg">Lingkar Kepala</CardTitle>
                  <CardDescription class="text-xs">Ukur keliling kepala balita</CardDescription>
                </div>
              </div>
              {#if activeForm === 'kepala'}
                <Badge class="bg-blue-600">Aktif</Badge>
              {/if}
            </div>
          </CardHeader>
        </button>
        
        {#if activeForm === 'kepala'}
          <CardContent class="pt-6">
            <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-8 border-2 border-blue-200">
              <div class="text-center space-y-4">
                {#if iotKepala !== null}
                  <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-600 mb-2 animate-pulse">
                    <Activity class="h-10 w-10 text-white" />
                  </div>
                  <div>
                    <p class="text-sm text-blue-600 font-medium mb-1">Hasil Pengukuran</p>
                    <div class="flex items-baseline justify-center gap-2">
                      <span class="text-6xl font-bold text-blue-700">{iotKepala}</span>
                      <span class="text-2xl font-semibold text-blue-600">cm</span>
                    </div>
                  </div>
                  <p class="text-xs text-blue-700 bg-blue-100 inline-block px-3 py-1 rounded-full">✓ Data siap disimpan</p>
                {:else}
                  <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-200 mb-2">
                    <div class="h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
                  </div>
                  <p class="text-blue-600 font-medium">Menunggu data dari alat ukur...</p>
                  <p class="text-xs text-blue-500">Pastikan perangkat sudah terpasang dengan benar</p>
                {/if}
              </div>
            </div>
          </CardContent>
        {/if}
      </Card>

      <!-- Lingkar Lengan -->
      <Card class="overflow-hidden transition-all {activeForm === 'lengan' ? 'ring-2 ring-green-500' : ''}">
        <button
          onclick={() => activeForm = 'lengan'}
          class="w-full text-left"
        >
          <CardHeader class="pb-3 {activeForm === 'lengan' ? 'bg-green-50' : ''}">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="rounded-full bg-green-100 p-3">
                  <Activity class="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <CardTitle class="text-lg">Lingkar Lengan Atas</CardTitle>
                  <CardDescription class="text-xs">Ukur tengah lengan atas (antara bahu dan siku)</CardDescription>
                </div>
              </div>
              {#if activeForm === 'lengan'}
                <Badge class="bg-green-600">Aktif</Badge>
              {/if}
            </div>
          </CardHeader>
        </button>
        
        {#if activeForm === 'lengan'}
          <CardContent class="pt-6">
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-8 border-2 border-green-200">
              <div class="text-center space-y-4">
                {#if iotLengan !== null}
                  <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-600 mb-2 animate-pulse">
                    <Activity class="h-10 w-10 text-white" />
                  </div>
                  <div>
                    <p class="text-sm text-green-600 font-medium mb-1">Hasil Pengukuran</p>
                    <div class="flex items-baseline justify-center gap-2">
                      <span class="text-6xl font-bold text-green-700">{iotLengan}</span>
                      <span class="text-2xl font-semibold text-green-600">cm</span>
                    </div>
                  </div>
                  <p class="text-xs text-green-700 bg-green-100 inline-block px-3 py-1 rounded-full">✓ Data siap disimpan</p>
                {:else}
                  <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-200 mb-2">
                    <div class="h-10 w-10 animate-spin rounded-full border-4 border-green-600 border-t-transparent"></div>
                  </div>
                  <p class="text-green-600 font-medium">Menunggu data dari alat ukur...</p>
                  <p class="text-xs text-green-500">Pastikan perangkat sudah terpasang dengan benar</p>
                {/if}
              </div>
            </div>
          </CardContent>
        {/if}
      </Card>

      <!-- Berat & Tinggi Badan -->
      <Card class="overflow-hidden transition-all {activeForm === 'bbtb' ? 'ring-2 ring-purple-500' : ''}">
        <button
          onclick={() => activeForm = 'bbtb'}
          class="w-full text-left"
        >
          <CardHeader class="pb-3 {activeForm === 'bbtb' ? 'bg-purple-50' : ''}">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="rounded-full bg-purple-100 p-3">
                  <Scale class="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle class="text-lg">Berat & Tinggi Badan</CardTitle>
                  <CardDescription class="text-xs">Input manual berat dan tinggi balita</CardDescription>
                </div>
              </div>
              {#if activeForm === 'bbtb'}
                <Badge class="bg-purple-600">Aktif</Badge>
              {/if}
            </div>
          </CardHeader>
        </button>
        
        {#if activeForm === 'bbtb'}
          <CardContent class="pt-6">
            <div class="space-y-4">
              <div class="grid gap-4 sm:grid-cols-2">
                <div class="space-y-2">
                  <Label for="berat" class="text-base font-semibold flex items-center gap-2">
                    <Scale class="h-4 w-4" />
                    Berat Badan
                  </Label>
                  <div class="relative">
                    <Input
                      id="berat"
                      type="number"
                      bind:value={beratBadan}
                      placeholder="12.5"
                      step="0.1"
                      class="pr-12 h-12 text-lg"
                    />
                    <span class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground font-medium">kg</span>
                  </div>
                  <p class="text-xs text-muted-foreground">Contoh: 12.5 kg</p>
                </div>

                <div class="space-y-2">
                  <Label for="tinggi" class="text-base font-semibold flex items-center gap-2">
                    <TrendingUp class="h-4 w-4" />
                    Tinggi Badan
                  </Label>
                  <div class="relative">
                    <Input
                      id="tinggi"
                      type="number"
                      bind:value={tinggiBadan}
                      placeholder="85.5"
                      step="0.1"
                      class="pr-12 h-12 text-lg"
                    />
                    <span class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground font-medium">cm</span>
                  </div>
                  <p class="text-xs text-muted-foreground">Contoh: 85.5 cm</p>
                </div>
              </div>

              <div class="rounded-lg bg-purple-50 border border-purple-200 p-4">
                <p class="text-sm text-purple-800 flex items-start gap-2">
                  <AlertCircle class="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>Gunakan timbangan dan pengukur tinggi yang sudah dikalibrasi untuk hasil akurat</span>
                </p>
              </div>
            </div>
          </CardContent>
        {/if}
      </Card>
    </div>

    <!-- Action Panel -->
    <div class="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle class="text-lg">Langkah Selanjutnya</CardTitle>
          <CardDescription class="text-xs">Simpan data lalu proses analisis</CardDescription>
        </CardHeader>
        <CardContent class="space-y-3">
          <Button
            onclick={saveData}
            class="w-full bg-green-600 hover:bg-green-700 h-12"
            disabled={isSaving}
          >
            {#if isSaving}
              <div class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
              Menyimpan...
            {:else}
              <Save class="mr-2 h-5 w-5" />
              Simpan Data
            {/if}
          </Button>

          <Separator />

          <Button
            onclick={processAnalisis}
            class="w-full h-12"
            variant="default"
            disabled={isProcessing}
          >
            {#if isProcessing}
              <div class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
              Memproses...
            {:else}
              <Brain class="mr-2 h-5 w-5" />
              Analisis Gizi
            {/if}
          </Button>

          <div class="rounded-lg bg-blue-50 border border-blue-200 p-3 text-xs text-blue-800">
            <strong>Tips:</strong> Simpan setiap pengukuran sebelum pindah ke pengukuran lain
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-lg">Navigasi</CardTitle>
        </CardHeader>
        <CardContent class="space-y-2">
          <Button
            onclick={() => goto(`/balita-det?id=${idAnak}&role=perawat`)}
            variant="outline"
            class="w-full justify-start"
          >
            <Eye class="mr-2 h-4 w-4" />
            Lihat Detail Lengkap
          </Button>

          <Button
            onclick={() => goto(`/peng1?id_anak=${idAnak}`)}
            variant="outline"
            class="w-full justify-start"
          >
            <ArrowLeft class="mr-2 h-4 w-4" />
            Kembali ke Step 1
          </Button>
        </CardContent>
      </Card>
    </div>
  </div>
</div>