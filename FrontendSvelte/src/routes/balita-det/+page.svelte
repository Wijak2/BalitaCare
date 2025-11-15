<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	// Shadcn-svelte components
	import {
		Card,
		CardContent,
		CardDescription,
		CardFooter,
		CardHeader,
		CardTitle
	} from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import { Separator } from '$lib/components/ui/separator';
	import { Alert, AlertDescription, AlertTitle } from '$lib/components/ui/alert';
	import {
		ArrowLeft,
		Calendar,
		Activity,
		BarChart3,
		Brain,
		FileText,
		TrendingUp
	} from 'lucide-svelte';

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
			(sekarang.getFullYear() - lahir.getFullYear()) * 12 + (sekarang.getMonth() - lahir.getMonth())
		);
	}

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
		return `${tahun} tahun ${bulan} bulan`;
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
				const sanitize = (arr: any[]) => (Array.isArray(arr) ? arr.map((v) => safeNumber(v)) : []);

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
			// Use setTimeout to ensure DOM is ready before rendering chart
			setTimeout(() => renderChart(), 100);
		}
	}

	// ---------- CHART ----------
	function buildOptions(
		categories: string[],
		seriesName: string,
		data: (number | null)[],
		yLabel: string
	) {
		return {
			chart: {
				type: 'line',
				height: 320,
				toolbar: { show: true },
				animations: {
					enabled: true,
					easing: 'easeinout',
					speed: 800,
					animateGradually: {
						enabled: true,
						delay: 150
					},
					dynamicAnimation: {
						enabled: true,
						speed: 350
					}
				}
			},
			colors: ['#2d626a'],
			stroke: { width: 3, curve: 'smooth' },
			series: [{ name: seriesName, data }],
			xaxis: {
				categories: categories.map(formatCategory),
				labels: { rotate: -45 }
			},
			yaxis: { title: { text: yLabel } },
			markers: { size: 4 },
			tooltip: {
				y: { formatter: (val: any) => (val == null ? '-' : val) }
			},
			title: {
				text: `${seriesName} ${activeRange === 'monthly' ? '(per bulan)' : '(rata-rata per tahun)'}`,
				align: 'left',
				style: { fontSize: '14px' }
			},
			noData: {
				text: 'Belum ada data grafik',
				align: 'center',
				verticalAlign: 'middle',
				style: {
					color: '#6B7280',
					fontSize: '14px'
				}
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

		// Find the chart container with a more specific selector
		const container = document.querySelector('#chart-area') as HTMLElement;
		if (!container) {
			console.error('Chart container not found');
			return;
		}

		// Clear any existing content
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
		// Use setTimeout to ensure DOM is ready before rendering chart
		setTimeout(() => renderChart(), 50);
	}

	function setRange(range: typeof activeRange) {
		activeRange = range;
		// Use setTimeout to ensure DOM is ready before rendering chart
		setTimeout(() => renderChart(), 50);
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

	function getStatusVariant(status: string) {
		switch (status?.toLowerCase()) {
			case 'sangat baik':
			case 'baik':
			case 'normal':
				return 'default';
			case 'perlu perhatian':
				return 'secondary';
			case 'berisiko':
				return 'destructive';
			default:
				return 'outline';
		}
	}
</script>

<div class="container mx-auto space-y-6 py-6">
	<!-- Header with Buttons - Moved to the right side -->
	<div class="flex items-center justify-between gap-4">
		<h1 class="text-3xl font-bold tracking-tight">Detail Balita</h1>
	</div>

	{#if loading}
		<div class="space-y-6">
			<Card>
				<CardHeader>
					<Skeleton class="h-8 w-48" />
				</CardHeader>
				<CardContent class="space-y-2">
					<Skeleton class="h-4 w-full" />
					<Skeleton class="h-4 w-full" />
					<Skeleton class="h-4 w-full" />
				</CardContent>
			</Card>
			<Card>
				<CardHeader>
					<Skeleton class="h-8 w-48" />
				</CardHeader>
				<CardContent>
					<Skeleton class="h-64 w-full" />
				</CardContent>
			</Card>
		</div>
	{:else}
		<!-- Main Content -->
		<div class="grid gap-6 lg:grid-cols-3">
			<!-- Left Column: Child Info -->
			<div class="space-y-6 lg:col-span-2">
				<!-- Child Info Card -->
				<Card>
					<CardHeader>
						<div class="flex items-center justify-between">
							<div>
								<CardTitle class="text-2xl">{anak.nama}</CardTitle>
								<CardDescription class="mt-1 flex items-center">
									<Calendar class="mr-1 h-4 w-4" />
									{hitungUsia(anak.tanggal_lahir)}
								</CardDescription>
							</div>
							<Badge variant={getStatusVariant(hasil?.status || 'Normal')}>
								{hasil?.status || 'Normal'}
							</Badge>
						</div>
					</CardHeader>
					<CardContent>
						<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
							<div class="space-y-1">
								<p class="text-muted-foreground text-sm font-medium">Jenis Kelamin</p>
								<p class="text-sm font-bold">{anak.jenis_kelamin}</p>
							</div>
							<div class="space-y-1">
								<p class="text-muted-foreground text-sm font-medium">Tanggal Lahir</p>
								<p class="text-sm font-bold">{anak.tanggal_lahir}</p>
							</div>
							<div class="space-y-1">
								<p class="text-muted-foreground text-sm font-medium">Umur (bulan)</p>
								<p class="text-sm font-bold">{anak.umur_bulan}</p>
							</div>
							<div class="space-y-1">
								<p class="text-muted-foreground text-sm font-medium">Pengukuran Terakhir</p>
								<p class="text-sm font-bold">{peng.created_at}</p>
							</div>
						</div>
					</CardContent>
				</Card>

				<!-- Measurement Data -->
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center">
							<Activity class="mr-2 h-5 w-5" />
							Data Pengukuran
						</CardTitle>
					</CardHeader>
					<CardContent>
						{#if peng.berat_badan === '-' && peng.tinggi_badan === '-' && peng.lingkar_kepala === '-' && peng.lingkar_lengan === '-'}
							<div class="py-6 text-center">
								<Activity class="text-muted-foreground mx-auto mb-4 h-12 w-12" />
								<h3 class="text-lg font-medium">Belum Ada Data Pengukuran</h3>
								<p class="text-muted-foreground mt-1 text-sm">
									Balita ini belum memiliki data pengukuran.
								</p>
							</div>
						{:else}
							<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
								<div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
									<p class="mb-1 text-xs text-gray-500">Tinggi Badan</p>
									<p class="text-xl font-bold text-blue-600">{peng.tinggi_badan}</p>
									<p class="text-xs text-gray-400">cm</p>
								</div>
								<div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
									<p class="mb-1 text-xs text-gray-500">Berat Badan</p>
									<p class="text-xl font-bold text-green-600">{peng.berat_badan}</p>
									<p class="text-xs text-gray-400">kg</p>
								</div>
								<div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
									<p class="mb-1 text-xs text-gray-500">Lingkar Kepala</p>
									<p class="text-xl font-bold text-purple-600">{peng.lingkar_kepala}</p>
									<p class="text-xs text-gray-400">cm</p>
								</div>
								<div class="rounded-lg bg-white p-4 shadow-md ring-1 ring-gray-200">
									<p class="mb-1 text-xs text-gray-500">Lingkar Lengan</p>
									<p class="text-xl font-bold text-orange-600">{peng.lingkar_lengan}</p>
									<p class="text-xs text-gray-400">cm</p>
								</div>
							</div>
						{/if}
					</CardContent>
				</Card>

<!-- Analysis Results - Updated to match the reference design -->
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center">
							<TrendingUp class="mr-2 h-5 w-5" />
							Hasil Analisis Status Gizi
						</CardTitle>
					</CardHeader>
					<CardContent>
						{#if Object.keys(hasil).length === 0}
							<div class="py-6 text-center">
								<TrendingUp class="text-muted-foreground mx-auto mb-4 h-12 w-12" />
								<h3 class="text-lg font-medium">Belum Ada Hasil Analisis</h3>
								<p class="text-muted-foreground mt-1 text-sm">
									Balita ini belum memiliki hasil analisis status gizi.
								</p>
							</div>
						{:else}
							<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
								<div class="rounded-lg border border-green-200 bg-green-50 p-4">
									<p class="mb-1 text-xs font-medium text-gray-600">BB/U</p>
									<p class="text-sm font-semibold text-gray-900">
										{hasil['BB/U']?.kategori ?? '-'}
									</p>
									{#if hasil['BB/U']?.z_score !== undefined && hasil['BB/U']?.z_score !== null}
										<p class="mt-1 text-xs text-gray-500">
											Z-score: {typeof hasil['BB/U'].z_score === 'number' ? hasil['BB/U'].z_score.toFixed(2) : hasil['BB/U'].z_score}
										</p>
									{/if}
								</div>
								<div class="rounded-lg border border-green-200 bg-green-50 p-4">
									<p class="mb-1 text-xs font-medium text-gray-600">IMT/U</p>
									<p class="text-sm font-semibold text-gray-900">
										{hasil['IMT/U']?.kategori ?? '-'}
									</p>
									{#if hasil['IMT/U']?.z_score !== undefined && hasil['IMT/U']?.z_score !== null}
										<p class="mt-1 text-xs text-gray-500">
											Z-score: {typeof hasil['IMT/U'].z_score === 'number' ? hasil['IMT/U'].z_score.toFixed(2) : hasil['IMT/U'].z_score}
										</p>
									{/if}
								</div>
								<div class="rounded-lg border border-green-200 bg-green-50 p-4">
									<p class="mb-1 text-xs font-medium text-gray-600">LILA/U</p>
									<p class="text-sm font-semibold text-gray-900">
										{hasil['LILA/U']?.kategori ?? '-'}
									</p>
									{#if hasil['LILA/U']?.z_score !== undefined && hasil['LILA/U']?.z_score !== null}
										<p class="mt-1 text-xs text-gray-500">
											Z-score: {typeof hasil['LILA/U'].z_score === 'number' ? hasil['LILA/U'].z_score.toFixed(2) : hasil['LILA/U'].z_score}
										</p>
									{/if}
								</div>
								<div class="rounded-lg border border-green-200 bg-green-50 p-4">
									<p class="mb-1 text-xs font-medium text-gray-600">LK/U</p>
									<p class="text-sm font-semibold text-gray-900">
										{hasil['LK/U']?.kategori ?? '-'}
									</p>
									{#if hasil['LK/U']?.z_score !== undefined && hasil['LK/U']?.z_score !== null}
										<p class="mt-1 text-xs text-gray-500">
											Z-score: {typeof hasil['LK/U'].z_score === 'number' ? hasil['LK/U'].z_score.toFixed(2) : hasil['LK/U'].z_score}
										</p>
									{/if}
								</div>
								<div class="rounded-lg border border-green-200 bg-green-50 p-4">
									<p class="mb-1 text-xs font-medium text-gray-600">TB/U</p>
									<p class="text-sm font-semibold text-gray-900">
										{hasil['TB/U']?.kategori ?? '-'}
									</p>
									{#if hasil['TB/U']?.z_score !== undefined && hasil['TB/U']?.z_score !== null}
										<p class="mt-1 text-xs text-gray-500">
											Z-score: {typeof hasil['TB/U'].z_score === 'number' ? hasil['TB/U'].z_score.toFixed(2) : hasil['TB/U'].z_score}
										</p>
									{/if}
								</div>
							</div>
						{/if}
					</CardContent>
				</Card>

				<div class="flex gap-2">
					<button
						class="ring-offset-background focus-visible:ring-ring border-input bg-background hover:bg-accent hover:text-accent-foreground inline-flex h-9 items-center justify-center gap-2 whitespace-nowrap rounded-md border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
						onclick={kembali}
					>
						<ArrowLeft class="h-4 w-4" />
						Kembali
					</button>
					<button
						class="ring-offset-background focus-visible:ring-ring bg-primary text-primary-foreground hover:bg-primary/90 inline-flex h-9 items-center justify-center gap-2 whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
						onclick={bukaRiwayat}
					>
						<FileText class="h-4 w-4" />
						Riwayat Pengukuran
					</button>
				</div>
			</div>

			<!-- Right Column: Charts and AI Analysis -->
			<div class="space-y-6">
				<!-- Growth Charts -->
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center">
							<BarChart3 class="mr-2 h-5 w-5" />
							Grafik Pertumbuhan
						</CardTitle>
					</CardHeader>
					<CardContent>
						<Tabs defaultValue="berat" class="w-full">
							<TabsList class="grid w-full grid-cols-5">
								<TabsTrigger value="berat" onclick={() => setChart('berat')}>BB</TabsTrigger>
								<TabsTrigger value="tinggi" onclick={() => setChart('tinggi')}>TB</TabsTrigger>
								<TabsTrigger value="imt" onclick={() => setChart('imt')}>IMT</TabsTrigger>
								<TabsTrigger value="lila" onclick={() => setChart('lila')}>LILA</TabsTrigger>
								<TabsTrigger value="lk" onclick={() => setChart('lk')}>LK</TabsTrigger>
							</TabsList>

							<!-- Single chart container that's reused for all tabs -->
							<div class="mt-4">
								<div class="mb-4 flex gap-2">
									<button
										class={`ring-offset-background focus-visible:ring-ring inline-flex h-9 items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
											activeRange === 'monthly'
												? 'bg-primary text-primary-foreground hover:bg-primary/90'
												: 'border-input bg-background hover:bg-accent hover:text-accent-foreground border'
										}`}
										onclick={() => setRange('monthly')}
									>
										Bulanan
									</button>
									<button
										class={`ring-offset-background focus-visible:ring-ring inline-flex h-9 items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
											activeRange === 'yearly'
												? 'bg-primary text-primary-foreground hover:bg-primary/90'
												: 'border-input bg-background hover:bg-accent hover:text-accent-foreground border'
										}`}
										onclick={() => setRange('yearly')}
									>
										Tahunan
									</button>
								</div>
								<!-- Chart container with unique ID for ApexCharts -->
								<div id="chart-area" class="w-full"></div>
							</div>
						</Tabs>
					</CardContent>
				</Card>

				<!-- AI Analysis -->
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center">
							<Brain class="mr-2 h-5 w-5" />
							Analisis AI
						</CardTitle>
					</CardHeader>
					<CardContent>
						{#if !ai_analysis || Object.keys(ai_analysis).length === 0}
							<div class="py-6 text-center">
								<Brain class="text-muted-foreground mx-auto mb-4 h-12 w-12" />
								<h3 class="text-lg font-medium">Belum Ada Analisis AI</h3>
								<p class="text-muted-foreground mt-1 text-sm">
									Balita ini belum memiliki analisis AI.
								</p>
							</div>
						{:else}
							<div class="space-y-4">
								<div>
									<h3 class="text-muted-foreground mb-1 text-sm font-medium">
										Status Perkembangan
									</h3>
									<Badge variant={getStatusVariant(ai_analysis.status_perkembangan)}>
										{ai_analysis.status_perkembangan || 'Tidak tersedia'}
									</Badge>
								</div>

								<Separator />

								<div>
									<h3 class="text-muted-foreground mb-1 text-sm font-medium">Analisis Umum</h3>
									<p class="text-sm">
										{ai_analysis.analisis_umum ||
											ai_analysis.ringkasan ||
											'Tidak ada analisis umum'}
									</p>
								</div>

								{#if ai_analysis.area_perhatian && ai_analysis.area_perhatian.length > 0}
									<Separator />
									<div>
										<h3 class="text-muted-foreground mb-2 text-sm font-medium">Area Perhatian</h3>
										<ul class="space-y-1 text-sm">
											{#each ai_analysis.area_perhatian as area}
												<li class="flex items-start">
													<span class="mr-2 text-red-500">•</span>
													<span>{area}</span>
												</li>
											{/each}
										</ul>
									</div>
								{/if}

								{#if ai_analysis.rekomendasi && ai_analysis.rekomendasi.length > 0}
									<Separator />
									<div>
										<h3 class="text-muted-foreground mb-2 text-sm font-medium">Rekomendasi</h3>
										<ul class="space-y-1 text-sm">
											{#each ai_analysis.rekomendasi as rekomendasi}
												<li class="flex items-start">
													<span class="mr-2 text-green-500">•</span>
													<span>{rekomendasi}</span>
												</li>
											{/each}
										</ul>
									</div>
								{/if}

								{#if ai_analysis.saran_pemantauan}
									<Separator />
									<div>
										<h3 class="text-muted-foreground mb-1 text-sm font-medium">Saran Pemantauan</h3>
										<p class="text-sm">{ai_analysis.saran_pemantauan}</p>
									</div>
								{/if}
							</div>
						{/if}
					</CardContent>
				</Card>
			</div>
		</div>
	{/if}
</div>
