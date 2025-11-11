<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	let ApexCharts: any;

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
	let ai_analysis: Record<string, any> = {};
	let loading = true;
	let role = '';
	let id_anak = '';

	const BACKEND_URL = `${PUBLIC_BACKEND_URL}/iot`;

	let activeChart: 'berat' | 'tinggi' | 'imt' | 'lila' | 'lk' = 'berat';
	let activeRange: 'monthly' | 'yearly' = 'monthly';
	let grafikData: any = null;
	let chartInstance: any = null;

	// ---------- UTIL FUNGI ----------
	function hitungUmurBulan(tanggal_lahir: string) {
		if (!tanggal_lahir || tanggal_lahir === '-') return '-';
		const lahir = new Date(tanggal_lahir);
		if (isNaN(lahir.getTime())) return '-';
		const sekarang = new Date();
		return (
			(sekarang.getFullYear() - lahir.getFullYear()) * 12 +
			(sekarang.getMonth() - lahir.getMonth())
		);
	}

	function safeNumber(v: any): number | null {
		if (v === null || v === undefined) return null;
		if (typeof v === 'number' && Number.isFinite(v)) return v;

		const s = String(v).trim();
		if (!s || s === '-' || s.toLowerCase() === 'null' || s.toLowerCase() === 'nan') return null;

		const parsed = Number(s.replace(/,/g, ''));
		return Number.isFinite(parsed) ? parsed : null;
	}

	function formatCategory(cat: string) {
		if (!cat) return '';
		const parts = cat.split('-');
		if (parts.length >= 2) {
			const y = +parts[0];
			const m = +parts[1] - 1;
			const d = parts[2] ? +parts[2] : 1;
			if (isNaN(y) || isNaN(m)) return cat;
			return new Date(y, m, d).toLocaleString('id-ID', { month: 'short', year: 'numeric' });
		}
		return cat;
	}

	function reduceMonthlyToLatest(categories: string[], values: (number | null)[]) {
		const map: Record<string, { dateRaw: string; value: number | null }> = {};
		for (let i = 0; i < categories.length; i++) {
			const c = categories[i];
			if (!c) continue;
			const monthKey = c.split('-').slice(0, 2).join('-');
			const currentDate = new Date(c);
			const existing = map[monthKey];
			if (!existing || currentDate > new Date(existing.dateRaw)) {
				map[monthKey] = { dateRaw: c, value: values[i] ?? null };
			}
		}
		const keys = Object.keys(map).sort();
		return { categories: keys, values: keys.map((k) => map[k].value) };
	}

	// ---------- DATA LOAD ----------
	async function loadData() {
		loading = true;
		try {
			const [resDetail, resGrafik] = await Promise.all([
				fetch(`${BACKEND_URL}/api/pengukuran/detail/${id_anak}`),
				fetch(`${BACKEND_URL}/api/pengukuran/${id_anak}/grafik`)
			]);

			if (resDetail.ok) {
				const d = await resDetail.json();
				anak = {
					nama: d?.anak?.nama ?? '-',
					jenis_kelamin: d?.anak?.jenis_kelamin ?? '-',
					tanggal_lahir: d?.anak?.tanggal_lahir ?? '-',
					umur_bulan: hitungUmurBulan(d?.anak?.tanggal_lahir)
				};
				peng = {
					berat_badan: d?.peng?.berat_badan ?? '-',
					tinggi_badan: d?.peng?.tinggi_badan ?? '-',
					lingkar_kepala: d?.peng?.lingkar_kepala ?? '-',
					lingkar_lengan: d?.peng?.lingkar_lengan ?? '-',
					created_at: d?.peng?.created_at
						? new Date(d.peng.created_at).toLocaleDateString('id-ID', {
								year: 'numeric',
								month: 'long',
								day: 'numeric'
						  })
						: '-'
				};
				hasil = d?.hasil ?? {};
				ai_analysis = d?.ai_analysis ?? {};
			}

			if (resGrafik.ok) {
				const gd = await resGrafik.json();
				const sanitize = (arr: any[]) =>
					Array.isArray(arr) ? arr.map((v) => safeNumber(v)) : [];

				grafikData = {
					monthly: {
						categories: gd.monthly?.categories?.map(String) ?? [],
						berat: sanitize(gd.monthly?.berat ?? []),
						tinggi: sanitize(gd.monthly?.tinggi ?? []),
						imt: sanitize(gd.monthly?.imt ?? []),
						lila: sanitize(gd.monthly?.lila ?? []),
						lk: sanitize(gd.monthly?.lk ?? [])
					},
					yearly: {
						categories: gd.yearly?.categories?.map(String) ?? [],
						berat: sanitize(gd.yearly?.berat ?? []),
						tinggi: sanitize(gd.yearly?.tinggi ?? []),
						imt: sanitize(gd.yearly?.imt ?? []),
						lila: sanitize(gd.yearly?.lila ?? []),
						lk: sanitize(gd.yearly?.lk ?? [])
					}
				};
			} else grafikData = null;
		} catch (e) {
			console.error('loadData error:', e);
			grafikData = null;
		} finally {
			loading = false;
			renderChart();
		}
	}

	// ---------- CHART ----------
	function buildOptions(categories: string[], seriesName: string, data: (number | null)[], yLabel: string) {
		return {
			chart: { type: 'line', height: 320, toolbar: { show: true } },
			colors: ['#2d626a'],
			stroke: { width: 3, curve: 'smooth' },
			series: [{ name: seriesName, data }],
			xaxis: { categories: categories.map(formatCategory), labels: { rotate: -45 } },
			yaxis: { title: { text: yLabel } },
			markers: { size: 4 },
			tooltip: {
				y: { formatter: (val: any) => (val == null ? '-' : val) }
			},
			title: {
				text: `${seriesName} ${activeRange === 'monthly' ? '(per bulan)' : '(rata-rata per tahun)'}`,
				align: 'left',
				style: { fontSize: '14px' }
			}
		};
	}

	function destroyChartInstance() {
		if (chartInstance) {
			try {
				chartInstance.destroy();
			} catch {}
			chartInstance = null;
		}
	}

	function renderChart() {
		if (!ApexCharts) return;
		destroyChartInstance();
		const container = document.querySelector('#chart-area') as HTMLElement;
		if (!container) return;
		container.innerHTML = '';

		if (!grafikData) {
			container.innerHTML = `<div class="p-6 text-gray-500 text-center">Belum ada data grafik</div>`;
			return;
		}

		const dataSrc = grafikData[activeRange];
		if (!dataSrc) return;

		let arr: (number | null)[] = [];
		let label = '';
		let name = '';

		switch (activeChart) {
			case 'berat':
				arr = dataSrc.berat;
				name = 'Berat Badan';
				label = 'kg';
				break;
			case 'tinggi':
				arr = dataSrc.tinggi;
				name = 'Tinggi Badan';
				label = 'cm';
				break;
			case 'imt':
				arr = dataSrc.imt;
				name = 'IMT';
				label = 'IMT';
				break;
			case 'lila':
				arr = dataSrc.lila;
				name = 'Lingkar Lengan';
				label = 'cm';
				break;
			case 'lk':
				arr = dataSrc.lk;
				name = 'Lingkar Kepala';
				label = 'cm';
				break;
		}

		let cats = dataSrc.categories;
		if (activeRange === 'monthly') {
			const reduced = reduceMonthlyToLatest(cats, arr);
			cats = reduced.categories;
			arr = reduced.values;
		}

		const opts = buildOptions(cats, name, arr, label);
		chartInstance = new ApexCharts(container, opts);
		chartInstance.render();
	}

	// ---------- HANDLER ----------
	function setChart(type: typeof activeChart) {
		activeChart = type;
		renderChart();
	}

	function setRange(range: typeof activeRange) {
		activeRange = range;
		renderChart();
	}

	onMount(async () => {
		ApexCharts = (await import('apexcharts')).default;
		const params = new URLSearchParams(window.location.search);
		role = params.get('role') || 'orangtua';
		id_anak = params.get('id') || sessionStorage.getItem('selected_anak_id') || '1';
		await loadData();
	});

	onDestroy(() => {
		destroyChartInstance();
	});

	function kembali() {
		if (window.history.length > 1) window.history.back();
		else {
			const key = role === 'perawat' ? 'id_perawat' : 'id_orangtua';
			const id = sessionStorage.getItem(key);
			goto(`/dashboard-${role}?id=${id}`);
		}
	}

	function bukaRiwayat() {
		goto(`/riwayat?id=${id_anak}`);
	}

	function getStatusColor(status: string) {
		switch (status?.toLowerCase()) {
			case 'sangat baik':
			case 'baik':
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

	<!-- container utama -->
	<div class="flex flex-1 flex-col gap-3 sm:flex-row">
		<!-- card informasi (TIDAK DIUBAH selain isi data) -->
		<div class="flex w-full flex-1 flex-col gap-2 rounded-xl">
			<div class="card-B w-full bg-white p-4">
				<p>Nama: {anak.nama}</p>
				<p>Jenis kelamin: {anak.jenis_kelamin}</p>
				<p>Usia (bulan): {anak.umur_bulan}</p>
				<p>Pengukuran terakhir: {peng.created_at}</p>
			</div>

			<h2 class="mt-4">Data Pengukuran</h2>
			{#if peng.berat_badan === '-' && peng.tinggi_badan === '-' && peng.lingkar_kepala === '-' && peng.lingkar_lengan === '-'}
				<div class="card-B w-full bg-white p-6 text-center text-gray-500">
					Belum ada data pengukuran
				</div>
			{:else}
				<div class="card-B w-full bg-white p-4">
					<p>Tinggi badan: {peng.tinggi_badan}</p>
					<p>Berat badan: {peng.berat_badan}</p>
					<p>Lingkar kepala: {peng.lingkar_kepala}</p>
					<p>Lingkar lengan atas: {peng.lingkar_lengan}</p>
				</div>
			{/if}

			<h2 class="mt-4">Hasil Analisis Status Gizi</h2>
			{#if Object.keys(hasil).length === 0}
				<div class="card-B w-full bg-white p-6 text-center text-gray-500">
					Belum ada hasil analisis
				</div>
			{:else}
				<div class="card-B w-full bg-white p-4">
					<p>BB/U: {hasil['BB/U']?.kategori ?? '-'}</p>
					<p>IMT/U: {hasil['IMT/U']?.kategori ?? '-'}</p>
					<p>LILA/U: {hasil['LILA/U']?.kategori ?? '-'}</p>
					<p>LK/U: {hasil['LK/U']?.kategori ?? '-'}</p>
					<p>TB/U: {hasil['TB/U']?.kategori ?? '-'}</p>
				</div>
			{/if}
		</div>

		<!-- grafik (DIISI: jangan ubah nama/id container agar mudah ditemukan) -->
		<div class="flex-2 flex flex-col gap-2">
			<h2 class="block sm:hidden">Grafik Anak</h2>

			<div class="card-A bg-white p-4">
				<!-- Controls -->
				<div class="mb-4 flex flex-wrap gap-2">
					<!-- chart type buttons -->
					<button
						class={`rounded px-3 py-2 ${activeChart === 'berat' ? 'bg-[#2d626a] text-white' : 'bg-gray-100 text-gray-700'}`}
						on:click={() => setChart('berat')}
					>
						Grafik Berat
					</button>

					<button
						class={`rounded px-3 py-2 ${activeChart === 'tinggi' ? 'bg-[#2d626a] text-white' : 'bg-gray-100 text-gray-700'}`}
						on:click={() => setChart('tinggi')}
					>
						Grafik Tinggi
					</button>

					<button
						class={`rounded px-3 py-2 ${activeChart === 'imt' ? 'bg-[#2d626a] text-white' : 'bg-gray-100 text-gray-700'}`}
						on:click={() => setChart('imt')}
					>
						Grafik IMT
					</button>

					<button
						class={`rounded px-3 py-2 ${activeChart === 'lila' ? 'bg-[#2d626a] text-white' : 'bg-gray-100 text-gray-700'}`}
						on:click={() => setChart('lila')}
					>
						Grafik LILA
					</button>

					<button
						class={`rounded px-3 py-2 ${activeChart === 'lk' ? 'bg-[#2d626a] text-white' : 'bg-gray-100 text-gray-700'}`}
						on:click={() => setChart('lk')}
					>
						Grafik LK
					</button>

					<div class="flex-1"></div>

					<!-- range toggle -->
					<button
						class={`rounded px-3 py-2 ${activeRange === 'monthly' ? 'bg-[#428a91] text-white' : 'bg-gray-100 text-gray-700'}`}
						on:click={() => setRange('monthly')}
					>
						Monthly
					</button>
					<button
						class={`rounded px-3 py-2 ${activeRange === 'yearly' ? 'bg-[#428a91] text-white' : 'bg-gray-100 text-gray-700'}`}
						on:click={() => setRange('yearly')}
					>
						Yearly
					</button>
				</div>

				<!-- Chart container (id digunakan di renderChart) -->
				<div id="chart-area" class="w-full"></div>
			</div>

			<!-- Analisis AI -->
			<h2 class="block sm:hidden">Analisis AI</h2>
			<div class="card-A bg-white p-6">
				{#if loading}
					<div class="text-center">Memuat analisis AI...</div>
				{:else if !ai_analysis || Object.keys(ai_analysis).length === 0}
					<div class="text-center text-gray-500">Belum ada analisis AI</div>
				{:else}
					<div class="space-y-4">
						<div class="border-b pb-3">
							<h3 class="mb-2 text-lg font-semibold">Status Perkembangan</h3>
							<div
								class="inline-block rounded-full px-3 py-1 {getStatusColor(
									ai_analysis.status_perkembangan
								)}"
							>
								{ai_analysis.status_perkembangan || 'Tidak tersedia'}
							</div>
						</div>

						<div class="border-b pb-3">
							<h3 class="mb-2 text-lg font-semibold">Analisis Umum</h3>
							<p class="leading-relaxed text-gray-700">
								{ai_analysis.analisis_umum || ai_analysis.ringkasan || 'Tidak ada analisis umum'}
							</p>
						</div>

						{#if ai_analysis.area_perhatian && ai_analysis.area_perhatian.length > 0}
							<div class="border-b pb-3">
								<h3 class="mb-2 text-lg font-semibold">Area Perhatian</h3>
								<ul class="list-inside list-disc space-y-1">
									{#each ai_analysis.area_perhatian as area}
										<li class="text-gray-700">{area}</li>
									{/each}
								</ul>
							</div>
						{/if}

						{#if ai_analysis.rekomendasi && ai_analysis.rekomendasi.length > 0}
							<div class="border-b pb-3">
								<h3 class="mb-2 text-lg font-semibold">Rekomendasi</h3>
								<ul class="list-inside list-disc space-y-1">
									{#each ai_analysis.rekomendasi as rekomendasi}
										<li class="text-gray-700">{rekomendasi}</li>
									{/each}
								</ul>
							</div>
						{/if}

						{#if ai_analysis.saran_pemantauan}
							<div>
								<h3 class="mb-2 text-lg font-semibold">Saran Pemantauan</h3>
								<p class="leading-relaxed text-gray-700">{ai_analysis.saran_pemantauan}</p>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</div>

	<!-- tombol -->
	<div class="mt-6 flex gap-4">
		<button class="btn-A bg-gray-500 text-white" on:click={kembali}>Kembali</button>
		<button class="btn-A ml-auto bg-blue-500 text-white" on:click={bukaRiwayat}>Riwayat</button>
	</div>
</div>

<style>
	/* sedikit style tombol chart (opsional, tailwind tetap utama) */
	.btn-A {
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
	}
	.card-A {
		border-radius: 0.75rem;
		box-shadow: 0 2px 6px rgba(16, 24, 40, 0.04);
	}
	.card-B {
		border-radius: 0.5rem;
		box-shadow: 0 1px 4px rgba(16, 24, 40, 0.04);
	}
</style>
