<script lang="ts">
  import { onMount } from "svelte";
  import { writable, derived } from "svelte/store";
  import { goto } from "$app/navigation";
  import { PUBLIC_BACKEND_URL } from "$env/static/public";

  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

  let statsPerawat = [
    { title: "Jumlah Orang Tua Terdaftar", value: 0 },
    { title: "Jumlah Balita Terdaftar", value: 0 },
    { title: "Jumlah Perawat Terdaftar", value: 0 }
  ];

  const orangtuaList = writable<
    { id_orang_tua: number; nama: string; email: string; telp: string }[]
  >([]);

  const search = writable("");

  const filteredList = derived([orangtuaList, search], ([$orangtuaList, $search]) =>
    $orangtuaList.filter((o) =>
      o.nama.toLowerCase().includes($search.toLowerCase())
    )
  );

  // ---------- Utility: ambil token (sessionStorage -> localStorage) ----------
  function readStoredToken(): string | null {
    let token = sessionStorage.getItem("token");
    if (token) {
      console.log("[auth] token found in sessionStorage");
      return token;
    }
    token = localStorage.getItem("token");
    if (token) {
      console.log("[auth] token found in localStorage (fallback)");
      return token;
    }
    console.log("[auth] token not found in storage");
    return null;
  }

  // ---------- Base64URL-safe JWT decode (meng-handle "Bearer " juga) ----------
  function decodeJWT(rawToken: string | null) {
    if (!rawToken) return null;
    try {
      // strip "Bearer " jika tidak sengaja disimpan demikian
      const token = rawToken.startsWith("Bearer ") ? rawToken.slice(7) : rawToken;
      const parts = token.split(".");
      if (parts.length !== 3) {
        console.warn("[auth] token tidak berbentuk JWT 3 bagian:", token);
        return null;
      }
      const base64Url = parts[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const padded = base64 + "=".repeat((4 - (base64.length % 4)) % 4);
      // atob pada Base64URL safe setelah replace
      const jsonPayload = decodeURIComponent(
        atob(padded)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );
      const payload = JSON.parse(jsonPayload);
      return payload;
    } catch (e) {
      console.error("[auth] gagal decode JWT:", e);
      return null;
    }
  }

  function isTokenExpired(payload: any) {
    if (!payload || typeof payload.exp !== "number") return false; // tidak tahu, anggap tidak
    // exp pada JWT biasanya dalam detik unix
    const nowSec = Math.floor(Date.now() / 1000);
    return payload.exp <= nowSec;
  }

  // ---------- onMount: validasi token + ambil data ----------
  onMount(async () => {
    console.log("[auth] onMount dashboard-perawat");
    const rawToken = readStoredToken();

    if (!rawToken) {
      alert("Anda belum login (token tidak ditemukan).");
      goto("/login");
      return;
    }

    console.log("[auth] rawToken preview (trimmed):", rawToken.slice(0, 30) + "...");
    const payload = decodeJWT(rawToken);
    console.log("[auth] decoded payload:", payload);

    if (!payload) {
      alert("Token tidak bisa didecode. Silakan login ulang.");
      // opsional: hapus storage lalu redirect
      sessionStorage.removeItem("token");
      localStorage.removeItem("token");
      goto("/login");
      return;
    }

    // cek expired
    if (isTokenExpired(payload)) {
      console.warn("[auth] token expired:", payload.exp);
      alert("Sesi anda telah kedaluwarsa. Silakan login ulang.");
      sessionStorage.removeItem("token");
      localStorage.removeItem("token");
      goto("/login");
      return;
    }

    // cek role (case-insensitive)
    const role = typeof payload.role === "string" ? payload.role.toLowerCase() : "";
    if (role !== "perawat") {
      console.warn("[auth] role tidak cocok:", payload.role);
      alert("Akses ditolak. Anda bukan perawat.");
      goto("/login");
      return;
    }

    // token valid — ambil data
    try {
      const headers = { Authorization: `Bearer ${rawToken}` };

      console.log("[fetch] GET /api/dashboard-stats");
      const resStats = await fetch(`${BACKEND_URL}/api/dashboard-stats`, { headers });
      if (resStats.status === 401 || resStats.status === 403) {
        console.warn("[fetch] /dashboard-stats returned", resStats.status);
        alert("Token tidak valid untuk permintaan ini. Silakan login ulang.");
        sessionStorage.removeItem("token");
        localStorage.removeItem("token");
        goto("/login");
        return;
      }
      if (!resStats.ok) {
        const txt = await resStats.text();
        throw new Error(`/api/dashboard-stats error ${resStats.status}: ${txt}`);
      }
      const dataStats = await resStats.json();
      console.log("[fetch] dataStats:", dataStats);

      statsPerawat = [
        { title: "Jumlah Orang Tua Terdaftar", value: dataStats.orangtua },
        { title: "Jumlah Balita Terdaftar", value: dataStats.anak },
        { title: "Jumlah Perawat Terdaftar", value: dataStats.perawat }
      ];

      console.log("[fetch] GET /api/orangtua");
      const resOrtu = await fetch(`${BACKEND_URL}/api/orangtua`, { headers });
      if (resOrtu.status === 401 || resOrtu.status === 403) {
        console.warn("[fetch] /orangtua returned", resOrtu.status);
        alert("Token tidak valid untuk permintaan daftar orang tua. Silakan login ulang.");
        sessionStorage.removeItem("token");
        localStorage.removeItem("token");
        goto("/login");
        return;
      }
      if (!resOrtu.ok) {
        const txt = await resOrtu.text();
        throw new Error(`/api/orangtua error ${resOrtu.status}: ${txt}`);
      }
      const dataOrtu = await resOrtu.json();
      console.log("[fetch] dataOrtu length:", Array.isArray(dataOrtu) ? dataOrtu.length : typeof dataOrtu);
      orangtuaList.set(dataOrtu);
    } catch (err) {
      console.error("[error] Gagal mengambil data dashboard:", err);
      alert("Terjadi kesalahan saat memuat data dashboard. Cek console untuk detail.");
    }
  });

  // ---------- navigasi ----------
  function goListBalita(id_orang_tua: number) {
    sessionStorage.setItem("selected_orangtua", String(id_orang_tua));
    // tetap navigasi di tab yang sama — jika ingin tab baru gunakan window.open
    goto("/list-balita");
  }

  function goTambahAnak(id_orang_tua: number) {
    sessionStorage.setItem("selected_orangtua", String(id_orang_tua));
    goto("/crud-anak");
  }
</script>

<div class="page-wrapper">
  <div class="mb-6 grid">
    {#each statsPerawat as stat}
      <div class="card-B row-span-3 grid gap-1 bg-white text-center shadow-sm">
        <p>{stat.title}</p>
        <h3 class="text-2xl font-bold text-blue-600">{stat.value}</h3>
      </div>
    {/each}
  </div>

  <div class="flex flex-col sm:flex-row gap-4 justify-between pb-2">
    <h2>Orangtua Terdaftar</h2>
    <input
      type="text"
      placeholder="🔍 Cari nama..."
      bind:value={$search}
      class="w-full rounded-md border border-gray-300 px-2 py-1 sm:w-52"
    />
  </div>

  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th>Nama</th>
          <th>Nomor Telpon</th>
          <th>Email</th>
          <th>Aksi</th>
        </tr>
      </thead>
      <tbody>
        {#if $filteredList.length > 0}
          {#each $filteredList as o}
            <tr>
              <td>{o.nama}</td>
              <td>{o.telp}</td>
              <td>{o.email}</td>
              <td class="space-x-2">
                <button on:click={() => goListBalita(o.id_orang_tua)} class="btn-B bg-blue-500 text-white">Daftar anak</button>
                <button on:click={() => goTambahAnak(o.id_orang_tua)} class="btn-B bg-green-500 text-white sm:px-3 sm:text-sm">Tambah anak</button>
              </td>
            </tr>
          {/each}
        {:else}
          <tr>
            <td colspan="4" class="text-center">Belum ada data orang tua</td>
          </tr>
        {/if}
      </tbody>
    </table>
  </div>
</div>
