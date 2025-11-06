<script lang="ts">
	import { onMount } from 'svelte';
	import { writable, derived } from 'svelte/store';
	import { goto } from '$app/navigation';

	let statsPerawat = [
		{ title: 'Jumlah Orang Tua Terdaftar', value: 0, link: '' },
		{ title: 'Jumlah Balita Terdaftar', value: 0, link: '' },
		{ title: 'Jumlah Perawat Terdaftar', value: 0, link: '' }
	];

	onMount(async () => {
		try {
			const res = await fetch('http://127.0.0.1:5000/iot/api/dashboard-stats');
			const data = await res.json();
			statsPerawat = [
				{ title: 'Jumlah Orang Tua Terdaftar', value: data.orangtua, link: '' },
				{ title: 'Jumlah Balita Terdaftar', value: data.anak, link: '' },
				{ title: 'Jumlah Perawat Terdaftar', value: data.perawat, link: '' }
			];
		} catch (err) {
			console.error('Gagal mengambil data dari backend:', err);
		}
	});

	const orangtuaList = writable<
		{ id_orang_tua: number; nama: string; email: string; telp: string }[]
	>([]);
	const search = writable('');

	const filteredList = derived([orangtuaList, search], ([$orangtuaList, $search]) =>
		$orangtuaList.filter((o) => o.nama.toLowerCase().includes($search.toLowerCase()))
	);

	onMount(async () => {
		try {
			const res = await fetch('http://127.0.0.1:5000/iot/api/orangtua');
			if (!res.ok) throw new Error('Gagal mengambil data');
			const data = await res.json();
			orangtuaList.set(data);
		} catch (err) {
			console.error('Gagal fetch data orang tua:', err);
		}
	});
</script>


<div class="page-wrapper">
	<div class="mb-6 grid">
		{#each statsPerawat as stat}
			<div class="card-B row-span-3 grid gap-1 bg-white text-center shadow-sm">
				<p>{stat.title}</p>
				<h3 class="text-2xl font-bold text-blue-600">{stat.value}</h3>
			</div>
		{/each}
	</div>

	<div class="flex flex-col sm:flex-row gap-4 justify-between pb-2">
		<h2>Orangtua Terdaftar</h2>
		<input
			type="text"
			placeholder="🔍 Cari nama..."
			bind:value={$search}
			class="w-full rounded-md border border-gray-300 px-2 py-1 sm:w-52"
		/>
	</div>

	<div class="table-container">
		<table>
			<thead>
				<tr>
					<th>Nama</th>
					<th>Nomor Telpon</th>
					<th>Email</th>
					<th>Aksi</th>
				</tr>
			</thead>
			<tbody>
				{#if $filteredList.length > 0}
					{#each $filteredList as o}
						<tr>
							<td>{o.nama}</td>
							<td>{o.telp}</td>
							<td>{o.email}</td>
							<td class="space-x-2">
								<button
									on:click={() => goto(`/list-balita?id_orangtua=${o.id_orang_tua}`)}
									class="btn-B bg-blue-500 text-white"
								>
									Daftar anak
								</button>
								<button
									on:click={() => goto(`/crud-anak?id_orangtua=${o.id_orang_tua}`)}
									class="btn-B bg-green-500 text-white sm:px-3 sm:text-sm"
								>
									Tambah anak
								</button>
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="4" class="text-center">Belum ada data orang tua</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
