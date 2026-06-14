<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { Badge, Spinner, Alert, Button } from 'flowbite-svelte';
  import { fetchChangeLogs } from '../lib/api';
  import type { ChangeLog } from '../lib/types';

  let currentPage = $state(1);
  const pageSize = 20;

  const changeLogsQuery = createQuery({
    queryKey: ['change-logs', currentPage],
    queryFn: () => fetchChangeLogs({ page: currentPage, page_size: pageSize }),
  });

  function getOperationBadgeColor(operation: string): string {
    switch (operation) {
      case 'create':
        return 'green';
      case 'update':
        return 'blue';
      case 'delete':
        return 'red';
      default:
        return 'gray';
    }
  }

  function getOperationLabel(operation: string): string {
    switch (operation) {
      case 'create':
        return '新建';
      case 'update':
        return '更新';
      case 'delete':
        return '删除';
      default:
        return operation;
    }
  }

  function getEntityLabel(entity: string): string {
    switch (entity) {
      case 'batch':
        return '批次';
      case 'note':
        return '笔记';
      case 'recipe':
        return '配方';
      default:
        return entity;
    }
  }

  function formatTime(dateStr: string): string {
    const d = new Date(dateStr);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  function formatDate(dateStr: string): string {
    const d = new Date(dateStr);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }

  const totalPages = $derived(Math.ceil(($changeLogsQuery.data?.total ?? 0) / pageSize));

  const groupedLogs = $derived(() => {
    const items = $changeLogsQuery.data?.items ?? [];
    const groups: Record<string, ChangeLog[]> = {};
    for (const log of items) {
      const key = formatDate(log.created_at);
      if (!groups[key]) groups[key] = [];
      groups[key].push(log);
    }
    return groups;
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-lg font-semibold text-gray-800">变更记录</h2>
  </div>

  {#if $changeLogsQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $changeLogsQuery.isError}
    <Alert color="red">无法加载变更记录，请确认后端运行在 http://localhost:5000</Alert>
  {:else if !$changeLogsQuery.data?.items.length}
    <Alert color="yellow">暂无变更记录，执行批次、笔记或配方操作后将自动记录。</Alert>
  {:else}
    <div class="space-y-6">
      {#each Object.entries(groupedLogs()) as [date, logs] (date)}
        <div>
          <div class="mb-3 flex items-center gap-2">
            <div class="h-2 w-2 rounded-full bg-indigo-500"></div>
            <span class="text-sm font-semibold text-gray-700">{date}</span>
          </div>
          <div class="relative ml-1 border-l-2 border-indigo-200 pl-6">
            {#each logs as log (log.id)}
              <div class="relative mb-4 last:mb-0">
                <div
                  class="absolute -left-[31px] top-1.5 h-3 w-3 rounded-full border-2 border-white"
                  class:bg-green-500={log.operation === 'create'}
                  class:bg-blue-500={log.operation === 'update'}
                  class:bg-red-500={log.operation === 'delete'}
                  class:bg-gray-400={log.operation !== 'create' && log.operation !== 'update' && log.operation !== 'delete'}
                ></div>
                <div class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                  <div class="flex flex-wrap items-center gap-2">
                    <Badge color={getOperationBadgeColor(log.operation)}>
                      {getOperationLabel(log.operation)}
                    </Badge>
                    <Badge color="indigo">
                      {getEntityLabel(log.entity)} #{log.entity_id}
                    </Badge>
                    <span class="text-xs text-gray-400">
                      {formatTime(log.created_at).split(' ')[1]}
                    </span>
                  </div>
                  <p class="mt-2 text-sm text-gray-700">{log.summary}</p>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>

    {#if totalPages > 1}
      <div class="flex items-center justify-center gap-2 pt-4">
        <Button
          size="sm"
          color="gray"
          outline
          disabled={currentPage <= 1}
          onclick={() => { currentPage = Math.max(1, currentPage - 1); }}
        >
          上一页
        </Button>
        <span class="text-sm text-gray-600">
          第 {currentPage} / {totalPages} 页（共 {$changeLogsQuery.data.total} 条）
        </span>
        <Button
          size="sm"
          color="gray"
          outline
          disabled={currentPage >= totalPages}
          onclick={() => { currentPage = Math.min(totalPages, currentPage + 1); }}
        >
          下一页
        </Button>
      </div>
    {/if}
  {/if}
</div>
