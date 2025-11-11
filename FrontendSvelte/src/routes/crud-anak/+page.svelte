<script lang="ts">
	import { onMount } from "svelte";
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";
	import { writable } from "svelte/store";
	import { PUBLIC_BACKEND_URL } from "$env/static/public";

	const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

	const notification = writable<{ message: string; type: 'success' | 'error' | '' }>({
		message: '',
		type: ''
	});

	function showNotification(message: string, type: 'success' | 'error') {
		notification.set({ message, type });
		setTimeout(() => notification.set({ message: '', type: '' }), 2000);
	}

	let idAnak: string | null = null;
	let idOrangtua: string | null = null;
	let nama = '';
	let jenis_kelamin = '';
	let tanggal_lahir = '';

	$: idAnak = $page.url.searchParams.get('id_anak');

	$: idOrangtua =
		$page.url.searchParams.get('id_orangtua') ||
		localStorage.getItem('selected_orangtua');

	onMount(async () => {
		if (idAnak) {
			try {
				const res = await fetch(`${BACKEND_URL}/api/anak/${idAnak}`);
				if (res.ok) {
					const data = await res.json();
					nama = data.nama;
					jenis_kelamin = data.jenis_kelamin;
					tanggal_lahir = data.tanggal_lahir;
				} else {
					showNotification('Gagal mengambil data anak', 'error');
				}
			} catch (err) {
				showNotification('Terjadi kesalahan', 'error');
			}
		}
	});

	let role = sessionStorage.getItem('role');

	function kembali() {
		if (window.history.length > 1) {
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
			showNotification('ID orang tua tidak ditemukan', 'error');
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
				showNotification('✅ Data berhasil disimpan', 'success');
				setTimeout(() => {
					kembali();
				}, 1000);
			} else {
				const text = await res.text();
				showNotification('Gagal menyimpan data: ' + text, 'error');
			}
		} catch (err) {
			showNotification('Terjadi kesalahan saat menyimpan data', 'error');
		}
	}
</script>

<section class="crud-anak mx-auto min-w-[400px] p-6">
	{#if $notification.message}
		<div
			class="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 rounded-lg px-6 py-3 text-white shadow-lg transition-all duration-300"
			class:bg-green-500={$notification.type === 'success'}
			class:bg-red-500={$notification.type === 'error'}
		>
			{$notification.message}
		</div>
	{/if}

	<div class="mx-auto max-w-lg rounded-2xl bg-white p-8 shadow-2xl">
		<h3 class="mb-6 text-2xl font-bold text-gray-800">
			{idAnak ? '✏️ Edit Anak' : '➕ Tambah Anak'}
		</h3>

		<form on:submit|preventDefault={submitForm} class="space-y-4">
			<div>
				<label class="mb-1 block font-medium text-gray-700">Nama Anak</label>
				<input
					type="text"
					bind:value={nama}
					required
					class="w-full rounded-lg border px-4 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none"
				/>
			</div>

			<div>
				<label class="mb-1 block font-medium text-gray-700">Jenis Kelamin</label>
				<select
					bind:value={jenis_kelamin}
					required
					class="w-full rounded-lg border px-4 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none"
				>
					<option value="">-- Pilih Jenis Kelamin --</option>
					<option value="Laki-laki">Laki-laki</option>
					<option value="Perempuan">Perempuan</option>
				</select>
			</div>

			<div>
				<label class="mb-1 block font-medium text-gray-700">Tanggal Lahir</label>
				<input
					type="date"
					bind:value={tanggal_lahir}
					required
					class="w-full rounded-lg border px-4 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none"
				/>
			</div>

			<div class="mt-6 flex justify-between">
				<button
					type="button"
					on:click={kembali}
					class="btn-A bg-gray-400 text-white transition-colors hover:bg-gray-500"
				>
					Batal
				</button>

				<button
					type="submit"
					class="rounded-xl bg-blue-600 px-6 py-2 font-semibold text-white transition-colors hover:bg-blue-700"
				>
					Simpan
				</button>
			</div>
		</form>
	</div>
</section>

<style>
	.crud-anak {
		max-width: 1000px;
		margin: 0 auto;
		font-family: 'Inter', sans-serif;
	}
</style>
