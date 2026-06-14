<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import RouterLink from '../components/RouterLink.svelte';
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
  import { fetchBatch, updateBatch, createNote, deleteNote, updateNote, createMeasurement, extractErrorDetail } from '../lib/api';
  import type { BatchForm, MeasurementForm } from '../lib/types';

  interface Props {
    id: string;
  }

  let { id }: Props = $props();

  const isValidId = /^\d+$/.test(id);
  const numericId = parseInt(id, 10);

  const queryClient = useQueryClient();

  const batchQuery = createQuery({
    queryKey: ['batch', id],
    queryFn: () => fetchBatch(numericId),
    enabled: isValidId,
  });

  const NOTE_MAX_LENGTH = 2000;

  let editMode = $state(false);
  let noteContent = $state('');
  let editingNoteId = $state<number | null>(null);
  let editingNoteContent = $state('');
  let updateNoteError = $state<string>('');

  function defaultMeasurementForm(): MeasurementForm {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return {
      recorded_at: now.toISOString().slice(0, 16),
      temperature: 25,
      ph: null,
    };
  }

  let measurementForm = $state<MeasurementForm>(defaultMeasurementForm());

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
    mutationFn: (payload: Partial<BatchForm>) => updateBatch(numericId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', id] });
      queryClient.invalidateQueries({ queryKey: ['batches'], exact: false });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      editMode = false;
    },
  });

  const statusMutation_ = createMutation({
    mutationFn: (status: string) => updateBatch(numericId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', id] });
      queryClient.invalidateQueries({ queryKey: ['batches'], exact: false });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
    },
  });

  function handleStatusChange(newStatus: string) {
    const currentStatus = $batchQuery.data?.status;
    if (newStatus === currentStatus) return;
    $statusMutation_.mutate(newStatus);
  }

  const noteMutation_ = createMutation({
    mutationFn: (content: string) => createNote(numericId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', id] });
      noteContent = '';
    },
  });

  const deleteNoteMutation_ = createMutation({
    mutationFn: deleteNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', id] });
    },
  });

  const updateNoteMutation_ = createMutation({
    mutationFn: ({ noteId, content }: { noteId: number; content: string }) =>
      updateNote(noteId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', id] });
      editingNoteId = null;
      editingNoteContent = '';
      updateNoteError = '';
    },
    onError: async (error) => {
      updateNoteError = await extractErrorDetail(error);
    },
  });

  function startEditNote(noteId: number, content: string) {
    editingNoteId = noteId;
    editingNoteContent = content;
    updateNoteError = '';
  }

  function cancelEditNote() {
    editingNoteId = null;
    editingNoteContent = '';
    updateNoteError = '';
  }

  function handleSaveNote(e: Event) {
    e.preventDefault();
    if (editingNoteId === null) return;
    const trimmed = editingNoteContent.trim();
    if (!trimmed) return;
    if (trimmed.length > NOTE_MAX_LENGTH) return;
    $updateNoteMutation_.mutate({ noteId: editingNoteId, content: trimmed });
  }

  const measurementMutation_ = createMutation({
    mutationFn: (payload: MeasurementForm) => createMeasurement(numericId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', id] });
      measurementForm = defaultMeasurementForm();
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

  /** 追加测量记录 */
  function handleAddMeasurement(e: Event) {
    e.preventDefault();
    const payload: MeasurementForm = {
      ...measurementForm,
      ph: measurementForm.ph === null || Number.isNaN(measurementForm.ph) ? null : measurementForm.ph,
    };
    $measurementMutation_.mutate(payload);
  }

  /** 格式化时间 */
  function formatTime(iso: string): string {
    return new Date(iso).toLocaleString('zh-CN');
  }

  /** 状态徽章颜色 */
  function statusColor(): 'dark' {
    return 'dark';
  }
</script>

<div class="space-y-6">
  <RouterLink to="/" class="inline-flex items-center text-sm text-blue-600 hover:underline">
    ← 返回列表
  </RouterLink>

  {#if !isValidId}
    <Alert color="red">无效的批次 ID</Alert>
  {:else if $batchQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $batchQuery.isError}
    <Alert color="red">批次不存在或后端未启动</Alert>
  {:else if $batchQuery.data}
    {@const batch = $batchQuery.data}

    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <h2 class="text-lg font-semibold text-gray-800">{batch.type}</h2>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div class="flex flex-wrap gap-2">
          {#each statusOptions as status}
            <Button
              size="sm"
              color={batch.status === status ? 'blue' : 'light'}
              onclick={() => handleStatusChange(status)}
              disabled={$statusMutation_.isPending || batch.status === status}
            >
              {$statusMutation_.isPending && batch.status !== status ? '切换中…' : status}
            </Button>
          {/each}
        </div>
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
        <dl class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <div>
            <dt class="text-sm text-gray-500">开始日期</dt>
            <dd class="font-medium">{batch.start_date}</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">已发酵天数</dt>
            <dd class="font-medium">
              <span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                {batch.fermentation_days} 天
              </span>
            </dd>
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
      <h3 class="text-base font-semibold text-gray-800">测量记录</h3>

      <form
        class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
        onsubmit={handleAddMeasurement}
      >
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <Label for="meas-recorded-at">记录时间</Label>
            <Input
              id="meas-recorded-at"
              type="datetime-local"
              bind:value={measurementForm.recorded_at}
              required
              class="mt-1"
            />
          </div>
          <div>
            <Label for="meas-temp">温度 (°C)</Label>
            <Input
              id="meas-temp"
              type="number"
              step="0.1"
              bind:value={measurementForm.temperature}
              required
              class="mt-1"
            />
          </div>
          <div>
            <Label for="meas-ph">pH（可选）</Label>
            <Input
              id="meas-ph"
              type="number"
              step="0.1"
              min="0"
              max="14"
              value={measurementForm.ph ?? ''}
              class="mt-1"
              oninput={(e) => {
                const v = (e.target as HTMLInputElement).value;
                measurementForm.ph = v === '' ? null : parseFloat(v);
              }}
            />
          </div>
        </div>
        <Button
          type="submit"
          color="blue"
          class="mt-3"
          disabled={$measurementMutation_.isPending}
        >
          {$measurementMutation_.isPending ? '提交中…' : '追加测量记录'}
        </Button>
      </form>

      {#if batch.measurements.length === 0}
        <Alert color="yellow">暂无测量记录，在上方表单追加第一条。</Alert>
      {:else}
        <div class="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">记录时间</th>
                <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">温度 (°C)</th>
                <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">pH</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              {#each batch.measurements as m (m.id)}
                <tr class="hover:bg-gray-50">
                  <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{formatTime(m.recorded_at)}</td>
                  <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{m.temperature.toFixed(1)}</td>
                  <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{m.ph?.toFixed(1) ?? '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </section>

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
              {#if editingNoteId === note.id}
                <form onsubmit={handleSaveNote} class="space-y-3">
                  {#if updateNoteError}
                    <Alert color="red">{updateNoteError}</Alert>
                  {/if}
                  <div class="flex items-start justify-between gap-2">
                    <time class="text-xs text-gray-400">{formatTime(note.created_at)}</time>
                    <div class="flex gap-2">
                      <Button
                        size="xs"
                        color="blue"
                        type="submit"
                        disabled={$updateNoteMutation_.isPending || !editingNoteContent.trim() || editingNoteContent.trim().length > NOTE_MAX_LENGTH}
                      >
                        {$updateNoteMutation_.isPending ? '保存中…' : '保存'}
                      </Button>
                      <Button
                        size="xs"
                        color="light"
                        type="button"
                        onclick={cancelEditNote}
                        disabled={$updateNoteMutation_.isPending}
                      >
                        取消
                      </Button>
                    </div>
                  </div>
                  <Textarea
                    bind:value={editingNoteContent}
                    rows={3}
                    autofocus
                    maxlength={NOTE_MAX_LENGTH}
                  />
                  <div class="text-right text-xs">
                    {#if editingNoteContent.trim().length > NOTE_MAX_LENGTH}
                      <span class="text-red-500">字数超限（{editingNoteContent.trim().length}/{NOTE_MAX_LENGTH}）</span>
                    {:else}
                      <span class="text-gray-400">{editingNoteContent.trim().length}/{NOTE_MAX_LENGTH}</span>
                    {/if}
                  </div>
                </form>
              {:else}
                <div class="mb-2 flex items-start justify-between gap-2">
                  <time class="text-xs text-gray-400">{formatTime(note.created_at)}</time>
                  <div class="flex gap-2">
                    <Button
                      size="xs"
                      color="light"
                      onclick={() => startEditNote(note.id, note.content)}
                      disabled={$deleteNoteMutation_.isPending || editingNoteId !== null}
                    >
                      编辑
                    </Button>
                    <Button
                      size="xs"
                      color="red"
                      outline
                      disabled={$deleteNoteMutation_.isPending || editingNoteId !== null}
                      onclick={() => {
                        if (confirm('确定删除这条笔记？')) {
                          $deleteNoteMutation_.mutate(note.id);
                        }
                      }}
                    >
                      删除
                    </Button>
                  </div>
                </div>
                <p class="whitespace-pre-wrap text-gray-700">{note.content}</p>
              {/if}
            </li>
          {/each}
        </ul>
      {/if}
    </section>
  {/if}
</div>
