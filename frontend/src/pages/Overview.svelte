<script lang="ts">
  import { createQuery, useQueryClient } from '@tanstack/svelte-query';
  import { Card, Badge, Spinner, Alert, Button, Modal, Checkbox } from 'flowbite-svelte';
  import { fetchStatistics, downloadBackup, previewBackup, restoreBackup } from '../lib/api';
  import type { BackupSummary, BackupRestoreResult } from '../lib/types';

  const queryClient = useQueryClient();
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

  let backupLoading = false;
  let restoreLoading = false;
  let previewLoading = false;
  let selectedFile: File | null = null;
  let fileInput: HTMLInputElement | null = null;
  let previewSummary: BackupSummary | null = null;
  let confirmOverwrite = false;
  let showConfirmModal = false;
  let successMessage: string | null = null;
  let errorMessage: string | null = null;
  let restoreResult: BackupRestoreResult | null = null;

  function clearMessages() {
    successMessage = null;
    errorMessage = null;
  }

  async function handleDownloadBackup() {
    clearMessages();
    backupLoading = true;
    try {
      await downloadBackup();
      successMessage = '数据备份下载成功！';
    } catch (err: any) {
      errorMessage = err.message ?? '备份下载失败，请稍后重试';
    } finally {
      backupLoading = false;
    }
  }

  function handleFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    const files = target.files;
    if (files && files.length > 0) {
      selectedFile = files[0];
      previewSummary = null;
      restoreResult = null;
      confirmOverwrite = false;
      clearMessages();
    }
  }

  async function handlePreview() {
    if (!selectedFile) return;
    clearMessages();
    previewLoading = true;
    try {
      previewSummary = await previewBackup(selectedFile);
    } catch (err: any) {
      errorMessage = err.message ?? '预览备份文件失败';
      previewSummary = null;
    } finally {
      previewLoading = false;
    }
  }

  function handleRestoreClick() {
    if (!selectedFile || !previewSummary) return;
    showConfirmModal = true;
  }

  async function handleConfirmRestore() {
    if (!selectedFile || !confirmOverwrite) return;
    clearMessages();
    restoreLoading = true;
    showConfirmModal = false;
    try {
      restoreResult = await restoreBackup(selectedFile, true);
      if (restoreResult.success) {
        successMessage = restoreResult.message ?? '数据恢复成功！';
        await queryClient.invalidateQueries({ queryKey: ['statistics'] });
        await queryClient.invalidateQueries({ queryKey: ['batches'] });
        await queryClient.invalidateQueries({ queryKey: ['recipes'] });
        await queryClient.invalidateQueries({ queryKey: ['reminders'] });
        await queryClient.invalidateQueries({ queryKey: ['strains'] });
      } else {
        errorMessage = restoreResult.message ?? '数据恢复失败';
      }
    } catch (err: any) {
      errorMessage = err.message ?? '数据恢复失败，请稍后重试';
      restoreResult = null;
    } finally {
      restoreLoading = false;
      confirmOverwrite = false;
    }
  }

  function resetRestoreForm() {
    selectedFile = null;
    previewSummary = null;
    restoreResult = null;
    confirmOverwrite = false;
    clearMessages();
    if (fileInput) {
      fileInput.value = '';
    }
  }
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
        <div class="flex">
          <div class="mr-2 flex flex-col justify-between text-right text-xs text-gray-500" style="height: 260px; width: 40px;">
            <span>{maxTypeCount}</span>
            <span>{Math.round(maxTypeCount * 0.75)}</span>
            <span>{Math.round(maxTypeCount * 0.5)}</span>
            <span>{Math.round(maxTypeCount * 0.25)}</span>
            <span>0</span>
          </div>
          <div class="flex-1">
            <div class="relative flex items-end gap-3 border-l border-b border-gray-200 pl-2" style="height: 260px;">
              {#each typeEntries as [type, count], i}
                <div class="group flex flex-1 flex-col items-center">
                  <span class="mb-1 text-xs font-semibold text-gray-700">{count}</span>
                  <div
                    class="w-full max-w-[60px] rounded-t transition-all duration-500 hover:opacity-80"
                    style="height: {maxTypeCount > 0 ? (count / maxTypeCount) * 220 : 0}px; background: linear-gradient(to top, hsl({i * 40}, 70%, 55%), hsl({i * 40 + 20}, 70%, 65%));"
                    title={`${type}: ${count} 批`}
                  ></div>
                  <span class="mt-2 text-center text-xs text-gray-600 break-all" style="max-width: 80px;">{type}</span>
                </div>
              {/each}
            </div>
          </div>
        </div>
      {:else}
        <p class="text-sm text-gray-500">暂无批次数据</p>
      {/if}
    </Card>
  {/if}

  {#if successMessage}
    <Alert color="green" class="mb-4">
      <span class="font-medium">{successMessage}</span>
    </Alert>
  {/if}
  {#if errorMessage}
    <Alert color="red" class="mb-4">
      <span class="font-medium">{errorMessage}</span>
    </Alert>
  {/if}

  <Card class="p-6">
    <h3 class="mb-4 text-base font-medium text-gray-700">数据备份与恢复</h3>
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
      <div class="space-y-3">
        <h4 class="text-sm font-semibold text-gray-600">备份数据</h4>
        <p class="text-sm text-gray-500">将当前数据库中的批次、笔记、测量记录、配方、提醒和菌种等全部数据导出为 JSON 备份文件。</p>
        <Button
          color="primary"
          on:click={handleDownloadBackup}
          disabled={backupLoading}
          class="w-full"
        >
          {#if backupLoading}
          <Spinner size="4" class="mr-2" />
          备份中...
          {:else}
          <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          下载备份文件
          {/if}
        </Button>
      </div>

      <div class="space-y-3">
        <h4 class="text-sm font-semibold text-gray-600">恢复数据</h4>
        <p class="text-sm text-gray-500">从备份文件恢复数据，将覆盖当前全部现有数据。</p>
        <div class="flex items-center justify-center w-full">
          <label for="backup-file" class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
            <div class="flex flex-col items-center justify-center pt-5 pb-6">
              <svg class="w-8 h-8 mb-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="mb-1 text-sm text-gray-500">
                {#if selectedFile}
                  <span class="font-medium text-blue-600">{selectedFile.name}</span>
                {:else}
                  <span>点击上传或拖拽备份文件</span>
                {/if}
              </p>
              <p class="text-xs text-gray-500">仅支持 .json 格式</p>
            </div>
            <input
              id="backup-file"
              type="file"
              accept=".json"
              class="hidden"
              bind:this={fileInput}
              on:change={handleFileSelect}
            />
          </label>
        </div>

        {#if selectedFile && !previewSummary}
          <Button
            color="blue"
            on:click={handlePreview}
            disabled={previewLoading}
            class="w-full"
          >
            {#if previewLoading}
              <Spinner size="4" class="mr-2" />
              校验中...
            {:else}
              校验文件并预览
            {/if}
          </Button>
        {/if}

        {#if previewSummary}
          <div class="rounded-lg bg-gray-50 p-4 text-sm">
            <p class="mb-2 font-medium text-gray-700">备份文件内容：</p>
            <div class="grid grid-cols-2 gap-2 text-gray-600">
              <div>批次：{previewSummary.batches}</div>
              <div>笔记：{previewSummary.notes}</div>
              <div>测量记录：{previewSummary.measurements}</div>
              <div>配方：{previewSummary.recipes}</div>
              <div>配方步骤：{previewSummary.recipe_steps}</div>
              <div>提醒：{previewSummary.reminders}</div>
              <div>菌种：{previewSummary.strains}</div>
            </div>
          </div>
          <div class="flex gap-2">
            <Button
              color="red"
              on:click={handleRestoreClick}
              disabled={restoreLoading}
              class="flex-1"
            >
              {#if restoreLoading}
                <Spinner size="4" class="mr-2" />
                恢复中...
              {:else}
                恢复数据
              {/if}
            </Button>
            <Button color="gray" on:click={resetRestoreForm} class="flex-1">
              重新选择
            </Button>
          </div>
        {/if}

        {#if restoreResult && restoreResult.success}
          <div class="rounded-lg bg-green-50 p-4 text-sm">
            <p class="font-medium text-green-700">恢复结果：</p>
            <div class="grid grid-cols-2 gap-2 text-green-600">
              <div>批次：{restoreResult.summary.batches}</div>
              <div>笔记：{restoreResult.summary.notes}</div>
              <div>测量记录：{restoreResult.summary.measurements}</div>
              <div>配方：{restoreResult.summary.recipes}</div>
              <div>菌种：{restoreResult.summary.strains}</div>
              <div>提醒：{restoreResult.summary.reminders}</div>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </Card>
</div>

<Modal bind:open={showConfirmModal} size="md" popup>
  <div class="text-center">
    <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
      <svg class="h-7 w-7 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    </div>
    <h3 class="mb-5 text-lg font-semibold text-gray-900">确认恢复数据？</h3>
    <div class="mb-5 space-y-3">
      <p class="text-sm text-gray-500">
      此操作将 <span class="font-semibold text-red-600">永久删除</span> 当前数据库中的所有数据，
      并替换为备份文件中的数据。此操作不可撤销！
      </p>
      <div class="flex items-center justify-center">
        <Checkbox
          bind:checked={confirmOverwrite}
          label="我已了解风险，确认覆盖现有全部数据"
          class="text-sm"
        />
      </div>
    </div>
    <div class="flex justify-center gap-3">
      <Button color="gray" on:click={() => { showConfirmModal = false; }}>
        取消
      </Button>
      <Button
        color="red"
        on:click={handleConfirmRestore}
        disabled={!confirmOverwrite || restoreLoading}
      >
        {#if restoreLoading}
          <Spinner size="4" class="mr-2" />
          恢复中...
        {:else}
          确认恢复
        {/if}
      </Button>
    </div>
  </div>
</Modal>
