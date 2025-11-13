<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { PUBLIC_BACKEND_URL } from "$env/static/public";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { Separator } from "$lib/components/ui/separator";
  import { Badge } from "$lib/components/ui/badge";
  import { CalendarIcon, UserIcon, ClipboardList, ArrowRight, ArrowLeft, Activity, AlertCircle, CheckCircle2, Clock, Sparkles, Baby, PlayCircle } from "lucide-svelte";

  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

  let daftarAnak: any[] = [];
  let selectedAnak = "";
  let daftarPengukuran: any[] = [];
  let tanggalPengukuran = "";
  let selectedPengukuran = "";
  let message = "";
  let isExisting = false;
  let isLoading = false;
  let isLoadingHistory = false;

  onMount(async () => {
    const params = new URLSearchParams(window.location.search);
    const idAnakUrl = params.get("id_anak");

    isLoading = true;
    try {
      const res = await fetch(`${BACKEND_URL}/api/anak`);
      daftarAnak = await res.json();
    } catch (err) {
      alert("Gagal memuat daftar anak");
      return;
    } finally {
      isLoading = false;
    }

    if (idAnakUrl) {
      selectedAnak = String(idAnakUrl);
      await getPengukuranByAnak();
    }

    // Set tanggal hari ini secara default
    const today = new Date().toISOString().split('T')[0];
    tanggalPengukuran = today;
  });

  async function getPengukuranByAnak() {
    if (!selectedAnak) return;
    isLoadingHistory = true;
    try {
      const res = await fetch(`${BACKEND_URL}/api/pengukuran-by-anak/${selectedAnak}`);
      daftarPengukuran = await res.json();
    } catch (err) {
      alert("Gagal memuat riwayat pengukuran");
    } finally {
      isLoadingHistory = false;
    }
  }

  async function mulaiPengukuran() {
    if (!selectedAnak || !tanggalPengukuran) {
      alert("Pilih anak dan tanggal terlebih dahulu!");
      return;
    }

    const formData = new FormData();
    formData.append("id_anak", selectedAnak);
    formData.append("tanggal_pengukuran", tanggalPengukuran);

    isLoading = true;
    try {
      const res = await fetch(`${BACKEND_URL}/api/create-pengukuran`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      message = data.message;
      selectedPengukuran = data.id_pengukuran;
      isExisting = data.message.includes("sudah ada");
      await getPengukuranByAnak();
    } catch (err) {
      alert("Gagal membuat pengukuran baru");
    } finally {
      isLoading = false;
    }
  }

  function lanjutStep2() {
    if (!selectedAnak || !selectedPengukuran) {
      alert("Silakan buat atau pilih pengukuran terlebih dahulu!");
      return;
    }
    goto(`/peng2?id_anak=${selectedAnak}&id_pengukuran=${selectedPengukuran}`);
  }

  function kembaliDashboard() {
    goto(`/per-dash`);
  }

  function getSelectedAnakName() {
    const anak = daftarAnak.find(a => String(a.id_anak) === selectedAnak);
    return anak ? anak.nama : '';
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

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 py-8 px-4">
  <div class="container mx-auto flex items-center justify-center">
    <div class="w-full max-w-3xl">
      <!-- Header Card -->
      <div class="mb-6 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-600 p-6 text-white shadow-2xl">
        <div class="flex items-center gap-4 mb-3">
          <div class="rounded-full bg-white/20 p-3 backdrop-blur-sm">
            <Activity class="h-8 w-8" />
          </div>
          <div>
            <div class="flex items-center gap-2 mb-1">
              <Badge variant="secondary" class="bg-white/20 text-white border-white/30">
                Langkah 1 dari 2
              </Badge>
            </div>
            <h1 class="text-3xl font-bold">Mulai Pengukuran Balita</h1>
          </div>
        </div>
        <p class="text-blue-100">
          Pilih data anak dan tentukan tanggal pengukuran untuk memulai proses antropometri
        </p>
      </div>

      <!-- Main Card -->
      <Card class="shadow-2xl border-0">
        <CardContent class="p-8 space-y-8">
          <!-- Step 1: Pilih Anak -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <div class="rounded-full bg-blue-100 p-2">
                <Baby class="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 class="font-semibold text-lg">Pilih Anak</h3>
                <p class="text-sm text-muted-foreground">Pilih anak yang akan diukur</p>
              </div>
            </div>
            
            <select
              id="anak-select"
              bind:value={selectedAnak}
              onchange={() => getPengukuranByAnak()}
              class="flex h-14 w-full items-center justify-between rounded-xl border-2 border-input bg-white px-4 py-2 text-base font-medium ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50 transition-all hover:border-blue-300"
            >
              <option value="">-- Pilih Anak --</option>
              {#each daftarAnak as anak}
                <option value={String(anak.id_anak)}>{anak.nama}</option>
              {/each}
            </select>

            {#if selectedAnak && getSelectedAnakName()}
              <div class="flex items-center gap-2 text-sm text-green-700 bg-green-50 px-4 py-2 rounded-lg border border-green-200">
                <CheckCircle2 class="h-4 w-4" />
                <span>Anak terpilih: <strong>{getSelectedAnakName()}</strong></span>
              </div>
            {/if}
          </div>

          <Separator class="my-6" />

          <!-- Step 2: Pilih Tanggal -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <div class="rounded-full bg-purple-100 p-2">
                <CalendarIcon class="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <h3 class="font-semibold text-lg">Tanggal Pengukuran</h3>
                <p class="text-sm text-muted-foreground">Pilih tanggal pelaksanaan pengukuran</p>
              </div>
            </div>
            
            <Input
              id="tanggal"
              type="date"
              bind:value={tanggalPengukuran}
              class="h-14 text-base border-2 rounded-xl focus:border-purple-500"
            />
          </div>

          <Separator class="my-6" />

          <!-- Action Button -->
          <Button
            onclick={mulaiPengukuran}
            class="w-full h-14 text-lg font-semibold bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-xl shadow-blue-600/30 transition-all hover:scale-105"
            disabled={isLoading || !selectedAnak || !tanggalPengukuran}
          >
            {#if isLoading}
              <div class="mr-2 h-5 w-5 animate-spin rounded-full border-3 border-current border-t-transparent"></div>
              Memproses...
            {:else}
              <PlayCircle class="mr-2 h-5 w-5" />
              Mulai Pengukuran Sekarang
            {/if}
          </Button>

          <!-- Status Message -->
          {#if message}
            <Alert class={isExisting ? "border-2 border-amber-400 bg-amber-50" : "border-2 border-green-400 bg-green-50"}>
              <div class="flex items-start gap-3">
                {#if isExisting}
                  <div class="rounded-full bg-amber-100 p-2">
                    <AlertCircle class="h-5 w-5 text-amber-600" />
                  </div>
                  <div>
                    <p class="font-semibold text-amber-900 mb-1">Pengukuran Sudah Ada</p>
                    <AlertDescription class="text-amber-800">
                      {message}
                    </AlertDescription>
                  </div>
                {:else}
                  <div class="rounded-full bg-green-100 p-2">
                    <CheckCircle2 class="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p class="font-semibold text-green-900 mb-1">Berhasil!</p>
                    <AlertDescription class="text-green-800">
                      {message}
                    </AlertDescription>
                  </div>
                {/if}
              </div>
            </Alert>
          {/if}

          <!-- Next Button -->
          {#if selectedPengukuran}
            <Button
              onclick={lanjutStep2}
              class="w-full h-14 text-lg font-semibold bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-xl shadow-green-600/30 transition-all hover:scale-105"
            >
              <Sparkles class="mr-2 h-5 w-5" />
              Lanjut ke Pengukuran
              <ArrowRight class="ml-2 h-5 w-5" />
            </Button>
          {/if}
        </CardContent>
      </Card>

      <!-- History Card -->
      <Card class="mt-6 shadow-xl border-0">
        <CardHeader>
          <div class="flex items-center gap-3">
            <div class="rounded-full bg-indigo-100 p-2">
              <ClipboardList class="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <CardTitle>Riwayat Pengukuran</CardTitle>
              <CardDescription>Daftar pengukuran yang pernah dilakukan</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {#if isLoadingHistory}
            <div class="flex flex-col items-center justify-center py-12">
              <div class="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-3"></div>
              <p class="text-sm text-muted-foreground">Memuat riwayat...</p>
            </div>
          {:else if daftarPengukuran.length > 0}
            <div class="space-y-3">
              {#each daftarPengukuran as p}
                <div class="flex items-center justify-between rounded-xl border-2 bg-gradient-to-r from-indigo-50 to-purple-50 p-4 transition-all hover:shadow-lg hover:scale-[1.02]">
                  <div class="flex items-center gap-4">
                    <div class="rounded-full bg-indigo-600 p-3">
                      <Clock class="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p class="font-semibold text-base">{formatTanggal(p.tanggal)}</p>
                      <p class="text-sm text-muted-foreground">ID: {p.id_pengukuran}</p>
                    </div>
                  </div>
                  <Badge class="bg-green-100 text-green-700 border-green-300 px-3 py-1">
                    <CheckCircle2 class="h-3 w-3 mr-1" />
                    Tersimpan
                  </Badge>
                </div>
              {/each}
            </div>
          {:else}
            <div class="rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 p-12 text-center">
              <div class="rounded-full bg-gray-100 p-4 inline-block mb-4">
                <ClipboardList class="h-10 w-10 text-gray-400" />
              </div>
              <p class="text-base font-medium text-gray-700 mb-1">
                {selectedAnak ? "Belum ada riwayat pengukuran" : "Pilih anak terlebih dahulu"}
              </p>
              <p class="text-sm text-muted-foreground">
                {selectedAnak ? "Mulai pengukuran pertama untuk anak ini" : "Riwayat akan muncul setelah Anda memilih anak"}
              </p>
            </div>
          {/if}
        </CardContent>
      </Card>

      <!-- Back Button -->
      <div class="mt-6">
        <Button
          onclick={kembaliDashboard}
          variant="outline"
          class="w-full h-12 text-base border-2 hover:bg-gray-50"
        >
          <ArrowLeft class="mr-2 h-5 w-5" />
          Kembali ke Dashboard
        </Button>
      </div>
    </div>
  </div>
</div>