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
  import { fetchBatches, createBatch, deleteBatch, exportBatches, importBatches } from '../lib/api';
  import type { BatchForm, ImportResult } from '../lib/types';

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

  let fileInput: HTMLInputElement;
  let showImportResult = $state(false);
  let importResult = $state<ImportResult | null>(null);

  const importMutation_ = createMutation({
    mutationFn: importBatches,
    onSuccess: (data: ImportResult) => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
      importResult = data;
      showImportResult = true;
      if (fileInput) {
        fileInput.value = '';
      }
    },
  });

  /** 处理导出 */
  function handleExport() {
    exportBatches();
  }

  /** 处理文件选择 */
  function handleFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      showImportResult = false;
      $importMutation_.mutate(file);
    }
  }

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
  function statusColor(): 'dark' {
    return 'dark';
  }
</script>

<div class="space-y-6">
  <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <h2 class="text-lg font-semibold text-gray-800">批次列表</h2>
    <div class="flex flex-wrap gap-2">
      <Button color="green" onclick={handleExport}>
        📤 导出数据
      </Button>
      <label class="cursor-pointer">
        <input
          bind:this={fileInput}
          type="file"
          accept=".xlsx,.xls"
          class="hidden"
          onchange={handleFileSelect}
          disabled={$importMutation_.isPending}
        />
        <Button color="purple" disabled={$importMutation_.isPending}>
          {$importMutation_.isPending ? '导入中…' : '📥 导入数据'}
        </Button>
      </label>
      <Button color="blue" onclick={() => (showForm = !showForm)}>
        {showForm ? '取消' : '+ 新建批次'}
      </Button>
    </div>
  </div>

  {#if showImportResult && importResult}
    <Alert color="green" class="space-y-1">
      <div class="font-medium">导入完成！</div>
      <div class="text-sm">
        批次：新增 {importResult.inserted_batches} 条，跳过 {importResult.skipped_batches} 条（共 {importResult.total_batches_in_file} 条）
      </div>
      <div class="text-sm">
        笔记：新增 {importResult.inserted_notes} 条，跳过 {importResult.skipped_notes} 条（共 {importResult.total_notes_in_file} 条）
      </div>
    </Alert>
  {/if}

  {#if $importMutation_.isError}
    <Alert color="red">
      导入失败：{$importMutation_.error?.message ?? '请检查文件格式是否正确'}
    </Alert>
  {/if}

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
                <Badge color={statusColor()}>{batch.status}</Badge>
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
