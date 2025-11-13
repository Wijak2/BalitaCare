<script lang="ts">
    import { goto } from '$app/navigation';
    import { Button } from '$lib/components/ui/button/index.js';
    import { Badge } from '$lib/components/ui/badge/index.js';
    import { Baby, Ruler, Activity, Weight, TrendingUp } from 'lucide-svelte';

    function keLogin() {
        goto('/login');
    }

    function keDaftar() {
        goto('/sign-up');
    }

    const features = [
        { icon: Ruler, title: 'Lingkar Kepala' },
        { icon: Activity, title: 'Lingkar Lengan' },
        { icon: Weight, title: 'Berat Badan' },
        { icon: TrendingUp, title: 'Tinggi Badan' }
    ];
</script>

<svelte:head>
    <title>BalitaCare - Monitoring Pertumbuhan Balita</title>
    <meta name="description" content="Aplikasi monitoring pertumbuhan balita" />
</svelte:head>

<!-- Container utama yang mengisi seluruh layar -->
<div class="min-h-screen flex flex-col bg-background">
    <!-- Area konten utama yang di tengah -->
    <main class="flex-1 flex flex-col items-center justify-center text-center px-4">
        <div class="max-w-3xl mx-auto w-full">
            <!-- Badge dan Judul -->
            <Badge variant="outline" class="mb-4 text-sm">
                <Baby class="w-3 h-3 mr-1" />
                Untuk Orang Tua Modern
            </Badge>
            <h1 class="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent">
                Selamat datang di BalitaCare
            </h1>
            <p class="text-lg text-muted-foreground mb-8">
                Pantau tumbuh kembang balita dengan mudah melalui 4 metrik penting.
            </p>

            <!-- Fitur dalam satu baris yang ringkas -->
            <div class="flex flex-wrap justify-center gap-6 md:gap-10 my-8">
                {#each features as feature (feature.title)}
                    <div class="flex flex-col items-center gap-2">
                        <div class="w-14 h-14 rounded-full bg-muted flex items-center justify-center">
                            <feature.icon class="w-7 h-7 text-primary" />
                        </div>
                        <span class="text-sm font-medium">{feature.title}</span>
                    </div>
                {/each}
            </div>

            <!-- Tombol Aksi -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center mt-6">
                <Button size="lg" class="text-lg px-8 py-3" on:click={keLogin}>
                    Masuk
                </Button>
                <Button size="lg" variant="outline" class="text-lg px-8 py-3" on:click={keDaftar}>
                    Daftar
                </Button>
            </div>
        </div>
    </main>

    <!-- Footer yang tetap di bawah -->
    <footer class="py-4 text-center text-sm text-muted-foreground border-t">
        <p>&copy; {new Date().getFullYear()} BalitaCare. Semua hak dilindungi.</p>
    </footer>
</div>