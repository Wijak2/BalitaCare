<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let anak = {
		nama: '-',
		jenis_kelamin: '-',
		tanggal_lahir: '-',
		umur_bulan: '-'
	};

	let peng = {
		berat_badan: '-',
		tinggi_badan: '-',
		lingkar_kepala: '-',
		lingkar_lengan: '-',
		created_at: '-'
	};

	let hasil: Record<string, any> = {};
	let ai_analysis: any = {}; // 🔥 Diubah dari string ke object
	let loading = true;
	let role = '';
	let id_anak = '';

	const BACKEND_URL = 'http://localhost:5000/iot';

	function hitungUmurBulan(tanggal_lahir: string) {
		if (!tanggal_lahir || tanggal_lahir === '-') return '-';
		const lahir = new Date(tanggal_lahir);
		if (isNaN(lahir.getTime())) return '-';
		const sekarang = new Date();
		return (
			(sekarang.getFullYear() - lahir.getFullYear()) * 12 + (sekarang.getMonth() - lahir.getMonth())
		);
	}

	onMount(async () => {
		const params = new URLSearchParams(window.location.search);
		role = params.get('role') || 'orangtua';
		id_anak = params.get('id') || sessionStorage.getItem('selected_anak_id') || '1';

		try {
			const res = await fetch(`${BACKEND_URL}/api/pengukuran/detail/${id_anak}`);
			if (!res.ok) throw new Error(`HTTP ${res.status}`);
			const data = await res.json();

			anak = {
				nama: data?.anak?.nama ?? '-',
				jenis_kelamin: data?.anak?.jenis_kelamin ?? '-',
				tanggal_lahir: data?.anak?.tanggal_lahir ?? '-',
				umur_bulan: hitungUmurBulan(data?.anak?.tanggal_lahir)
			};

			peng = {
				berat_badan: data?.peng?.berat_badan ?? '-',
				tinggi_badan: data?.peng?.tinggi_badan ?? '-',
				lingkar_kepala: data?.peng?.lingkar_kepala ?? '-',
				lingkar_lengan: data?.peng?.lingkar_lengan ?? '-',
				created_at: data?.peng?.created_at
					? new Date(data.peng.created_at).toLocaleDateString('id-ID', {
							year: 'numeric',
							month: 'long',
							day: 'numeric'
						})
					: '-'
			};

			hasil = data?.hasil ?? {};
			
			// 🔥 PERUBAHAN: ai_analysis sekarang object, bukan string
			ai_analysis = data?.ai_analysis ?? {};
			
		} catch (err) {
			console.error('🔥 Error fetch detail pengukuran:', err);
		} finally {
			loading = false;
		}
	});

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

	function bukaRiwayat() {
		goto(`/riwayat?id=${id_anak}`);
	}

	// 🔥 FUNGSI BARU: Untuk mendapatkan class warna berdasarkan status perkembangan
	function getStatusColor(status: string) {
		switch (status?.toLowerCase()) {
			case 'sangat baik':
				return 'text-green-600 bg-green-100';
			case 'baik':
				return 'text-blue-600 bg-blue-100';
			case 'normal':
				return 'text-green-600 bg-green-100';
			case 'perlu perhatian':
				return 'text-yellow-600 bg-yellow-100';
			case 'berisiko':
				return 'text-red-600 bg-red-100';
			default:
				return 'text-gray-600 bg-gray-100';
		}
	}
</script>

<div class="page-wrapper">
	<h1 class="mb-4 text-4xl font-extrabold">Informasi anak</h1>

	<div class="flex flex-1 flex-col gap-3 sm:flex-row">

		<div class="flex w-full flex-1 flex-col gap-2 rounded-xl">
			<div class="card-B w-full bg-white">
				<p>Nama: {anak.nama}</p>
				<p>Jenis kelamin: {anak.jenis_kelamin}</p>
				<p>Usia (bulan): {anak.umur_bulan}</p>
				<p>Pengukuran terakhir: {peng.created_at}</p>
			</div>

			<h2>Data Pengukuran</h2>
			{#if peng.berat_badan === '-' && peng.tinggi_badan === '-' && peng.lingkar_kepala === '-' && peng.lingkar_lengan === '-'}
				<div class="card-B w-full bg-white text-center text-gray-500">
					Belum ada data pengukuran
				</div>
			{:else}
				<div class="card-B w-full bg-white">
					<p>Tinggi badan: {peng.tinggi_badan}</p>
					<p>Berat badan: {peng.berat_badan}</p>
					<p>Lingkar kepala: {peng.lingkar_kepala}</p>
					<p>Lingkar lengan atas: {peng.lingkar_lengan}</p>
				</div>
			{/if}

			<h2>Hasil Analisis Status Gizi</h2>
			{#if Object.keys(hasil).length === 0}
				<div class="card-B w-full bg-white text-center text-gray-500">Belum ada hasil analisis</div>
			{:else}
				<div class="card-B w-full bg-white">
					<p>BB/U: {hasil['BB/U']?.kategori ?? '-'}</p>
					<p>IMT/U: {hasil['IMT/U']?.kategori ?? '-'}</p>
					<p>LILA/U: {hasil['LILA/U']?.kategori ?? '-'}</p>
					<p>LK/U: {hasil['LK/U']?.kategori ?? '-'}</p>
					<p>TB/U: {hasil['TB/U']?.kategori ?? '-'}</p>
				</div>
			{/if}
		</div>

		<div class="flex flex-2 flex-col gap-2">
			<h2 class="block sm:hidden">Grafik Anak</h2>
			<div class="card-A h-70 bg-white text-center">
				{loading ? 'Memuat grafik...' : 'grafik anak'}
			</div>
			
			<!--  PERUBAHAN: Bagian Analisis AI yang diperbarui -->
			<h2 class="block sm:hidden">Analisis AI</h2>
			<div class="card-A bg-white p-6">
				{#if loading}
					<div class="text-center">Memuat analisis AI...</div>
				{:else if Object.keys(ai_analysis).length === 0}
					<div class="text-center text-gray-500">Belum ada analisis AI</div>
				{:else}
					<div class="space-y-4">
						<!-- Status Perkembangan -->
						<div class="border-b pb-3">
							<h3 class="text-lg font-semibold mb-2">Status Perkembangan</h3>
							<div class="inline-block px-3 py-1 rounded-full {getStatusColor(ai_analysis.status_perkembangan)}">
								{ai_analysis.status_perkembangan || 'Tidak tersedia'}
							</div>
						</div>

						<!-- Analisis Umum -->
						<div class="border-b pb-3">
							<h3 class="text-lg font-semibold mb-2">Analisis Umum</h3>
							<p class="text-gray-700 leading-relaxed">
								{ai_analysis.analisis_umum || ai_analysis.ringkasan || 'Tidak ada analisis umum'}
							</p>
						</div>

						<!-- Area Perhatian -->
						{#if ai_analysis.area_perhatian && ai_analysis.area_perhatian.length > 0}
							<div class="border-b pb-3">
								<h3 class="text-lg font-semibold mb-2">Area Perhatian</h3>
								<ul class="list-disc list-inside space-y-1">
									{#each ai_analysis.area_perhatian as area}
										<li class="text-gray-700">{area}</li>
									{/each}
								</ul>
							</div>
						{/if}

						<!-- Rekomendasi -->
						{#if ai_analysis.rekomendasi && ai_analysis.rekomendasi.length > 0}
							<div class="border-b pb-3">
								<h3 class="text-lg font-semibold mb-2">Rekomendasi</h3>
								<ul class="list-disc list-inside space-y-1">
									{#each ai_analysis.rekomendasi as rekomendasi}
										<li class="text-gray-700">{rekomendasi}</li>
									{/each}
								</ul>
							</div>
						{/if}

						<!-- Saran Pemantauan -->
						{#if ai_analysis.saran_pemantauan}
							<div>
								<h3 class="text-lg font-semibold mb-2">Saran Pemantauan</h3>
								<p class="text-gray-700 leading-relaxed">{ai_analysis.saran_pemantauan}</p>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="mt-6 flex gap-4">
		<button class="btn-A bg-gray-500 text-white" on:click={kembali}>Kembali</button>
		<button class="btn-A ml-auto bg-blue-500 text-white" on:click={bukaRiwayat}>Riwayat</button>
	</div>
</div>