<script lang="ts">
  import type { Snippet } from 'svelte';
  import { navigate } from '../lib/router';

  interface Props {
    to: string;
    class?: string;
    children: Snippet;
  }

  let { to, class: className = '', children }: Props = $props();

  /** 拦截点击并走客户端路由 */
  function handleClick(e: MouseEvent) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    navigate(to);
  }
</script>

<a href={to} class={className} onclick={handleClick}>
  {@render children()}
</a>
