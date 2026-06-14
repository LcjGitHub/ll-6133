<script lang="ts">
  import { onMount } from 'svelte';
  import { createQuery } from '@tanstack/svelte-query';
  import RouterLink from '../components/RouterLink.svelte';
  import { Spinner, Alert, Badge } from 'flowbite-svelte';
  import { globalSearch } from '../lib/api';
  import type { SearchResult } from '../lib/types';

  let keyword = $state('');
  let debounceTimer: number | null = null;
  let searchTrigger = $state(0);
  let inputElement: HTMLInputElement | null = null;
  let currentKeyword = $state('');

  const isQueryEnabled = $derived(currentKeyword.trim().length > 0 && searchTrigger > 0);

  const searchQuery = createQuery({
    queryKey: ['search', searchTrigger, currentKeyword],
    queryFn: async (): Promise<SearchResult> => {
      if (!currentKeyword.trim()) {
        return {
          batches: [],
          recipes: [],
          notes: [],
          batch_count: 0,
          recipe_count: 0,
          note_count: 0,
          total_count: 0,
        };
      }
      return globalSearch(currentKeyword.trim());
    },
    enabled: isQueryEnabled,
    staleTime: 60_000,
  });

  function onInput(e: Event) {
    const target = e.target as HTMLInputElement;
    keyword = target.value;

    if (debounceTimer !== null) {
      clearTimeout(debounceTimer);
    }

    if (!keyword.trim()) {
      return;
    }

    debounceTimer = window.setTimeout(() => {
      currentKeyword = keyword;
      searchTrigger++;
    }, 500);
  }

  function truncateText(text: string, maxLength: number = 100): string {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '…';
  }

  function highlightKeyword(text: string, kw: string): string {
    if (!kw.trim()) return text;
    const regex = new RegExp(`(${kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>');
  }

  onMount(() => {
    if (inputElement) {
      inputElement.focus();
    }
  });
</script>

<div class="space-y-6">
  <div class="flex items-center gap-3">
    <h2 class="text-lg font-semibold text-gray-800">🔍 全局搜索</h2>
  </div>

  <div class="relative">
    <input
      id="search-input"
      type="text"
      placeholder="输入关键字搜索批次类型、配方名称、观察笔记…"
      value={keyword}
      oninput={onInput}
      class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-4 pl-10 text-lg text-gray-900 focus:border-blue-500 focus:ring-blue-500"
      bind:this={inputElement}
    />
    <svg
      class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
      />
    </svg>
    {#if keyword && searchTrigger > 0 && $searchQuery.isPending}
      <div class="absolute right-3 top-1/2 -translate-y-1/2">
        <Spinner size="6" />
      </div>
    {/if}
  </div>

  {#if currentKeyword.trim() && searchTrigger > 0}
    {#if $searchQuery.isPending}
      <div class="flex justify-center py-12">
        <Spinner size="8" />
      </div>
    {:else if $searchQuery.isError}
      <Alert color="red">搜索失败，请确认后端运行在 http://localhost:5000</Alert>
    {:else if $searchQuery.data}
      {#if $searchQuery.data.total_count === 0}
        <Alert color="yellow">未找到与「{currentKeyword}」相关的结果</Alert>
      {:else}
        <div class="mb-4 text-sm text-gray-600">
          共找到 {$searchQuery.data.total_count} 条结果
          （批次 {$searchQuery.data.batch_count}、配方 {$searchQuery.data.recipe_count}、笔记 {$searchQuery.data.note_count}）
        </div>

        {#if $searchQuery.data.batch_count > 0}
          <div class="space-y-3">
            <h3 class="flex items-center gap-2 text-base font-medium text-blue-700">
              <span>📦 批次</span>
              <Badge color="blue">{$searchQuery.data.batch_count}</Badge>
            </h3>
            <div class="space-y-2">
              {#each $searchQuery.data.batches as batch (batch.id)}
                <RouterLink
                  to="/batches/{batch.id}"
                  class="block rounded-lg border border-blue-100 bg-blue-50 p-3 shadow-sm hover:bg-blue-100 transition-colors"
                >
                  <div class="flex items-center justify-between">
                    <div class="font-medium text-gray-900">
                      {@html highlightKeyword(batch.type, currentKeyword)}
                    </div>
                    <Badge color="blue">{batch.status}</Badge>
                  </div>
                  <div class="mt-1 text-sm text-gray-600">
                    开始日期：{batch.start_date} · 已发酵 {batch.fermentation_days} 天
                  </div>
                </RouterLink>
              {/each}
            </div>
          </div>
        {/if}

        {#if $searchQuery.data.recipe_count > 0}
          <div class="space-y-3 pt-4">
            <h3 class="flex items-center gap-2 text-base font-medium text-green-700">
              <span>📋 配方</span>
              <Badge color="green">{$searchQuery.data.recipe_count}</Badge>
            </h3>
            <div class="space-y-2">
              {#each $searchQuery.data.recipes as recipe (recipe.id)}
                <RouterLink
                  to="/recipes/{recipe.id}"
                  class="block rounded-lg border border-green-100 bg-green-50 p-3 shadow-sm hover:bg-green-100 transition-colors"
                >
                  <div class="font-medium text-gray-900">
                    {@html highlightKeyword(recipe.name, currentKeyword)}
                  </div>
                  <div class="mt-1 text-sm text-gray-600">
                    类型：{recipe.ferment_type}
                  </div>
                </RouterLink>
              {/each}
            </div>
          </div>
        {/if}

        {#if $searchQuery.data.note_count > 0}
          <div class="space-y-3 pt-4">
            <h3 class="flex items-center gap-2 text-base font-medium text-purple-700">
              <span>📝 笔记</span>
              <Badge color="purple">{$searchQuery.data.note_count}</Badge>
            </h3>
            <div class="space-y-2">
              {#each $searchQuery.data.notes as note (note.id)}
                <RouterLink
                  to="/batches/{note.batch_id}"
                  class="block rounded-lg border border-purple-100 bg-purple-50 p-3 shadow-sm hover:bg-purple-100 transition-colors"
                >
                  <div class="text-sm text-gray-600 mb-1">
                    批次 #{note.batch_id} · {note.created_at.slice(0, 10)}
                  </div>
                  <div class="text-gray-800">
                    {@html highlightKeyword(truncateText(note.content, 150), currentKeyword)}
                  </div>
                </RouterLink>
              {/each}
            </div>
          </div>
        {/if}
      {/if}
    {/if}
  {:else if keyword.trim() === ''}
    <div class="text-center py-12 text-gray-500">
      <p class="text-lg">请输入关键字开始搜索</p>
      <p class="text-sm mt-2">支持搜索批次类型、配方名称、观察笔记正文</p>
    </div>
  {/if}
</div>
