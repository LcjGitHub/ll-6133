<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { Card, Badge, Spinner, Alert } from 'flowbite-svelte';
  import { fetchStatistics } from '../lib/api';

  const statisticsQuery = createQuery({
    queryKey: ['statistics'],
    queryFn: fetchStatistics,
  });

  function statusColor(status: string): 'green' | 'yellow' | 'blue' | 'dark' {
    if (status === '已完成') return 'green';
    if (status === '观察中') return 'yellow';
    if (status === '发酵中') return 'blue';
    return 'dark';
  }

  $: typeEntries = Object.entries($statisticsQuery.data?.type_counts ?? {});
  $: maxTypeCount = typeEntries.length > 0 ? Math.max(...typeEntries.map(([, v]) => v)) : 0;
  $: statusEntries = Object.entries($statisticsQuery.data?.status_counts ?? {});
  $: totalBatches = statusEntries.reduce((sum, [, v]) => sum + v, 0);
</script>

<div class="space-y-6">
  <h2 class="text-lg font-semibold text-gray-800">数据概览</h2>

  {#if $statisticsQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $statisticsQuery.isError}
    <Alert color="red">无法加载统计数据，请确认后端运行在 http://localhost:5000</Alert>
  {:else}
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">发酵状态分布</p>
            <p class="mt-1 text-2xl font-bold text-gray-900">{totalBatches} 批</p>
          </div>
          <div class="rounded-full bg-blue-100 p-3">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <div class="mt-3 space-y-1">
          {#each statusEntries as [status, count]}
            <div class="flex items-center justify-between text-sm">
              <div class="flex items-center gap-2">
                <Badge color={statusColor(status)}>{status}</Badge>
              </div>
              <span class="font-medium text-gray-700">{count} 批</span>
            </div>
          {/each}
          {#if statusEntries.length === 0}
            <p class="text-sm text-gray-500">暂无数据</p>
          {/if}
        </div>
      </Card>

      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">类型分布</p>
            <p class="mt-1 text-2xl font-bold text-gray-900">{typeEntries.length} 类</p>
          </div>
          <div class="rounded-full bg-green-100 p-3">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
          </div>
        </div>
        <div class="mt-3 space-y-1">
          {#each typeEntries as [type, count]}
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">{type}</span>
              <span class="font-medium text-gray-700">{count} 批</span>
            </div>
          {/each}
          {#if typeEntries.length === 0}
            <p class="text-sm text-gray-500">暂无数据</p>
          {/if}
        </div>
      </Card>

      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">近 7 天新增笔记</p>
            <p class="mt-1 text-2xl font-bold text-gray-900">{$statisticsQuery.data?.recent_notes_count ?? 0} 条</p>
          </div>
          <div class="rounded-full bg-purple-100 p-3">
            <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
        </div>
        <p class="mt-3 text-xs text-gray-500">统计最近 7 天内新增的观察笔记数量</p>
      </Card>
    </div>

    <Card class="p-6">
      <h3 class="mb-4 text-base font-medium text-gray-700">各类型批次数量对比</h3>
      {#if typeEntries.length > 0}
        <div class="space-y-3">
          {#each typeEntries as [type, count]}
            <div class="flex items-center gap-4">
              <div class="w-24 flex-shrink-0 text-right text-sm text-gray-600">{type}</div>
              <div class="flex-1">
                <div class="h-8 overflow-hidden rounded bg-gray-100">
                  <div
                    class="h-full rounded bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-500"
                    style="width: {maxTypeCount > 0 ? (count / maxTypeCount) * 100 : 0}%;"
                  ></div>
                </div>
              </div>
              <div class="w-12 text-right text-sm font-medium text-gray-700">{count}</div>
            </div>
          {/each}
        </div>
      {:else}
        <p class="text-sm text-gray-500">暂无批次数据</p>
      {/if}
    </Card>
  {/if}
</div>
