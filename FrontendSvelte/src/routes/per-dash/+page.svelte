<script lang="ts">
  import { onMount } from "svelte";
  import { writable, derived } from "svelte/store";
  import { goto } from "$app/navigation";
  import { PUBLIC_BACKEND_URL } from "$env/static/public";

  // Import shadcn-svelte components
  import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Table, TableBody, TableCell, TableHead, TableRow, TableHeader } from "$lib/components/ui/table";
  import { Search, Users, Baby, UserRound, PlusCircle, Eye } from "lucide-svelte";

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

  function decodeJWT(token: string) {
    try {
      return JSON.parse(atob(token.split(".")[1]));
    } catch {
      return null;
    }
  }

  onMount(async () => {
    const token = sessionStorage.getItem("token");

    if (!token) {
      alert("Anda belum login");
      goto("/sign-in");
      return;
    }

    const payload = decodeJWT(token);

    if (!payload || payload.role !== "perawat") {
      alert("Akses ditolak. Anda bukan perawat.");
      goto("/sign-in");
      return;
    }

    try {
      const resStats = await fetch(`${BACKEND_URL}/api/dashboard-stats`, {
        headers: { Authorization: "Bearer " + token }
      });
      const dataStats = await resStats.json();

      statsPerawat = [
        { title: "Jumlah Orang Tua Terdaftar", value: dataStats.orangtua },
        { title: "Jumlah Balita Terdaftar", value: dataStats.anak },
        { title: "Jumlah Perawat Terdaftar", value: dataStats.perawat }
      ];

      const resOrtu = await fetch(`${BACKEND_URL}/api/orangtua`, {
        headers: { Authorization: "Bearer " + token }
      });
      const dataOrtu = await resOrtu.json();
      orangtuaList.set(dataOrtu);

    } catch (err) {
      console.error("Gagal mengambil data dashboard:", err);
    }
  });

  function goListBalita(id_orang_tua: number) {
    sessionStorage.setItem("selected_orangtua", String(id_orang_tua));
    goto("/balita-daf");
  }

  function goTambahAnak(id_orang_tua: number) {
    sessionStorage.setItem("selected_orangtua", String(id_orang_tua));
    goto("/crud-anak");
  }
</script>

<div class="container mx-auto px-4 py-8 sm:py-12">
  <!-- Stats Cards -->
  <div class="mb-6 grid gap-4 md:grid-cols-3">
    {#each statsPerawat as stat}
      <Card class="relative overflow-hidden">
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">{stat.title}</CardTitle>
          <div class="h-8 w-8 rounded-md bg-muted p-1.5">
            {#if stat.title.includes("Orang Tua")}
              <Users class="h-full w-full text-blue-600" />
            {:else if stat.title.includes("Balita")}
              <Baby class="h-full w-full text-green-600" />
            {:else if stat.title.includes("Perawat")}
              <UserRound class="h-full w-full text-purple-600" />
            {/if}
          </div>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-blue-600">{stat.value}</div>
        </CardContent>
        <div class="absolute bottom-0 right-0 h-16 w-16 rounded-full bg-gradient-to-br from-transparent to-muted/20"></div>
      </Card>
    {/each}
  </div>

  <!-- Search and Title -->
  <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <h2 class="text-2xl font-bold">Orangtua Terdaftar</h2>
    <div class="relative w-full sm:w-64">
      <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
      <Input
        type="text"
        placeholder="Cari nama..."
        bind:value={$search}
        class="pl-8"
      />
    </div>
  </div>

  <!-- Table -->
  <Card>
    <CardContent class="p-0">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nama</TableHead>
            <TableHead>Nomor Telepon</TableHead>
            <TableHead>Email</TableHead>
            <TableHead class="text-right">Aksi</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {#if $filteredList.length > 0}
            {#each $filteredList as o}
              <TableRow>
                <TableCell class="font-medium">{o.nama}</TableCell>
                <TableCell>{o.telp}</TableCell>
                <TableCell>{o.email}</TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onclick={() => goListBalita(o.id_orang_tua)}
                      class="h-8 gap-1"
                    >
                      <Eye class="h-3.5 w-3.5" />
                      <span class="hidden sm:inline">Daftar Anak</span>
                    </Button>
                    <Button
                      size="sm"
                      onclick={() => goTambahAnak(o.id_orang_tua)}
                      class="h-8 gap-1"
                    >
                      <PlusCircle class="h-3.5 w-3.5" />
                      <span class="hidden sm:inline">Tambah Anak</span>
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            {/each}
          {:else}
            <TableRow>
              <TableCell colspan="4" class="text-center">Belum ada data orang tua</TableCell>
            </TableRow>
          {/if}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</div>

<style>
  :global(.text-muted-foreground) {
    color: hsl(var(--muted-foreground));
  }
</style>
