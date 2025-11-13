<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	let anakList: any[] = [];
	let id_orang_tua: string | null = null;
	let isLoadingPengukuran = true; // spinner hanya di card-A
	let selectedAnak: any = null;

	function decodeJWT(token: string) {
		try {
			return JSON.parse(atob(token.split('.')[1]));
		} catch {
			return null;
		}
	}

	function cekToken() {
		const token = sessionStorage.getItem('token');
		if (!token) {
			alert('Anda belum login!');
			goto('/login');
			return null;
		}
		const payload = decodeJWT(token);
		if (!payload || !payload.user_id) {
			alert('Sesi tidak valid, silakan login ulang.');
			goto('/login');
			return null;
		}
		return token;
	}

	// 🔹 Ambil semua anak
	async function ambilDataAnak(token: string) {
		try {
			const res = await fetch(`${PUBLIC_BACKEND_URL}/iot/api/anak-by-orangtua/${id_orang_tua}`, {
				headers: { Authorization: 'Bearer ' + token }
			});
			const data = await res.json();
			return data.sort((a, b) => a.id_anak - b.id_anak);
		} catch (e) {
			console.error('Gagal memuat data anak:', e);
			return [];
		}
	}

	// 🔹 Ambil pengukuran tiap anak
	async function preloadPengukuran(anakList: any[], token: string) {
		for (const anak of anakList) {
			try {
				const res = await fetch(`${PUBLIC_BACKEND_URL}/iot/api/pengukuran/detail/${anak.id_anak}`, {
					headers: { Authorization: 'Bearer ' + token }
				});
				if (!res.ok) continue;
				const d = await res.json();
				anak.tinggi_badan = d?.peng?.tinggi_badan ?? '-';
				anak.berat_badan = d?.peng?.berat_badan ?? '-';
				anak.lingkar_kepala = d?.peng?.lingkar_kepala ?? '-';
				anak.lingkar_lengan = d?.peng?.lingkar_lengan ?? '-';
				anak.hasil = d?.hasil ?? {};
				anak.status = d?.hasil?.['BB/U']?.kategori ?? 'Normal';
			} catch (e) {
				console.error(`Gagal memuat pengukuran anak ${anak.nama}:`, e);
			}
		}
	}

	onMount(async () => {
		const token = cekToken();
		if (!token) return;
		id_orang_tua = decodeJWT(token).user_id;

		isLoadingPengukuran = true;
		anakList = await ambilDataAnak(token);

		if (anakList.length > 0) {
			await preloadPengukuran(anakList, token);
			selectedAnak = anakList[0];
		}
		isLoadingPengukuran = false;
	});

	function hitungUsia(tanggal_lahir: string) {
		if (!tanggal_lahir) return '-';
		const tgl = new Date(tanggal_lahir);
		const now = new Date();
		let th = now.getFullYear() - tgl.getFullYear();
		let bln = now.getMonth() - tgl.getMonth();
		if (bln < 0) {
			th--;
			bln += 12;
		}
		return `${th} th ${bln} bln`;
	}

	// 🔹 Navigasi
	function navigasiKe(url: string) {
		const token = cekToken();
		if (!token) return;
		goto(url);
	}

	function tampilkanGrafik(anak: any) {
		selectedAnak = anak;
	}

	function riwayatAnak(anak: any, e: Event) {
		e.stopPropagation();
		navigasiKe(`/riwayat?id=${anak.id_anak}`);
	}

	function kelolaAnak() {
		navigasiKe(`/list-anak?id_orangtua=${id_orang_tua}`);
	}

	function lihatDetail(anak: any) {
		navigasiKe(`/detail-pengukuran?id=${anak.id_anak}`);
	}
</script>

<header
	class="hidden py-14 text-center text-gray-100 sm:block"
	style="background: linear-gradient(to right, #029ae2, #6ed3ff);"
>
	<h1 class="mb-2 text-4xl font-extrabold">Selamat datang di Dashboard Orangtua Bapak/Ibu!</h1>
	<p>Lihat informasi mengenai status, riwayat, serta detail pengukuran anak anda</p>
	<p>Jumlah anak terdaftar: {anakList.length}</p>
</header>

<div class="page-wrapper">
	<div class="mb-2 flex items-center justify-between">
		<h2 class="text-left text-3xl font-bold text-blue-900">Status Anak</h2>
		<button
			on:click={kelolaAnak}
			class="rounded-lg bg-sky-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-sky-600"
		>
			Kelola Anak
		</button>
	</div>

	<!-- 🔹 MOBILE DROPDOWN -->
	<script src="https://cdn.jsdelivr.net/npm/@tailwindplus/elements@1" type="module"></script>
	<el-dropdown class="mb-2 block inline-block w-full sm:hidden">
		<button
			class="shadow-xs inline-flex w-full justify-center gap-x-1.5 rounded-md bg-blue-500 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-600"
		>
			{selectedAnak ? selectedAnak.nama : 'Pilih Anak'}
			<svg viewBox="0 0 20 20" fill="currentColor" class="-mr-1 size-5 text-gray-200">
				<path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"
				/>
			</svg>
		</button>

		<el-menu anchor="bottom end" class="w-full rounded-md bg-white shadow-lg">
			<div class="py-1">
				{#each anakList as anak}
					<a
						on:click={() => tampilkanGrafik(anak)}
						class="block cursor-pointer px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
					>
						{anak.nama}
					</a>
				{/each}
				<button
					on:click={kelolaAnak}
					class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
				>
					Kelola Anak
				</button>
			</div>
		</el-menu>
	</el-dropdown>

	<!-- 🔹 DESKTOP -->
	<div class="hidden sm:block">
		<div class="flex h-[60vh] gap-4">
			<!-- CARD-A -->
			<div class="card-A flex-3 bg-white p-4 text-center relative">
				{#if isLoadingPengukuran}
					<div class="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
						<div class="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
					</div>
				{/if}

				{#if selectedAnak}
					<p class="mb-4 text-lg font-semibold">{selectedAnak.nama} - Pengukuran Terakhir</p>

					<div class="mb-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
						<div class="rounded bg-gray-50 p-2">
							<p class="text-sm text-gray-500">Tinggi Badan</p>
							<p class="font-semibold text-gray-800">{selectedAnak.tinggi_badan ?? '-'}</p>
						</div>
						<div class="rounded bg-gray-50 p-2">
							<p class="text-sm text-gray-500">Berat Badan</p>
							<p class="font-semibold text-gray-800">{selectedAnak.berat_badan ?? '-'}</p>
						</div>
						<div class="rounded bg-gray-50 p-2">
							<p class="text-sm text-gray-500">Lingkar Kepala</p>
							<p class="font-semibold text-gray-800">{selectedAnak.lingkar_kepala ?? '-'}</p>
						</div>
						<div class="rounded bg-gray-50 p-2">
							<p class="text-sm text-gray-500">Lingkar Lengan</p>
							<p class="font-semibold text-gray-800">{selectedAnak.lingkar_lengan ?? '-'}</p>
						</div>
					</div>

					<div class="mb-4">
						<h3 class="text-md mb-2 text-left font-semibold">Hasil Analisis Status Gizi</h3>
						<div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
							{#each ['BB/U','IMT/U','LILA/U','LK/U','TB/U'] as key}
								<div class="rounded bg-green-50 p-2">
									<p class="text-sm text-gray-500">{key}</p>
									<p class="font-semibold text-gray-800">{selectedAnak.hasil?.[key]?.kategori ?? '-'}</p>
								</div>
							{/each}
						</div>
					</div>

					<button
						on:click={() => lihatDetail(selectedAnak)}
						class="rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white shadow-md transition hover:bg-blue-700"
					>
						Lihat Detail
					</button>
				{:else}
					<p>Silakan pilih anak untuk melihat data pengukuran dan status gizi</p>
				{/if}
			</div>

			<!-- CARD-B -->
			<div class="flex flex-1 grow flex-col flex-nowrap gap-4 overflow-y-auto scroll-smooth pb-6 pt-1">
				{#each anakList as anak}
					<div
						class="card-B relative cursor-pointer bg-white text-center"
						on:click={() => tampilkanGrafik(anak)}
					>
						<button
							class="btn-riwayat absolute right-3 top-3 rounded-full bg-sky-500 px-3 py-1 text-sm text-white hover:bg-sky-600"
							on:click={(e) => riwayatAnak(anak, e)}
						>
							Riwayat
						</button>
						<p class="mt-3 text-lg font-bold text-gray-800">{anak.nama}</p>
						<p class="mt-1 text-sm text-gray-600">Usia: {hitungUsia(anak.tanggal_lahir)}</p>
						<p class="mt-1 text-sm font-semibold text-blue-700">{anak.status || 'Normal'}</p>
					</div>
				{/each}
			</div>
		</div>
	</div>

	<!-- 🔹 MOBILE VIEW -->
	{#if selectedAnak}
		<div
			class="mb-2 block cursor-pointer rounded-xl bg-white p-4 shadow transition hover:bg-blue-50 sm:hidden"
			on:click={() => tampilkanGrafik(selectedAnak)}
		>
			<p class="font-semibold text-gray-800">{selectedAnak.nama}</p>
			<p class="text-sm text-gray-500">Usia: {hitungUsia(selectedAnak.tanggal_lahir)}</p>
			<p class="mt-1 inline-block rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800">
				{selectedAnak.status || 'Normal'}
			</p>
		</div>

		<div class="card-grafik block rounded-xl bg-white p-4 shadow-md sm:hidden relative">
			{#if isLoadingPengukuran}
				<div class="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
					<div class="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
				</div>
			{/if}

			<p class="mb-4 text-lg font-semibold">{selectedAnak.nama} - Pengukuran Terakhir</p>

			<div class="mb-4 grid grid-cols-2 gap-2">
				{#each [
					['Tinggi Badan', selectedAnak.tinggi_badan],
					['Berat Badan', selectedAnak.berat_badan],
					['Lingkar Kepala', selectedAnak.lingkar_kepala],
					['Lingkar Lengan', selectedAnak.lingkar_lengan]
				] as [label, val]}
					<div class="rounded bg-gray-50 p-2">
						<p class="text-sm text-gray-500">{label}</p>
						<p class="font-semibold text-gray-800">{val ?? '-'}</p>
					</div>
				{/each}
			</div>

			<div class="mb-4">
				<h3 class="text-md mb-2 text-left font-semibold">Hasil Analisis Status Gizi</h3>
				<div class="grid grid-cols-2 gap-2">
					{#each ['BB/U','IMT/U','LILA/U','LK/U','TB/U'] as key}
						<div class="rounded bg-green-50 p-2">
							<p class="text-sm text-gray-500">{key}</p>
							<p class="font-semibold text-gray-800">{selectedAnak.hasil?.[key]?.kategori ?? '-'}</p>
						</div>
					{/each}
				</div>
			</div>

			<button
				on:click={() => lihatDetail(selectedAnak)}
				class="w-full rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white shadow-md transition hover:bg-blue-700"
			>
				Lihat Detail
			</button>
		</div>
	{:else}
		<p class="text-center text-gray-600 sm:hidden">
			Silakan pilih anak untuk melihat data pengukuran dan status gizi
		</p>
	{/if}
</div>
