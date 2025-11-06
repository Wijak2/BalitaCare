<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { writable, derived } from 'svelte/store';
	import { goto } from '$app/navigation';

	type Anak = {
		id: number;
		nama: string;
		jenis_kelamin: string;
		tanggal_lahir: string;
	};

	const anakList = writable<Anak[]>([]);
	const search = writable('');

	// ✅ NOTIFIKASI
	const notification = writable<{ message: string; type: 'success' | 'error' | '' }>({
		message: '',
		type: ''
	});

	function showNotification(message: string, type: 'success' | 'error') {
		notification.set({ message, type });
		setTimeout(() => notification.set({ message: '', type: '' }), 2500);
	}

	// ✅ MODAL KONFIRMASI
	let showConfirmModal = false;
	let anakToDelete: number | null = null;

	function konfirmasiHapus(id: number) {
		anakToDelete = id;
		showConfirmModal = true;
	}

	async function hapusAnak() {
		if (!anakToDelete) return;

		try {
			const res = await fetch(`http://127.0.0.1:5000/iot/anak/delete/${anakToDelete}`, {
				method: 'POST'
			});

			if (res.ok) {
				anakList.update((list) => list.filter((a) => a.id !== anakToDelete));
				showNotification('✅ Anak berhasil dihapus', 'success');
			} else {
				showNotification('❌ Gagal menghapus anak', 'error');
			}
		} catch (err) {
			showNotification('❌ Terjadi kesalahan saat menghapus anak', 'error');
		} finally {
			showConfirmModal = false;
			anakToDelete = null;
		}
	}

	// 🔍 Filter hasil pencarian
	const filteredList = derived([anakList, search], ([$anakList, $search]) =>
		$anakList.filter((a) => a.nama.toLowerCase().includes($search.toLowerCase()))
	);

	// Ambil id_orangtua
	let idOrangtua: string | null = null;
	$: idOrangtua = $page.url.searchParams.get('id_orangtua');

	// Ambil data anak dari backend
	async function loadAnak() {
		try {
			let urlAnak = `http://127.0.0.1:5000/iot/api/anak`;
			if (idOrangtua) urlAnak = `http://127.0.0.1:5000/iot/api/anak-by-orangtua/${idOrangtua}`;

			const resAnak = await fetch(urlAnak);
			const dataAnak = await resAnak.json();

			anakList.set(
				dataAnak.map((a: any) => ({
					id: a.id_anak,
					nama: a.nama,
					jenis_kelamin: a.jenis_kelamin,
					tanggal_lahir: a.tanggal_lahir
				}))
			);
		} catch (err) {
			showNotification('❌ Gagal memuat data anak dari server', 'error');
		}
	}

	onMount(() => {
		loadAnak();
	});

	// Navigasi
	function tambahAnak() {
		goto(`/crud-anak?id_orangtua=${idOrangtua}`);
	}

	function editAnak(id: number) {
		goto(`/crud-anak?id_anak=${id}&id_orangtua=${idOrangtua}`);
	}

	function kembali() {
		window.location.href = '/dashboard-orangtua';
	}
</script>

<section class="page-wrapper w-full px-4 sm:px-8 lg:px-24">

	<!-- ✅ NOTIFIKASI -->
	{#if $notification.message}
		<div
			class="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 rounded-lg px-6 py-3 text-white shadow-lg transition-all duration-300"
			class:bg-green-500={$notification.type === 'success'}
			class:bg-red-500={$notification.type === 'error'}
		>
			{$notification.message}
		</div>
	{/if}

	<!-- ✅ MODAL KONFIRMASI -->
	{#if showConfirmModal}
		<div class="fixed inset-0 z-40 flex items-center justify-center bg-black bg-opacity-40">
			<div class="rounded-lg bg-white p-6 shadow-xl w-[90%] max-w-sm text-center animate-fadeIn">
				<h3 class="text-lg font-semibold mb-3 text-gray-800">Konfirmasi Hapus</h3>
				<p class="text-gray-600 mb-5">Apakah Anda yakin ingin menghapus anak ini?</p>

				<div class="flex justify-center gap-3">
					<button
						on:click={hapusAnak}
						class="rounded-md bg-red-600 px-4 py-2 text-white font-semibold hover:bg-red-700"
					>
						Hapus
					</button>

					<button
						on:click={() => (showConfirmModal = false)}
						class="rounded-md bg-gray-300 px-4 py-2 text-gray-800 font-semibold hover:bg-gray-400"
					>
						Batal
					</button>
				</div>
			</div>
		</div>
	{/if}

	<!-- Tombol Kembali -->
	<div class="mb-6">
		<button
			on:click={kembali}
			class="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-all duration-200 hover:bg-blue-700 sm:px-6 sm:py-3 sm:text-base"
		>
			Kembali ke Dashboard Orang Tua
		</button>
	</div>

	<header class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="text-2xl font-bold text-blue-900 sm:text-3xl">Daftar Anak</h1>
		<button
			on:click={tambahAnak}
			class="btn-A bg-blue-500 text-white transition-all hover:bg-blue-700 sm:px-6 sm:py-2 sm:text-base"
		>
			+ Tambah Anak
		</button>
	</header>

	<div class="mb-4">
		<input
			type="text"
			placeholder="🔍 Cari anak..."
			bind:value={$search}
			class="w-full rounded-lg border p-3 focus:ring-2 focus:ring-blue-400 focus:outline-none"
		/>
	</div>

	<div class="table-container">
		<table class="w-full min-w-[500px] border-collapse text-left text-sm sm:text-base">
			<thead class="bg-blue-100">
				<tr>
					<th class="min-w-[250px] p-3 sm:min-w-[300px]">Nama Anak</th>
					<th class="w-32 p-3 sm:w-36">Jenis Kelamin</th>
					<th class="w-40 p-3 sm:w-44">Tanggal Lahir</th>
					<th class="w-40 p-3 text-center sm:w-48">Aksi</th>
				</tr>
			</thead>

			<tbody>
				{#if $filteredList.length > 0}
					{#each $filteredList as a (a.id)}
						<tr class="bg-white transition-colors hover:bg-blue-50">
							<td class="p-3">{a.nama}</td>
							<td class="p-3">{a.jenis_kelamin ?? '-'}</td>
							<td class="p-3">{a.tanggal_lahir}</td>
							<td class="flex justify-center gap-2 p-3">
								<button
									on:click={() => editAnak(a.id)}
									class="rounded-lg bg-blue-500 px-2 py-1 text-xs font-semibold text-white hover:bg-blue-600 sm:px-3 sm:text-sm"
								>Edit</button>

								<button
									on:click={() => konfirmasiHapus(a.id)}
									class="rounded-lg bg-red-600 px-2 py-1 text-xs font-semibold text-white hover:bg-red-700 sm:px-3 sm:text-sm"
								>Hapus</button>
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="5" class="p-3 text-center text-gray-500">Belum ada data anak</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</section>
