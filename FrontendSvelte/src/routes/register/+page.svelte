<script lang="ts">
	import { PUBLIC_BACKEND_URL } from "$env/static/public";

	const BACKEND_URL = `${PUBLIC_BACKEND_URL}/auth`;

	let nama = "";
	let email = "";
	let password = "";
	let no_hp = "";
	let message = "";
	let success = false;

	async function handleRegister(e: Event) {
		e.preventDefault();
		message = "";
		success = false;

		try {
			const res = await fetch(`${BACKEND_URL}/register`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ nama, email, password, no_hp })
			});

			const data = await res.json();

			if (!res.ok) {
				message = data.error || "Registrasi gagal.";
				return;
			}

			message = data.message || "Registrasi berhasil!";
			success = true;

			setTimeout(() => {
				window.location.href = "/login";
			}, 1500);
		} catch (err) {
			console.error("Register error:", err);
			message = "Terjadi kesalahan koneksi ke server.";
		}
	}
</script>

<div class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
	<div class="bg-white p-6 rounded-lg shadow-md w-96">
		<h1 class="text-2xl font-bold mb-4 text-center text-blue-700">Registrasi Akun Orang Tua</h1>

		<form on:submit|preventDefault={handleRegister} class="flex flex-col gap-3">
			<label class="font-semibold">Nama Lengkap</label>
			<input
				bind:value={nama}
				type="text"
				class="border p-2 rounded"
				placeholder="Masukkan nama lengkap"
				required
			/>

			<label class="font-semibold">Email</label>
			<input
				bind:value={email}
				type="email"
				class="border p-2 rounded"
				placeholder="Masukkan email"
				required
			/>

			<label class="font-semibold">No. HP</label>
			<input
				bind:value={no_hp}
				type="tel"
				class="border p-2 rounded"
				placeholder="Masukkan nomor HP"
				required
			/>

			<label class="font-semibold">Password</label>
			<input
				bind:value={password}
				type="password"
				class="border p-2 rounded"
				placeholder="Masukkan password"
				required
			/>

			<button type="submit" class="bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
				Daftar
			</button>
		</form>

		{#if message}
			<p class="mt-3 text-center text-sm {success ? 'text-green-600' : 'text-red-500'}">
				{message}
			</p>
		{/if}

		<div class="mt-4 text-center text-sm">
			<a href="/login" class="text-blue-600 underline">Sudah punya akun?</a>
		</div>
	</div>
</div>
