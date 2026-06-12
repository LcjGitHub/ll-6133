<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import { Link } from 'svelte-routing';
  import {
    Button,
    Input,
    Label,
    Select,
    Textarea,
    Badge,
    Spinner,
    Alert,
    Card,
  } from 'flowbite-svelte';
  import { fetchBatch, updateBatch, createNote, deleteNote } from '../lib/api';
  import type { BatchForm } from '../lib/types';

  interface Props {
    id: string;
  }

  let { id }: Props = $props();

  const batchId = $derived(parseInt(id, 10));
  const queryClient = useQueryClient();

  const batchQuery = createQuery(() => ({
    queryKey: ['batch', batchId],
    queryFn: () => fetchBatch(batchId),
    enabled: !Number.isNaN(batchId),
  }));

  let editMode = $state(false);
  let noteContent = $state('');
  let form = $state<BatchForm>({
    type: '',
    start_date: '',
    temperature: 25,
    status: '发酵中',
    ph: null,
  });

  const statusOptions = ['发酵中', '观察中', '已完成'];

  $effect(() => {
    const data = $batchQuery.data;
    if (data) {
      form = {
        type: data.type,
        start_date: data.start_date,
        temperature: data.temperature,
        status: data.status,
        ph: data.ph,
      };
    }
  });

  const updateMutation_ = createMutation({
    mutationFn: (payload: Partial<BatchForm>) => updateBatch(batchId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', batchId] });
      queryClient.invalidateQueries({ queryKey: ['batches'] });
      editMode = false;
    },
  });

  const noteMutation_ = createMutation({
    mutationFn: (content: string) => createNote(batchId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', batchId] });
      noteContent = '';
    },
  });

  const deleteNoteMutation_ = createMutation({
    mutationFn: deleteNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', batchId] });
    },
  });

  /** 保存批次编辑 */
  function handleUpdate(e: Event) {
    e.preventDefault();
    const payload: Partial<BatchForm> = {
      ...form,
      ph: form.ph === null || Number.isNaN(form.ph) ? null : form.ph,
    };
    $updateMutation_.mutate(payload);
  }

  /** 追加笔记 */
  function handleAddNote(e: Event) {
    e.preventDefault();
    const trimmed = noteContent.trim();
    if (!trimmed) return;
    $noteMutation_.mutate(trimmed);
  }

  /** 格式化时间 */
  function formatTime(iso: string): string {
    return new Date(iso).toLocaleString('zh-CN');
  }

  /** 状态徽章颜色 */
  function statusColor(status: string): 'green' | 'yellow' | 'blue' | 'gray' {
    if (status === '已完成') return 'green';
    if (status === '观察中') return 'yellow';
    if (status === '发酵中') return 'blue';
    return 'gray';
  }
</script>

<div class="space-y-6">
  <Link to="/" class="inline-flex items-center text-sm text-blue-600 hover:underline">
    ← 返回列表
  </Link>

  {#if Number.isNaN(batchId)}
    <Alert color="red">无效的批次 ID</Alert>
  {:else if $batchQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $batchQuery.isError}
    <Alert color="red">批次不存在或后端未启动</Alert>
  {:else if $batchQuery.data}
    {@const batch = $batchQuery.data}

    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-800">{batch.type}</h2>
      <div class="flex gap-2">
        <Badge color={statusColor(batch.status)} large>{batch.status}</Badge>
        <Button size="sm" color="light" onclick={() => (editMode = !editMode)}>
          {editMode ? '取消编辑' : '编辑'}
        </Button>
      </div>
    </div>

    {#if editMode}
      <Card class="max-w-none">
        <form onsubmit={handleUpdate} class="space-y-4">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <Label for="edit-type">类型</Label>
              <Input id="edit-type" bind:value={form.type} required />
            </div>
            <div>
              <Label for="edit-date">开始日期</Label>
              <Input id="edit-date" type="date" bind:value={form.start_date} required />
            </div>
            <div>
              <Label for="edit-temp">温度 (°C)</Label>
              <Input id="edit-temp" type="number" step="0.1" bind:value={form.temperature} required />
            </div>
            <div>
              <Label for="edit-status">状态</Label>
              <Select
                id="edit-status"
                bind:value={form.status}
                items={statusOptions.map((s) => ({ value: s, name: s }))}
              />
            </div>
            <div>
              <Label for="edit-ph">pH（可选）</Label>
              <Input
                id="edit-ph"
                type="number"
                step="0.1"
                min="0"
                max="14"
                value={form.ph ?? ''}
                oninput={(e) => {
                  const v = (e.target as HTMLInputElement).value;
                  form.ph = v === '' ? null : parseFloat(v);
                }}
              />
            </div>
          </div>
          <Button type="submit" color="blue" disabled={$updateMutation_.isPending}>
            {$updateMutation_.isPending ? '保存中…' : '保存修改'}
          </Button>
        </form>
      </Card>
    {:else}
      <Card class="max-w-none">
        <dl class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div>
            <dt class="text-sm text-gray-500">开始日期</dt>
            <dd class="font-medium">{batch.start_date}</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">温度</dt>
            <dd class="font-medium">{batch.temperature}°C</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">pH</dt>
            <dd class="font-medium">{batch.ph ?? '—'}</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">创建时间</dt>
            <dd class="font-medium">{formatTime(batch.created_at)}</dd>
          </div>
        </dl>
      </Card>
    {/if}

    <section class="space-y-4">
      <h3 class="text-base font-semibold text-gray-800">观察笔记</h3>

      <form
        class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
        onsubmit={handleAddNote}
      >
        <Label for="note-content">追加笔记</Label>
        <Textarea
          id="note-content"
          bind:value={noteContent}
          rows={3}
          placeholder="记录气味、气泡、颜色变化等观察…"
          class="mt-1"
        />
        <Button
          type="submit"
          color="blue"
          class="mt-3"
          disabled={$noteMutation_.isPending || !noteContent.trim()}
        >
          {$noteMutation_.isPending ? '提交中…' : '追加笔记'}
        </Button>
      </form>

      {#if batch.notes.length === 0}
        <Alert color="yellow">暂无观察笔记，在上方表单追加第一条。</Alert>
      {:else}
        <ul class="space-y-3">
          {#each batch.notes as note (note.id)}
            <li class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <div class="mb-2 flex items-start justify-between gap-2">
                <time class="text-xs text-gray-400">{formatTime(note.created_at)}</time>
                <Button
                  size="xs"
                  color="red"
                  outline
                  disabled={$deleteNoteMutation_.isPending}
                  onclick={() => {
                    if (confirm('确定删除这条笔记？')) {
                      $deleteNoteMutation_.mutate(note.id);
                    }
                  }}
                >
                  删除
                </Button>
              </div>
              <p class="whitespace-pre-wrap text-gray-700">{note.content}</p>
            </li>
          {/each}
        </ul>
      {/if}
    </section>
  {/if}
</div>
