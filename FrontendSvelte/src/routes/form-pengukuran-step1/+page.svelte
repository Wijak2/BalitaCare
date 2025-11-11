<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { PUBLIC_BACKEND_URL } from "$env/static/public";

  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

  let daftarAnak: any[] = [];
  let selectedAnak = "";
  let daftarPengukuran: any[] = [];
  let tanggalPengukuran = "";
  let selectedPengukuran = "";
  let message = "";
  let isExisting = false;

  let idPerawat: string | null = null;

  function decodeJWT(token: string) {
    try {
      return JSON.parse(atob(token.split(".")[1]));
    } catch {
      return null;
    }
  }

  onMount(async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      alert("Anda belum login!");
      goto("/login");
      return;
    }

    const payload = decodeJWT(token);
    idPerawat = payload?.user_id || null;

    if (!idPerawat) {
      alert("ID perawat tidak ditemukan! Login ulang.");
      goto("/login");
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const idAnakUrl = params.get("id_anak");

    const res = await fetch(`${BACKEND_URL}/api/anak`, {
      headers: {
        Authorization: "Bearer " + token
      }
    });

    daftarAnak = await res.json();

    if (idAnakUrl) {
      selectedAnak = String(idAnakUrl);
      await getPengukuranByAnak();
    }
  });

  async function getPengukuranByAnak() {
    const token = localStorage.getItem("token");
    if (!selectedAnak || !token) return;

    const res = await fetch(`${BACKEND_URL}/api/pengukuran-by-anak/${selectedAnak}`, {
      headers: {
        Authorization: "Bearer " + token
      }
    });

    daftarPengukuran = await res.json();
  }

  async function mulaiPengukuran() {
    const token = localStorage.getItem("token");
    if (!token) return;

    if (!selectedAnak || !tanggalPengukuran) {
      alert("Pilih anak dan tanggal terlebih dahulu!");
      return;
    }

    const formData = new FormData();
    formData.append("id_anak", selectedAnak);
    formData.append("tanggal_pengukuran", tanggalPengukuran);

    const res = await fetch(`${BACKEND_URL}/api/create-pengukuran`, {
      method: "POST",
      headers: { Authorization: "Bearer " + token },
      body: formData
    });

    const data = await res.json();
    message = data.message;
    selectedPengukuran = data.id_pengukuran;
    isExisting = data.message.includes("sudah ada");

    await getPengukuranByAnak();
  }

  function lanjutStep2() {
    if (!selectedAnak || !selectedPengukuran) {
      alert("Silakan buat atau pilih pengukuran terlebih dahulu!");
      return;
    }
    goto(`/form-pengukuran-step2?id_anak=${selectedAnak}&id_pengukuran=${selectedPengukuran}`);
  }

  function kembaliDashboard() {
    if (!idPerawat) {
      alert("ID perawat tidak ditemukan!");
      return;
    }
    goto(`/dashboard-perawat`);
  }
</script>

<div class="page-wrapper flex items-center justify-center">
  <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-lg space-y-6 border border-blue-100">
    <h2 class="text-2xl font-bold text-center text-sky-700">📏 Mulai Pengukuran Balita</h2>
    <p class="text-center text-gray-600 text-sm">
      Pilih anak dan tanggal pengukuran untuk memulai proses.
    </p>

    <!-- Pilih Anak -->
    <div>
      <label class="block mb-1 font-semibold text-gray-700">Pilih Anak:</label>
      <select
        bind:value={selectedAnak}
        on:change={getPengukuranByAnak}
        class="border border-gray-300 rounded-lg p-2.5 w-full focus:ring-2 focus:ring-sky-400 focus:outline-none"
      >
        <option value="">-- Pilih Anak --</option>
        {#each daftarAnak as anak}
          <option value={String(anak.id_anak)}>{anak.nama}</option>
        {/each}
      </select>
    </div>

    <!-- Pilih Tanggal -->
    <div>
      <label class="block mb-1 font-semibold text-gray-700">Tanggal Pengukuran:</label>
      <input
        type="date"
        bind:value={tanggalPengukuran}
        class="border border-gray-300 rounded-lg p-2.5 w-full focus:ring-2 focus:ring-sky-400 focus:outline-none"
      />
    </div>

    <!-- Tombol -->
    <div class="flex flex-col gap-3">
      <button
        on:click={mulaiPengukuran}
        class="bg-sky-500 hover:bg-sky-600 transition text-white font-semibold rounded-lg px-5 py-2.5 w-full shadow"
      >
        Mulai Pengukuran
      </button>

      {#if selectedPengukuran}
        <button
          on:click={lanjutStep2}
          class="bg-green-500 hover:bg-green-600 transition text-white font-semibold rounded-lg px-5 py-2.5 w-full shadow"
        >
          Lanjut ke Form Pengukuran
        </button>
      {/if}

      <button
        on:click={kembaliDashboard}
        class="bg-gray-200 hover:bg-gray-300 transition text-gray-800 font-medium rounded-lg px-5 py-2.5 w-full shadow"
      >
        Kembali ke Dashboard
      </button>
    </div>

    <!-- Pesan -->
    {#if message}
      <div
        class={`p-3 rounded-lg text-center ${
          isExisting ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"
        }`}
      >
        {message}
      </div>
    {/if}

    <!-- Riwayat -->
    <div class="bg-sky-50 p-4 rounded-lg border border-sky-100">
      <h3 class="font-semibold text-sky-700 mb-2">📋 Riwayat Pengukuran:</h3>
      {#if daftarPengukuran.length > 0}
        <ul class="list-disc pl-5 space-y-1 text-gray-700 text-sm">
          {#each daftarPengukuran as p}
            <li>{p.tanggal} — <span class="font-medium text-sky-600">ID: {p.id_pengukuran}</span></li>
          {/each}
        </ul>
      {:else}
        <p class="text-gray-500 text-sm italic">Belum ada riwayat pengukuran.</p>
      {/if}
    </div>
  </div>
</div>
