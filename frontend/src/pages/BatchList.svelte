<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import { derived, writable } from 'svelte/store';
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
  import { fetchBatches, createBatch, deleteBatch, exportBatches, importBatches, fetchStatistics } from '../lib/api';
  import type { BatchForm, ImportResult } from '../lib/types';

  const queryClient = useQueryClient();

  const statusFilter = writable<string>('');
  const typeFilter = writable<string>('');

  const statusOptions = ['发酵中', '观察中', '已完成'];

  const statisticsQuery = createQuery({
    queryKey: ['statistics'],
    queryFn: fetchStatistics,
  });

  const typeOptions = derived(statisticsQuery, ($q) =>
    Object.keys($q.data?.type_counts ?? {}).sort(),
  );

  const batchesQueryOptions = derived(
    [statusFilter, typeFilter],
    ([$status, $type]) => ({
      queryKey: ['batches', { status: $status, type: $type }] as const,
      queryFn: () =>
        fetchBatches({
          status: $status || undefined,
          type: $type || undefined,
        }),
    }),
  );

  const batchesQuery = createQuery(batchesQueryOptions);

  let showForm = $state(false);
  let form = $state<BatchForm>({
    type: '',
    start_date: new Date().toISOString().slice(0, 10),
    temperature: 25,
    status: '发酵中',
    ph: null,
  });

  const createMutation_ = createMutation({
    mutationFn: createBatch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'], exact: false });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
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
      queryClient.invalidateQueries({ queryKey: ['batches'], exact: false });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
    },
  });

  let fileInput: HTMLInputElement;
  let showImportResult = $state(false);
  let importResult = $state<ImportResult | null>(null);
  let isExporting = $state(false);
  let exportError = $state<string | null>(null);
  let importError = $state<string | null>(null);
  let isDragging = $state(false);
  let selectedFileName = $state<string | null>(null);

  const importMutation_ = createMutation({
    mutationFn: importBatches,
    onSuccess: (data: ImportResult) => {
      queryClient.invalidateQueries({ queryKey: ['batches'], exact: false });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      importResult = data;
      showImportResult = true;
      importError = null;
      exportError = null;
      selectedFileName = null;
      if (fileInput) {
        fileInput.value = '';
      }
    },
    onError: (err: Error) => {
      importError = err.message;
      showImportResult = false;
      exportError = null;
    },
  });

  /** 处理导出 */
  async function handleExport() {
    isExporting = true;
    exportError = null;
    importError = null;
    try {
      await exportBatches();
    } catch (err: any) {
      exportError = err?.message ?? '导出失败，请稍后重试';
    } finally {
      isExporting = false;
    }
  }

  /** 触发文件选择对话框 */
  function triggerFileSelect() {
    if (fileInput && !$importMutation_.isPending) {
      fileInput.click();
    }
  }

  /** 统一处理文件选择 */
  function processFile(file: File) {
    selectedFileName = file.name;
    showImportResult = false;
    importError = null;
    exportError = null;
    $importMutation_.mutate(file);
  }

  /** 处理 input 文件选择 */
  function handleFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      processFile(file);
    }
  }

  /** 处理拖拽进入 */
  function handleDragEnter(e: DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (!$importMutation_.isPending) {
      isDragging = true;
    }
  }

  /** 处理拖拽离开 */
  function handleDragLeave(e: DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    isDragging = false;
  }

  /** 处理拖拽悬停 */
  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    e.stopPropagation();
  }

  /** 处理文件拖拽放下 */
  function handleDrop(e: DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    isDragging = false;
    const file = e.dataTransfer?.files?.[0];
    if (file && !$importMutation_.isPending) {
      processFile(file);
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
  <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-6">
    <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:gap-2">
      <Label for="filter-status" class="text-sm font-medium text-gray-700 whitespace-nowrap">发酵状态</Label>
      <select
        id="filter-status"
        bind:value={$statusFilter}
        class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 sm:w-40"
      >
        <option value="">全部状态</option>
        {#each statusOptions as status}
          <option value={status}>{status}</option>
        {/each}
      </select>
    </div>
    <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:gap-2">
      <Label for="filter-type" class="text-sm font-medium text-gray-700 whitespace-nowrap">批次类型</Label>
      <select
        id="filter-type"
        bind:value={$typeFilter}
        class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 sm:w-40"
      >
        <option value="">全部类型</option>
        {#each $typeOptions as type}
          <option value={type}>{type}</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
    <h2 class="text-lg font-semibold text-gray-800">批次列表</h2>
    <div class="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:flex-wrap">
      <Button color="green" onclick={handleExport} disabled={isExporting || $importMutation_.isPending}>
        {#if isExporting}
          <span class="inline-flex items-center gap-2">
            <Spinner size="4" />
            导出中…
          </span>
        {:else}
          📤 导出数据
        {/if}
      </Button>

      <div class="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 shadow-sm">
        <label
          for="batch-import-file"
          class="cursor-pointer inline-flex items-center gap-2 text-sm font-medium text-purple-700 hover:text-purple-800"
        >
          📥 选择文件导入
        </label>
        <input
          id="batch-import-file"
          bind:this={fileInput}
          type="file"
          accept=".xlsx,.xls"
          class="hidden"
          onchange={handleFileSelect}
          disabled={$importMutation_.isPending || isExporting}
        />
        <span class="text-xs text-gray-500">
          {#if $importMutation_.isPending}
            <span class="inline-flex items-center gap-1">
              <Spinner size="3" />
              导入中…
            </span>
          {:else if selectedFileName}
            已选：{selectedFileName}
          {:else}
            支持 .xlsx
          {/if}
        </span>
      </div>

      <Button color="blue" onclick={() => (showForm = !showForm)}>
        {showForm ? '取消' : '+ 新建批次'}
      </Button>
    </div>
  </div>

  <div
    class="cursor-pointer rounded-lg border-2 border-dashed p-5 text-center transition-colors {isDragging
      ? 'border-purple-500 bg-purple-50'
      : $importMutation_.isPending
        ? 'border-gray-200 bg-gray-100 cursor-not-allowed'
        : 'border-gray-300 bg-gray-50 hover:border-purple-400 hover:bg-purple-50/50'}"
    onclick={triggerFileSelect}
    ondragenter={handleDragEnter}
    ondragleave={handleDragLeave}
    ondragover={handleDragOver}
    ondrop={handleDrop}
  >
    <div class="flex flex-col items-center gap-2 text-gray-600">
      <div class="text-2xl">📂</div>
      <div class="text-sm font-medium">
        {#if $importMutation_.isPending}
          <span class="inline-flex items-center gap-2">
            <Spinner size="4" />
            正在导入，请稍候…
          </span>
        {:else if selectedFileName}
          已选择文件：{selectedFileName}
        {:else}
          点击选择文件或将 Excel 文件拖拽到此处（支持 .xlsx 格式）
        {/if}
      </div>
      <div class="text-xs text-gray-500">可导入批次及关联笔记数据，重复编号将自动跳过</div>
    </div>
  </div>

  {#if exportError}
    <Alert color="red">导出失败：{exportError}</Alert>
  {/if}

  {#if importError}
    <Alert color="red">导入失败：{importError}</Alert>
  {/if}

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

  {#if $importMutation_.isError && !importError}
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
          <TableHeadCell>发酵天数</TableHeadCell>
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
              <TableBodyCell>
                <span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                  {batch.fermentation_days} 天
                </span>
              </TableBodyCell>
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
