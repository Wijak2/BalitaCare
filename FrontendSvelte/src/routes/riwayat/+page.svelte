<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from '$app/navigation';
  import { PUBLIC_BACKEND_URL } from "$env/static/public";

  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

  let id_anak: string | null = null;
  let data: any[] = [];
  let loading = true;

  onMount(async () => {
    try {
      const params = new URLSearchParams(window.location.search);
      id_anak = params.get("id") || sessionStorage.getItem("selected_anak_id") || "1";

      const res = await fetch(`${BACKEND_URL}/api/pengukuran/riwayat/${id_anak}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const json = await res.json();
      data = Array.isArray(json) ? json : [];
    } catch (err) {
      console.error("🔥 Gagal memuat riwayat pengukuran:", err);
    } finally {
      loading = false;
    }
  });

  let role = sessionStorage.getItem('role');

  function kembali() {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      if (role === 'perawat') {
        const idPerawat = sessionStorage.getItem('id_perawat');
        goto(`/dashboard-perawat?id=${idPerawat}`);
      } else {
        const idOrangtua = sessionStorage.getItem('id_orangtua');
        goto(`/dashboard-orangtua?id=${idOrangtua}`);
      }
    }
  }

  function formatTanggal(t: string | null) {
    if (!t) return "-";
    const d = new Date(t);
    if (isNaN(d.getTime())) return t;
    return d.toLocaleString("id-ID", { year: "numeric", month: "long", day: "numeric" });
  }
</script>

<section class="page-wrapper">
  <div class="table-container">
    <h1 class="text-3xl font-extrabold text-center text-blue-900 mb-6">
      Riwayat Pengukuran
    </h1>

    {#if loading}
      <p class="text-center text-gray-500 font-semibold">Memuat data riwayat...</p>
    {:else if data && data.length > 0}
      <table class="w-full text-left border-collapse bg-blue-50/30 rounded-xl overflow-hidden shadow-sm">
        <thead class="bg-blue-200">
          <tr>
            <th class="p-3">Lingkar Kepala (cm)</th>
            <th class="p-3">Lingkar Lengan (cm)</th>
            <th class="p-3">Berat Badan (kg)</th>
            <th class="p-3">Tinggi Badan (cm)</th>
            <th class="p-3">Tanggal</th>
          </tr>
        </thead>
        <tbody>
          {#each data as item, i}
            <tr class={i % 2 === 0 ? "bg-blue-50" : "bg-white"}>
              <td class="p-2">{item.lingkar_kepala ?? '-'}</td>
              <td class="p-2">{item.lingkar_lengan ?? '-'}</td>
              <td class="p-2">{item.berat_badan ?? '-'}</td>
              <td class="p-2">{item.tinggi_badan ?? '-'}</td>
              <td class="p-2">{formatTanggal(item.tanggal ?? null)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p class="text-center text-gray-500">Belum ada data pengukuran untuk anak ini.</p>
    {/if}

    <div class="text-center mt-3">
      <button
        on:click={kembali}
        class="btn-A bg-blue-500 hover:bg-blue-700 text-white transition-all duration-200">
        Kembali
      </button>
    </div>
  </div>
</section>

<style>
.orangtua-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
}
table th, table td {
  text-align: left;
}
table th {
  font-weight: 600;
}
</style>
