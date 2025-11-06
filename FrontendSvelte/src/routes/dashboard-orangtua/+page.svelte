<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let anakList: any[] = [];
	let id_orang_tua: string | null = null;
	let isLoading = true;
	let selectedAnak: any = null;

	function decodeJWT(token: string) {
		try {
			return JSON.parse(atob(token.split(".")[1]));
		} catch {
			return null;
		}
	}

	function cekToken() {
		const token = localStorage.getItem("token");
		if (!token) {
			alert("Anda belum login!");
			goto("/login");
			return null;
		}
		const payload = decodeJWT(token);
		if (!payload || !payload.user_id) {
			alert("Sesi tidak valid, silakan login ulang.");
			goto("/login");
			return null;
		}
		return token;
	}

	onMount(async () => {
		const token = cekToken();
		if (!token) return;

		id_orang_tua = decodeJWT(token).user_id;

		try {
			const res = await fetch(
				`http://127.0.0.1:5000/iot/api/anak-by-orangtua/${id_orang_tua}`,
				{ headers: { Authorization: "Bearer " + token } }
			);

			const data = await res.json();
			anakList = data;

			if (anakList.length > 0) {
				anakList.sort((a, b) => a.id_anak - b.id_anak);
				selectedAnak = anakList[0];
			}
		} catch (err) {
			console.error("Gagal memuat data anak:", err);
		} finally {
			isLoading = false;
		}
	});

	function hitungUsia(tanggal_lahir: string) {
		if (!tanggal_lahir) return '-';
		const tglLahir = new Date(tanggal_lahir);
		const sekarang = new Date();
		let tahun = sekarang.getFullYear() - tglLahir.getFullYear();
		let bulan = sekarang.getMonth() - tglLahir.getMonth();
		if (bulan < 0) {
			tahun--;
			bulan += 12;
		}
		return `${tahun} th ${bulan} bln`;
	}

	// ================= NAVIGASI DENGAN JWT =================
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

	<!-- MOBILE DROPDOWN -->
	<script src="https://cdn.jsdelivr.net/npm/@tailwindplus/elements@1" type="module"></script>
	<el-dropdown class="mb-2 block inline-block w-full sm:hidden">
		<button
			class="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-blue-500 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-blue-600"
		>
			{selectedAnak ? selectedAnak.nama : 'Pilih Anak'}
			<svg viewBox="0 0 20 20" fill="currentColor" class="-mr-1 size-5 text-gray-200">
				<path fill-rule="evenodd" clip-rule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"/>
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

	<!-- DESKTOP & MOBILE CARDS -->
	<div class="hidden sm:block">
		<div class="flex h-[60vh] gap-4">
			<!-- GRAFIK -->
			<div class="card-A flex-3 bg-white text-center">
				{#if selectedAnak}
					<p class="mb-4 text-lg font-semibold">Grafik {selectedAnak.nama}</p>
					<button
						on:click={() => lihatDetail(selectedAnak)}
						class="rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white shadow-md transition hover:bg-blue-700"
					>
						Lihat Detail
					</button>
				{:else}
					<p>Silakan pilih anak untuk melihat grafik</p>
				{/if}
			</div>

			<!-- CARD ANAK -->
			<div class="flex flex-1 grow flex-col flex-nowrap gap-4 overflow-x-hidden overflow-y-auto scroll-smooth pt-1 pb-6 [-ms-overflow-style:none] [scrollbar-width:none]">
				{#each anakList as anak}
					<div
						class="bg-white card-B hidden cursor-pointer text-center sm:block"
						on:click={() => tampilkanGrafik(anak)}
					>
						<button
							class="btn-riwayat absolute top-3 right-3 rounded-full bg-sky-500 px-3 py-1 text-sm text-white hover:bg-sky-600"
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

	<!-- MOBILE GRAFIK -->
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

		<div class="card-grafik block rounded-xl bg-white p-6 text-center shadow-md sm:hidden">
			<p class="mb-4 text-lg font-semibold">Grafik {selectedAnak.nama}</p>
			<button
				on:click={() => lihatDetail(selectedAnak)}
				class="rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white shadow-md transition hover:bg-blue-700"
			>
				Lihat Detail
			</button>
		</div>
	{/if}
</div>


<style>
	.container-anak {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
	}
</style>
