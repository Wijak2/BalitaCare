<script lang="ts">
  import { onMount } from "svelte";
  import { writable, derived } from "svelte/store";
  import { goto } from "$app/navigation";
  import { PUBLIC_BACKEND_URL } from "$env/static/public";

  // Backend URL dari .env
  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

  const balitaList = writable<{ id: number; nama: string; tglLahir: string; status: string }[]>([]);
  const search = writable("");
  const notification = writable<{ message: string; type: "success" | "error" | "" }>({
    message: "",
    type: ""
  });

  let showConfirmModal = false;
  let anakToDelete: number | null = null;

  const filteredList = derived([balitaList, search], ([$balitaList, $search]) =>
    $balitaList.filter((b) => b.nama.toLowerCase().includes($search.toLowerCase()))
  );

  let idOrangtua: number | null = null;

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
      alert("Anda belum login");
      goto("/login");
      return;
    }

    const payload = decodeJWT(token);
    if (!payload) {
      alert("Token tidak valid");
      goto("/login");
      return;
    }

    if (payload.role === "orang_tua") {
      idOrangtua = payload.user_id;
    } else if (payload.role === "perawat") {
      const stored = localStorage.getItem("selected_orangtua");
      if (!stored) {
        alert("Silakan pilih orang tua dari dashboard terlebih dahulu.");
        goto("/dashboard-perawat");
        return;
      }
      idOrangtua = Number(stored);
    } else {
      alert("Role tidak dikenali");
      goto("/login");
      return;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/api/anak-by-orangtua/${idOrangtua}`, {
        headers: { Authorization: "Bearer " + token }
      });

      const data = await res.json();

      balitaList.set(
        data.map((a: any) => ({
          id: a.id_anak,
          nama: a.nama,
          tglLahir: a.tanggal_lahir,
          status: a.status || "-"
        }))
      );
    } catch (err) {
      showNotification("Gagal memuat data anak", "error");
    }
  });

  function showNotification(message: string, type: "success" | "error") {
    notification.set({ message, type });
    setTimeout(() => notification.set({ message: "", type: "" }), 2500);
  }

  function mulaiPengukuran(idAnak: number) {
    goto(`/form-pengukuran-step1?id_anak=${idAnak}`);
  }

  function detailPengukuran(idAnak: number) {
    goto(`/detail-pengukuran?id=${idAnak}`);
  }

  function editAnak(id: number) {
    goto(`/crud-anak?id_anak=${id}&id_orangtua=${idOrangtua}`);
  }

  function konfirmasiHapus(id: number) {
    anakToDelete = id;
    showConfirmModal = true;
  }

  async function hapusAnak() {
    if (!anakToDelete) return;

    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${BACKEND_URL}/anak/delete/${anakToDelete}`, {
        method: "POST",
        headers: { Authorization: "Bearer " + token }
      });

      if (res.ok) {
        balitaList.update((list) => list.filter((a) => a.id !== anakToDelete));
        showNotification("✅ Anak berhasil dihapus", "success");
      } else {
        showNotification("❌ Gagal menghapus anak", "error");
      }
    } catch (err) {
      showNotification("❌ Terjadi kesalahan saat menghapus anak", "error");
    } finally {
      showConfirmModal = false;
      anakToDelete = null;
    }
  }
</script>

<div class="page-wrapper relative">
  {#if $notification.message}
    <div
      class="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 rounded-lg px-6 py-3 text-white shadow-lg transition-all duration-300"
      class:bg-green-500={$notification.type === "success"}
      class:bg-red-500={$notification.type === "error"}
    >
      {$notification.message}
    </div>
  {/if}

  {#if showConfirmModal}
    <div class="fixed inset-0 z-40 flex items-center justify-center bg-black bg-opacity-40">
      <div class="rounded-lg bg-white p-6 shadow-xl w-[90%] max-w-sm text-center animate-fadeIn">
        <h3 class="text-lg font-semibold mb-3 text-gray-800">Konfirmasi Hapus</h3>
        <p class="text-gray-600 mb-5">Apakah Anda yakin ingin menghapus anak ini?</p>
        <div class="flex justify-center gap-3">
          <button
            on:click={hapusAnak}
            class="rounded-md bg-red-600 px-4 py-2 text-white font-semibold hover:bg-red-700"
          >Hapus</button>
          <button
            on:click={() => (showConfirmModal = false)}
            class="rounded-md bg-gray-300 px-4 py-2 text-gray-800 font-semibold hover:bg-gray-400"
          >Batal</button>
        </div>
      </div>
    </div>
  {/if}

  <div class="flex flex-col sm:flex-row justify-between pb-2">
    <h2 class="text-2xl font-bold text-blue-900">Daftar Balita</h2>
    <input
      type="text"
      placeholder="🔍 Cari nama..."
      bind:value={$search}
      class="w-full sm:w-52 rounded-md border border-gray-300 px-2 py-1 focus:ring-2 focus:ring-blue-400 focus:outline-none"
    />
  </div>

  <div class="table-container mt-3">
    <table class="w-full border-collapse text-left text-sm sm:text-base">
      <thead class="bg-blue-100">
        <tr>
          <th class="p-3">Nama</th>
          <th class="p-3">Tanggal Lahir</th>
          <th class="p-3">Status</th>
          <th class="p-3 text-center">Aksi</th>
        </tr>
      </thead>
      <tbody>
        {#if $filteredList.length > 0}
          {#each $filteredList as b}
            <tr class="bg-white hover:bg-blue-50 transition">
              <td class="p-3">{b.nama}</td>
              <td class="p-3">{b.tglLahir}</td>
              <td class="p-3">{b.status}</td>
              <td class="flex justify-center gap-2 p-3">
                <button class="btn-B bg-blue-500 text-white hover:bg-blue-600" on:click={() => mulaiPengukuran(b.id)}>Pengukuran</button>
                <button class="btn-B bg-green-500 text-white hover:bg-green-600" on:click={() => detailPengukuran(b.id)}>Detail</button>
                <button class="btn-B bg-yellow-500 text-white hover:bg-yellow-600" on:click={() => editAnak(b.id)}>Edit</button>
                <button class="btn-B bg-red-600 text-white hover:bg-red-700" on:click={() => konfirmasiHapus(b.id)}>Hapus</button>
              </td>
            </tr>
          {/each}
        {:else}
          <tr>
            <td colspan="4" class="text-center py-3 text-gray-500">Belum ada data balita</td>
          </tr>
        {/if}
      </tbody>
    </table>
  </div>
</div>
