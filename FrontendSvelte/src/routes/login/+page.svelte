<script lang="ts">
  import { PUBLIC_BACKEND_URL } from "$env/static/public";

  const BACKEND_URL = `${PUBLIC_BACKEND_URL}/auth`;

  let notelp = "";
  let password = "";
  let message = "";

  function decodeJWT(token: string) {
    try {
      const base64Payload = token.split(".")[1];
      return JSON.parse(atob(base64Payload));
    } catch {
      return null;
    }
  }

  async function handleLogin(e: Event) {
    e.preventDefault();
    message = "";

    try {
      const res = await fetch(`${BACKEND_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: notelp,
          password
        })
      });

      const data = await res.json();

      if (!res.ok) {
        message = data.error || "Nomor telepon atau password salah.";
        return;
      }

      sessionStorage.setItem("token", data.token);

      const payload = decodeJWT(data.token);
      if (!payload) {
        message = "Token tidak valid.";
        return;
      }

      const role = payload.role;

      message = "Login berhasil!";

      if (role === "orang_tua") {
        window.location.href = "/dashboard-orangtua";
      } else if (role === "perawat") {
        window.location.href = "/dashboard-perawat";
      }

    } catch (err) {
      console.error("Login error:", err);
      message = "Terjadi kesalahan koneksi ke server.";
    }
  }
</script>

<div class="page-login">
  <div class="card-login">
    <div class="left hidden lg:block">
      <div class="mt-40">
        <h1 class="text-2xl font-bold mb-4">Selamat Datang!</h1>
        <p>
          Selamat datang di website monitoring balita, silakan login untuk melanjutkan ke halaman dashboard,
          apabila belum punya akun silakan buat akun
        </p>
        <a href="/register" class="text-white underline">Belum punya akun</a>
      </div>
    </div>

    <div class="right">
      <h1 class="text-2xl font-bold mb-4 text-center">Login</h1>
      <p class="hidden lg:block mb-4">
        Silakan login menggunakan nomor telepon yang telah didaftarkan
      </p>

      <form on:submit|preventDefault={handleLogin}>
        <label for="notelp" class="font-semibold">Nomor Telepon</label>
        <input
          bind:value={notelp}
          type="text"
          id="notelp"
          class="block w-full border border-gray-300 rounded-md p-2 mb-4"
          placeholder="Masukkan nomor telepon"
          required
        />

        <label for="password" class="font-semibold">Password</label>
        <input
          bind:value={password}
          type="password"
          id="password"
          class="block w-full border border-gray-300 rounded-md p-2 mb-4"
          placeholder="Masukkan password"
          required
        />

        <a href="#" class="text-blue-600 hover:underline">Lupa password?</a>

        <button
          type="submit"
          class="w-full mt-4 bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
        >
          Login
        </button>
      </form>

      {#if message}
        <p class="mt-3 text-center text-sm text-red-500">{message}</p>
      {/if}

      <a class="block lg:hidden mt-4 text-blue-600 hover:underline" href="/register">
        Belum punya akun
      </a>
    </div>
  </div>
</div>
