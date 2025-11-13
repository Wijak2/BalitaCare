<script lang="ts">
	import type { PageProps } from './$types';
	import { Button } from '$lib/components/ui/button/index.js';
	let { data }: PageProps = $props();
</script>

<section>
    <Button>Click me</Button>
</section>
