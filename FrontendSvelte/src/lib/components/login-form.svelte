<script lang="ts">
    import logo from '$lib/assets/balitacare.jpeg';
    import * as Card from '$lib/components/ui/card/index.js';
    import {
        FieldGroup,
        Field,
        FieldLabel,
        FieldDescription
    } from '$lib/components/ui/field/index.js';
    import { Input } from '$lib/components/ui/input/index.js';
    import { Button } from '$lib/components/ui/button/index.js';
    import { cn } from '$lib/utils.js';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';
    import { goto } from '$app/navigation';

    import CircleAlertIcon from "@lucide/svelte/icons/circle-alert";
    import * as Alert from "$lib/components/ui/alert/index.js";

    let identifier = "";
    let password = "";
    let message = "";
    let isLoading = false;

    const BACKEND_URL = `${PUBLIC_BACKEND_URL}/auth`;

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
        isLoading = true;

        try {
            const res = await fetch(`${BACKEND_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ identifier, password })
            });

            const data = await res.json();
            isLoading = false;

            if (!res.ok) {
                message = data.error || "Email/nomor telepon atau password salah.";
                return;
            }

            // 保存 JWT token 到 sessionStorage
            sessionStorage.setItem("token", data.token);

            // 解码 JWT 获取用户信息
            const payload = decodeJWT(data.token);
            if (!payload) {
                message = "Token tidak valid.";
                return;
            }

            // 检查 token 是否过期
            const now = Date.now() / 1000;
            if (payload.exp && payload.exp < now) {
                message = "Token sudah kadaluarsa.";
                return;
            }

            // 保存用户角色到 sessionStorage
            sessionStorage.setItem("userRole", payload.role);
            
            // 保存用户ID（如果有的话）
            if (payload.userId) {
                sessionStorage.setItem("userId", payload.userId);
            }

            // 根据角色重定向到相应的仪表板
            const role = payload.role;
            if (role === "orang_tua") {
                goto("/ortu-dash");
            } else if (role === "perawat") {
                goto("/per-dash");
            } else {
                message = "Peran pengguna tidak dikenali.";
            }

        } catch (err) {
            isLoading = false;
            console.error(err);
            message = "Terjadi kesalahan koneksi ke server.";
        }
    }
</script>

<div class="flex flex-col gap-6">
    <Card.Root class="overflow-hidden p-0">
        <Card.Content class="grid p-0 md:grid-cols-2">
            <div class="bg-muted relative hidden md:block">
                <img
                    src={logo}
                    alt="placeholder"
                    class="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
                />
            </div>

            <form class="p-6 md:p-8" on:submit|preventDefault={handleLogin}>
                <FieldGroup>
                    <div class="flex flex-col items-center gap-2 text-center">
                        <h1 class="text-sky-500 text-2xl font-bold">Selamat Datang</h1>
                        <p class="text-muted-foreground text-balance">
                            Silakan masukkan nomor telepon atau email dan password untuk melanjutkan
                        </p>
                    </div>

                    <Field>
                        <FieldLabel for="login">Nomor Telepon atau Email</FieldLabel>
                        <Input
                            id="login"
                            type="text"
                            placeholder="nomor telepon atau email"
                            bind:value={identifier}
                            required
                        />
                    </Field>

                    <Field>
                        <div class="flex items-center">
                            <FieldLabel for="password">Password</FieldLabel>
                            <a href="##" class="ml-auto text-sm underline-offset-2 hover:underline">
                                Lupa Password?
                            </a>
                        </div>
                        <Input
                            id="password"
                            type="password"
                            placeholder="******"
                            bind:value={password}
                            required
                        />
                    </Field>

                    <Field>
                        <Button class="bg-sky-500" type="submit" disabled={isLoading}>
                            {isLoading ? "Loading..." : "Login"}
                        </Button>
                    </Field>

                    <FieldDescription class="text-center">
                        Belum punya akun? <a href="sign-up">Daftar</a>
                    </FieldDescription>
                </FieldGroup>
            </form>
        </Card.Content>
    </Card.Root>

    {#if message}
        <Alert.Root variant="destructive" class="mb-4">
            <CircleAlertIcon class="size-4" />
            <Alert.Title>Error</Alert.Title>
            <Alert.Description>{message}</Alert.Description>
        </Alert.Root>
    {/if}
</div>