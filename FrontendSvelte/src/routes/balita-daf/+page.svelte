<script lang="ts">
  import { onMount } from "svelte";
  import { writable, derived } from "svelte/store";
  import { goto } from "$app/navigation";
  import { PUBLIC_BACKEND_URL } from "$env/static/public";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "$lib/components/ui/alert-dialog";
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";
  import { Search, Plus, Eye, Edit, Trash2, Activity } from "lucide-svelte";

  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

  const balitaList = writable<{ id: number; nama: string; tglLahir: string; status: string }[]>([]);
  const search = writable("");
  const notification = writable<{ message: string; type: "success" | "error" | "" }>({
    message: "",
    type: ""
  });

  let showConfirmModal = false;
  let anakToDelete: number | null = null;
  let isLoading = true;

  const filteredList = derived([balitaList, search], ([$balitaList, $search]) =>
    $balitaList.filter((b) => b.nama.toLowerCase().includes($search.toLowerCase()))
  );

  let idOrangtua: number | null = null;

  onMount(async () => {
    const params = new URLSearchParams(window.location.search);
    const idParam = params.get("id");
    idOrangtua = idParam ? Number(idParam) : Number(sessionStorage.getItem("selected_orangtua"));

    if (!idOrangtua) {
      showNotification("ID orang tua tidak ditemukan", "error");
      setTimeout(() => goto("/dashboard-perawat"), 1500);
      return;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/api/anak-by-orangtua/${idOrangtua}`);
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
    } finally {
      isLoading = false;
    }
  });

  function showNotification(message: string, type: "success" | "error") {
    notification.set({ message, type });
    setTimeout(() => notification.set({ message: "", type: "" }), 3000);
  }

  function mulaiPengukuran(idAnak: number) {
    goto(`/peng1?id_anak=${idAnak}`);
  }

  function detailPengukuran(idAnak: number) {
    goto(`/balita-det?id=${idAnak}`);
  }

  function editAnak(id: number) {
    goto(`/anak-kel?id_anak=${id}&id_orangtua=${idOrangtua}`);
  }

  function konfirmasiHapus(id: number) {
    anakToDelete = id;
    showConfirmModal = true;
  }

  async function hapusAnak() {
    if (!anakToDelete) return;
    try {
      const res = await fetch(`${BACKEND_URL}/anak/delete/${anakToDelete}`, {
        method: "POST"
      });

      if (res.ok) {
        balitaList.update((list) => list.filter((a) => a.id !== anakToDelete));
        showNotification("Anak berhasil dihapus", "success");
      } else {
        showNotification("Gagal menghapus anak", "error");
      }
    } catch (err) {
      showNotification("Terjadi kesalahan saat menghapus anak", "error");
    } finally {
      showConfirmModal = false;
      anakToDelete = null;
    }
  }

  function getStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
    const s = status.toLowerCase();
    if (s.includes("normal")) return "default";
    if (s.includes("gizi buruk") || s.includes("stunting")) return "destructive";
    if (s.includes("kurang")) return "secondary";
    return "outline";
  }
</script>

<div class="container mx-auto py-6 px-4 max-w-7xl">
  <!-- Notification Toast -->
  {#if $notification.message}
    <div
      class="fixed top-4 right-4 z-50 rounded-lg px-6 py-4 text-white shadow-xl transition-all duration-300 animate-in slide-in-from-top-5"
      class:bg-green-600={$notification.type === "success"}
      class:bg-red-600={$notification.type === "error"}
    >
      <div class="flex items-center gap-2">
        <div class="text-sm font-medium">{$notification.message}</div>
      </div>
    </div>
  {/if}

  <!-- Delete Confirmation Dialog -->
  <AlertDialog open={showConfirmModal}>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Konfirmasi Hapus</AlertDialogTitle>
        <AlertDialogDescription>
          Apakah Anda yakin ingin menghapus data anak ini? Tindakan ini tidak dapat dibatalkan dan akan menghapus semua data pengukuran terkait.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel onclick={() => (showConfirmModal = false)}>
          Batal
        </AlertDialogCancel>
        <AlertDialogAction onclick={hapusAnak} class="bg-red-600 hover:bg-red-700">
          Hapus
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>

  <!-- Main Card -->
  <Card>
    <CardHeader>
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <CardTitle class="text-2xl font-bold">Daftar Balita</CardTitle>
          <CardDescription class="mt-1">
            Kelola data balita dan lakukan pengukuran pertumbuhan
          </CardDescription>
        </div>
        <Button onclick={() => goto(`/crud-anak?id_orangtua=${idOrangtua}`)} class="w-full sm:w-auto">
          <Plus class="mr-2 h-4 w-4" />
          Tambah Balita
        </Button>
      </div>
    </CardHeader>
    <CardContent>
      <!-- Search Bar -->
      <div class="mb-6">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Cari nama balita..."
            bind:value={$search}
            class="pl-9"
          />
        </div>
      </div>

      <!-- Table -->
      {#if isLoading}
        <div class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
            <p class="mt-2 text-sm text-muted-foreground">Memuat data...</p>
          </div>
        </div>
      {:else}
        <div class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[250px]">Nama</TableHead>
                <TableHead>Tanggal Lahir</TableHead>
                <TableHead>Status Gizi</TableHead>
                <TableHead class="text-right">Aksi</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {#if $filteredList.length > 0}
                {#each $filteredList as balita}
                  <TableRow>
                    <TableCell class="font-medium">{balita.nama}</TableCell>
                    <TableCell>{balita.tglLahir}</TableCell>
                    <TableCell>
                      <Badge variant={getStatusVariant(balita.status)}>
                        {balita.status}
                      </Badge>
                    </TableCell>
                    <TableCell class="text-right">
                      <div class="flex justify-end gap-2">
                        <Button
                          variant="default"
                          size="sm"
                          onclick={() => mulaiPengukuran(balita.id)}
                          class="h-8"
                        >
                          <Activity class="mr-1 h-3 w-3" />
                          Ukur
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onclick={() => detailPengukuran(balita.id)}
                          class="h-8"
                        >
                          <Eye class="mr-1 h-3 w-3" />
                          Detail
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onclick={() => editAnak(balita.id)}
                          class="h-8"
                        >
                          <Edit class="mr-1 h-3 w-3" />
                          Edit
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onclick={() => konfirmasiHapus(balita.id)}
                          class="h-8"
                        >
                          <Trash2 class="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                {/each}
              {:else}
                <TableRow>
                  <TableCell colspan="4" class="h-32 text-center">
                    <div class="flex flex-col items-center justify-center text-muted-foreground">
                      <p class="text-sm">Belum ada data balita</p>
                      <p class="text-xs mt-1">Klik tombol "Tambah Balita" untuk menambahkan data</p>
                    </div>
                  </TableCell>
                </TableRow>
              {/if}
            </TableBody>
          </Table>
        </div>
      {/if}

      <!-- Stats Footer -->
      {#if $filteredList.length > 0}
        <div class="mt-4 flex items-center justify-between text-sm text-muted-foreground">
          <div>
            Menampilkan <span class="font-medium text-foreground">{$filteredList.length}</span> dari <span class="font-medium text-foreground">{$balitaList.length}</span> balita
          </div>
        </div>
      {/if}
    </CardContent>
  </Card>
</div>

<style>
  :global(body) {
    background-color: hsl(var(--background));
  }
</style>