<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import RouterLink from '../components/RouterLink.svelte';
  import {
    Button,
    Input,
    Label,
    Select,
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
    Badge,
    Spinner,
    Alert,
  } from 'flowbite-svelte';
  import { fetchBatches, createBatch, deleteBatch } from '../lib/api';
  import type { BatchForm } from '../lib/types';

  const queryClient = useQueryClient();

  const batchesQuery = createQuery({
    queryKey: ['batches'],
    queryFn: fetchBatches,
  });

  let showForm = $state(false);
  let form = $state<BatchForm>({
    type: '',
    start_date: new Date().toISOString().slice(0, 10),
    temperature: 25,
    status: '发酵中',
    ph: null,
  });

  const statusOptions = ['发酵中', '观察中', '已完成'];

  const createMutation_ = createMutation({
    mutationFn: createBatch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
      showForm = false;
      form = {
        type: '',
        start_date: new Date().toISOString().slice(0, 10),
        temperature: 25,
        status: '发酵中',
        ph: null,
      };
    },
  });

  const deleteMutation_ = createMutation({
    mutationFn: deleteBatch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
    },
  });

  /** 提交新建批次 */
  function handleSubmit(e: Event) {
    e.preventDefault();
    const payload: BatchForm = {
      ...form,
      ph: form.ph === null || Number.isNaN(form.ph) ? null : form.ph,
    };
    $createMutation_.mutate(payload);
  }

  /** 状态徽章颜色 */
  function statusColor(status: string): 'green' | 'yellow' | 'blue' | 'dark' {
    if (status === '已完成') return 'green';
    if (status === '观察中') return 'yellow';
    if (status === '发酵中') return 'blue';
    return 'dark';
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-lg font-semibold text-gray-800">批次列表</h2>
    <Button color="blue" onclick={() => (showForm = !showForm)}>
      {showForm ? '取消' : '+ 新建批次'}
    </Button>
  </div>

  {#if showForm}
    <form
      class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      onsubmit={handleSubmit}
    >
      <h3 class="mb-4 text-base font-medium text-gray-700">新建发酵批次</h3>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <Label for="type">类型</Label>
          <Input id="type" bind:value={form.type} placeholder="如：康普茶" required />
        </div>
        <div>
          <Label for="start_date">开始日期</Label>
          <Input id="start_date" type="date" bind:value={form.start_date} required />
        </div>
        <div>
          <Label for="temperature">温度 (°C)</Label>
          <Input
            id="temperature"
            type="number"
            step="0.1"
            bind:value={form.temperature}
            required
          />
        </div>
        <div>
          <Label for="status">状态</Label>
          <Select id="status" bind:value={form.status} items={statusOptions.map((s) => ({ value: s, name: s }))} />
        </div>
        <div>
          <Label for="ph">pH（可选）</Label>
          <Input
            id="ph"
            type="number"
            step="0.1"
            min="0"
            max="14"
            placeholder="留空则不填"
            value={form.ph ?? ''}
            oninput={(e) => {
              const v = (e.target as HTMLInputElement).value;
              form.ph = v === '' ? null : parseFloat(v);
            }}
          />
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <Button type="submit" color="blue" disabled={$createMutation_.isPending}>
          {$createMutation_.isPending ? '保存中…' : '保存'}
        </Button>
      </div>
      {#if $createMutation_.isError}
        <Alert color="red" class="mt-3">创建失败，请检查后端是否已启动。</Alert>
      {/if}
    </form>
  {/if}

  {#if $batchesQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $batchesQuery.isError}
    <Alert color="red">无法加载批次列表，请确认后端运行在 http://localhost:5000</Alert>
  {:else if ($batchesQuery.data ?? []).length === 0}
    <Alert color="yellow">暂无批次，点击「新建批次」开始记录。</Alert>
  {:else}
    <div class="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
      <Table hoverable>
        <TableHead>
          <TableHeadCell>类型</TableHeadCell>
          <TableHeadCell>开始日期</TableHeadCell>
          <TableHeadCell>温度</TableHeadCell>
          <TableHeadCell>状态</TableHeadCell>
          <TableHeadCell>pH</TableHeadCell>
          <TableHeadCell>操作</TableHeadCell>
        </TableHead>
        <TableBody>
          {#each $batchesQuery.data ?? [] as batch (batch.id)}
            <TableBodyRow>
              <TableBodyCell>
                <RouterLink
                  to="/batches/{batch.id}"
                  class="font-medium text-blue-600 hover:underline"
                >
                  {batch.type}
                </RouterLink>
              </TableBodyCell>
              <TableBodyCell>{batch.start_date}</TableBodyCell>
              <TableBodyCell>{batch.temperature}°C</TableBodyCell>
              <TableBodyCell>
                <Badge color={statusColor(batch.status)}>{batch.status}</Badge>
              </TableBodyCell>
              <TableBodyCell>{batch.ph ?? '—'}</TableBodyCell>
              <TableBodyCell>
                <div class="flex gap-2">
                  <RouterLink to="/batches/{batch.id}">
                    <Button size="xs" color="light">详情</Button>
                  </RouterLink>
                  <Button
                    size="xs"
                    color="red"
                    outline
                    disabled={$deleteMutation_.isPending}
                    onclick={() => {
                      if (confirm(`确定删除「${batch.type}」批次？`)) {
                        $deleteMutation_.mutate(batch.id);
                      }
                    }}
                  >
                    删除
                  </Button>
                </div>
              </TableBodyCell>
            </TableBodyRow>
          {/each}
        </TableBody>
      </Table>
    </div>
  {/if}
</div>
