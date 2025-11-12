<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { get } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { writable } from 'svelte/store';
	import { PUBLIC_BACKEND_URL } from "$env/static/public";

	const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

	const notification = writable<{ message: string; type: 'success' | 'error' | '' }>({
		message: '',
		type: ''
	});

	function showNotification(message: string, type: 'success' | 'error') {
		notification.set({ message, type });
		setTimeout(() => {
			notification.set({ message: '', type: '' });
		}, 2000);
	}

	let idAnak = '';
	let idPengukuran = '';
	let activeForm = 'kepala';
	let iotKepala: number | null = null;
	let iotLengan: number | null = null;
	let tinggiBadan = '';
	let beratBadan = '';
	let anakNama = '';

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
			}
		} catch (err) {
			console.error('Gagal ambil data IoT:', err);
			iotKepala = null;
			iotLengan = null;
		}
	}

	async function saveData() {
		if (!idAnak || !idPengukuran) {
			showNotification('❌ ID anak atau ID pengukuran tidak ditemukan', 'error');
			return;
		}

		const formData = new FormData();
		formData.append('id_anak', idAnak);
		formData.append('id_pengukuran', idPengukuran);

		if (activeForm === 'kepala') {
			if (iotKepala === null) {
				showNotification('⚠️ Belum ada data IoT!', 'error');
				return;
			}
			formData.append('jenis', 'kepala');
			formData.append('nilai', iotKepala.toString());
		} else if (activeForm === 'lengan') {
			if (iotLengan === null) {
				showNotification('⚠️ Belum ada data IoT!', 'error');
				return;
			}
			formData.append('jenis', 'lengan');
			formData.append('nilai', iotLengan.toString());
		} else {
			formData.append('jenis', 'bbtb');
			formData.append('tinggi_badan', tinggiBadan);
			formData.append('berat_badan', beratBadan);
		}

		try {
			const res = await fetch(`${BACKEND_URL}/save-current`, {
				method: 'POST',
				body: formData
			});

			const data = await res.text();

			if (res.ok) {
				showNotification('✅ Data berhasil disimpan', 'success');
			} else {
				showNotification('❌ Gagal menyimpan data', 'error');
			}
		} catch (err) {
			console.error(err);
			showNotification('❌ Gagal menyimpan data', 'error');
		}
	}

	async function processAnalisis() {
		if (!idPengukuran) {
			showNotification('❌ ID pengukuran tidak ditemukan', 'error');
			return;
		}

		try {
			const res = await fetch(`${BACKEND_URL}/api/process/${idPengukuran}`, {
				method: 'POST'
			});
			const data = await res.json();

			if (!res.ok) {
				showNotification(`❌ ${data.error || 'Gagal memproses analisis'}`, 'error');
				return;
			}

			showNotification('✅ Analisis berhasil diproses', 'success');
			console.log('Hasil analisis:', data);

		} catch (err) {
			console.error(err);
			showNotification('❌ Terjadi kesalahan saat memproses analisis', 'error');
		}
	}

	function showForm(form: string) {
		activeForm = form;
	}
</script>


{#if $notification.message}
	<div
		class="fixed left-1/2 top-1/2 z-50
		-translate-x-1/2 -translate-y-1/2
		rounded-lg px-6 py-3 text-white shadow-lg transition-all duration-300"
		class:bg-green-500={$notification.type === 'success'}
		class:bg-red-500={$notification.type === 'error'}
	>
		{$notification.message}
	</div>
{/if}

<div class="">
	<div class="page-wrapper flex items-center justify-center">
		<div class="max-w-200 flex w-full flex-col rounded-xl bg-white p-8 shadow-md">
			<h2 class="mb-4">📏 Langkah 2: Pengukuran Anak</h2>
			<p class="mb-8">Nama Anak: <b>{anakNama}</b></p>

			<div class="mb-8 flex gap-2">
				<button
					class="rounded-4xl flex-1 cursor-pointer bg-sky-500 py-2.5 text-white transition hover:bg-sky-600"
					class:bg-sky-700={activeForm === 'kepala'}
					on:click={() => showForm('kepala')}
				>
					Lingkar Kepala
				</button>

				<button
					class="rounded-4xl flex-1 cursor-pointer bg-sky-500 py-2.5 text-white transition hover:bg-sky-600"
					class:bg-sky-700={activeForm === 'lengan'}
					on:click={() => showForm('lengan')}
				>
					Lingkar Lengan
				</button>

				<button
					class="rounded-4xl flex-1 cursor-pointer bg-sky-500 py-2.5 text-white transition hover:bg-sky-600"
					class:bg-sky-700={activeForm === 'bbtb'}
					on:click={() => showForm('bbtb')}
				>
					BB & TB
				</button>
			</div>

			{#if activeForm === 'kepala'}
				<div>
					<h5>Pengukuran Lingkar Kepala</h5>
					<div
						class="my-4 flex h-40 items-center justify-center rounded-xl bg-gray-200 p-6 text-center"
					>
						{#if iotKepala !== null}
							Data IoT: <b>{iotKepala} cm</b>
						{:else}
							Menunggu data IoT...
						{/if}
					</div>
					<p class="text-[0.85em] text-gray-500 mb-4">
						Data ini akan tersimpan di DB saat klik tombol Simpan.
					</p>
				</div>
			{/if}

			{#if activeForm === 'lengan'}
				<div>
					<h5>Pengukuran Lingkar Lengan</h5>
					<div
						class="my-4 flex h-40 items-center justify-center rounded-xl bg-gray-200 p-6 text-center"
					>
						{#if iotLengan !== null}
							Data IoT: <b>{iotLengan} cm</b>
						{:else}
							Menunggu data IoT...
						{/if}
					</div>
					<p class="text-[0.85em] text-gray-500 mb-4">
						Data ini akan tersimpan di DB saat klik tombol Simpan.
					</p>
				</div>
			{/if}

			{#if activeForm === 'bbtb'}
				<div class="flex flex-col gap-3 pb-4">
					<h5>Pengukuran Manual</h5>

					<label>Berat Badan (kg)</label>
					<input
						type="number"
						bind:value={beratBadan}
						placeholder="Masukkan berat badan anak"
						class="rounded-4xl w-full border border-gray-300 p-4 outline-none focus:ring-2 focus:ring-sky-400"
					/>

					<label>Tinggi Badan (cm)</label>
					<input
						type="number"
						bind:value={tinggiBadan}
						placeholder="Masukkan tinggi badan anak"
						class="rounded-4xl w-full border border-gray-300 p-4 outline-none focus:ring-2 focus:ring-sky-400"
					/>
				</div>
			{/if}

			<div class="mt-auto flex flex-col gap-3">
				<button
					class="btn-A w-full bg-green-500 text-white transition hover:bg-green-600"
					on:click={saveData}>Simpan Pengukuran</button
				>

				<button
					class="btn-A w-full bg-blue-600 text-white transition hover:bg-blue-700"
					on:click={processAnalisis}
				>
					Proses Analisis Gizi
				</button>

				<button
					on:click={() => goto(`/detail-pengukuran?id=${idAnak}&role=perawat`)}
					class="btn-A w-full bg-sky-500 text-white transition hover:bg-sky-600"
				>
					Lihat Detail Pengukuran
				</button>
				<button
					on:click={() => goto(`/form-pengukuran-step1?id_anak=${idAnak}`)}
					class="btn-A w-full bg-gray-300 transition hover:bg-gray-400"
				>
					Kembali ke Step 1
				</button>
			</div>
		</div>
	</div>
</div>
