<script lang="ts">
	import logo from '$lib/assets/balitacare.jpeg';
	import { cn } from '$lib/utils.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Field from '$lib/components/ui/field/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import type { HTMLAttributes } from 'svelte/elements';
	import { PUBLIC_BACKEND_URL } from "$env/static/public";

	let { class: className, ...restProps }: HTMLAttributes<HTMLDivElement> = $props();

	const BACKEND_URL = `${PUBLIC_BACKEND_URL}/auth`;

	// State form
	let nama = "";
	let email = "";
	let no_hp = "";
	let password = "";
	let confirmPassword = "";
	let message = "";
	let success = false;

	async function handleRegister(e: Event) {
		e.preventDefault();
		message = "";
		success = false;

		if (password !== confirmPassword) {
			message = "Password dan konfirmasi password tidak sama.";
			return;
		}

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
				window.location.href = "/sign-in";
			}, 1500);
		} catch (err) {
			console.error("Register error:", err);
			message = "Terjadi kesalahan koneksi ke server.";
		}
	}
</script>

<div class={cn('flex flex-col gap-6 justify-center items-center min-h-screen', className)} {...restProps}>
	<Card.Root class="w-full max-w-md">
		<Card.Header class="text-center">
			<Card.Title class="text-xl">Daftarkan Akun</Card.Title>
			<Card.Description>
				Masukkan Email, Nomor telepon dan password untuk membuat akun
			</Card.Description>
		</Card.Header>

		<Card.Content>
			<form on:submit|preventDefault={handleRegister}>
				<Field.Group class="flex flex-col gap-3">
					<Field.Field>
						<Field.Label for="name">Nama</Field.Label>
						<Input id="name" type="text" placeholder="Nama" bind:value={nama} required />
					</Field.Field>

					<Field.Field>
						<Field.Label for="email">Email</Field.Label>
						<Input id="email" type="email" placeholder="contoh@contoh.com" bind:value={email} required />
					</Field.Field>

					<Field.Field>
						<Field.Label for="tel">Nomor Telepon</Field.Label>
						<Input id="tel" type="tel" placeholder="08123456789" bind:value={no_hp} required/>
					</Field.Field>

					<Field.Field class="grid grid-cols-2 gap-4">
						<Field.Field>
							<Field.Label for="password">Password</Field.Label>
							<Input id="password" type="password" bind:value={password} required />
						</Field.Field>
						<Field.Field>
							<Field.Label for="confirm-password">Confirm Password</Field.Label>
							<Input id="confirm-password" type="password" bind:value={confirmPassword} required />
						</Field.Field>
					</Field.Field>

					<Field.Field>
						<Button type="submit" class="w-full bg-sky-500">Daftar Akun</Button>
						{#if message}
							<p class="text-center text-sm mt-2 {success ? 'text-green-600' : 'text-red-500'}">{message}</p>
						{/if}
						<Field.Description class="text-center mt-2">
							Sudah punya akun? <a href="/sign-in" class="text-blue-600 underline">Masuk</a>
						</Field.Description>
					</Field.Field>
				</Field.Group>
			</form>
		</Card.Content>
	</Card.Root>
</div>
