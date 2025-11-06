<script>
  import { goto } from '$app/navigation';
  function keLogin() {
    goto('/login');
  }
</script>

<div class="flex flex-col items-center justify-center h-screen text-center">
  <h1 class="text-3xl font-bold mb-4">Selamat datang di BalitaCare 👶</h1>
  <p class="mb-6 text-gray-600">Silakan login untuk melanjutkan</p>
  <button
    on:click={keLogin}
    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
  >
    Ke Halaman Login
  </button>
</div>
