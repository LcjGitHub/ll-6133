<script lang="ts">
  import { onMount } from 'svelte';
  import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
  import BatchList from './pages/BatchList.svelte';
  import BatchDetail from './pages/BatchDetail.svelte';
  import RecipeList from './pages/RecipeList.svelte';
  import RecipeDetail from './pages/RecipeDetail.svelte';
  import Overview from './pages/Overview.svelte';
  import {
    initRouter,
    parseBatchId,
    parseRecipeId,
    isRecipeList,
    isOverview,
    pathname,
    navigate,
  } from './lib/router';

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 1,
      },
    },
  });

  onMount(initRouter);

  function isBatchesActive(path: string): boolean {
    return path === '/' || parseBatchId(path) !== null;
  }

  function isRecipesActive(path: string): boolean {
    return isRecipeList(path) || parseRecipeId(path) !== null;
  }

  function isOverviewActive(path: string): boolean {
    return isOverview(path);
  }
</script>

<QueryClientProvider client={queryClient}>
  <div class="min-h-screen bg-gray-50">
    <header class="border-b border-gray-200 bg-white shadow-sm">
      <div class="mx-auto max-w-5xl px-4 py-4">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h1 class="text-xl font-bold text-gray-900">🧪 家庭发酵实验日志</h1>
          <nav class="flex gap-1">
            <button
              class={
                'rounded-lg px-3 py-2 text-sm font-medium transition-colors ' +
                (isOverviewActive($pathname)
                  ? 'bg-purple-100 text-purple-700'
                  : 'text-gray-600 hover:bg-gray-100')
              }
              onclick={() => navigate('/overview')}
            >
              数据概览
            </button>
            <button
              class={
                'rounded-lg px-3 py-2 text-sm font-medium transition-colors ' +
                (isBatchesActive($pathname)
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100')
              }
              onclick={() => navigate('/')}
            >
              批次管理
            </button>
            <button
              class={
                'rounded-lg px-3 py-2 text-sm font-medium transition-colors ' +
                (isRecipesActive($pathname)
                  ? 'bg-green-100 text-green-700'
                  : 'text-gray-600 hover:bg-gray-100')
              }
              onclick={() => navigate('/recipes')}
            >
              配方管理
            </button>
          </nav>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-6">
      {#if isOverview($pathname)}
        <Overview />
      {:else if parseRecipeId($pathname)}
        {#key parseRecipeId($pathname)}
          <RecipeDetail id={parseRecipeId($pathname)!} />
        {/key}
      {:else if isRecipeList($pathname)}
        <RecipeList />
      {:else if parseBatchId($pathname)}
        {#key parseBatchId($pathname)}
          <BatchDetail id={parseBatchId($pathname)!} />
        {/key}
      {:else}
        <BatchList />
      {/if}
    </main>
  </div>
</QueryClientProvider>
