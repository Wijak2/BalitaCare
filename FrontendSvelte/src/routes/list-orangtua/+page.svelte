<script lang="ts">
	import { writable, derived } from 'svelte/store';
	import { onMount } from 'svelte';
    import { goto } from '$app/navigation';


	// Store untuk daftar orang tua
	const orangtuaList = writable<{ nama: string; email: string; telp: string }[]>([]);
	const search = writable('');

	// Derived store untuk hasil pencarian
	const filteredList = derived(
		[orangtuaList, search],
		([$orangtuaList, $search]) =>
			$orangtuaList.filter((o) =>
				o.nama.toLowerCase().includes($search.toLowerCase())
			)
	);

	// Ambil data dari backend saat halaman dimuat
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

<!-- Tampilan -->
<div class="list-orangtua-container">
	<div class="list-header">
		<h2>Daftar Orang Tua Terdaftar</h2>

		<div class="search-box">
			<input
				type="text"
				placeholder="🔍 Cari"
				bind:value={$search}
				class="search-input"
			/>
		</div>
	</div>

	<table class="list-table">
		<thead>
			<tr>
				<th>Nama</th>
				<th>Email</th>
				<th>No. Telepon</th>
				<th>Aksi</th>
			</tr>
		</thead>
		<tbody>
			{#if $filteredList.length > 0}
				{#each $filteredList as o}
					<tr>
						<td>{o.nama}</td>
						<td>{o.email}</td>
						<td>{o.telp}</td>
						<td>
                        <button
                            class="lihat-btn"
                            on:click={() => goto(`/list-balita?id_orangtua=${o.id_orang_tua}`)}>
                            Lihat daftar anak
                        </button>
                        </td>
					</tr>
				{/each}
			{:else}
				<tr>
					<td colspan="4" style="text-align:center;">Belum ada data orang tua</td>
				</tr>
			{/if}
		</tbody>
	</table>
</div>
