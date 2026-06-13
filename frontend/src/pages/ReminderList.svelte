<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import RouterLink from '../components/RouterLink.svelte';
  import {
    Button,
    Input,
    Label,
    Badge,
    Spinner,
    Alert,
  } from 'flowbite-svelte';
  import {
    fetchReminders,
    createReminder,
    updateReminder,
    toggleReminderCompleted,
    deleteReminder,
    fetchBatches,
  } from '../lib/api';
  import type { Reminder, ReminderForm, Batch } from '../lib/types';

  const queryClient = useQueryClient();

  const remindersQuery = createQuery({
    queryKey: ['reminders'],
    queryFn: fetchReminders,
  });

  const batchesQuery = createQuery({
    queryKey: ['batches'],
    queryFn: () => fetchBatches(),
  });

  let showForm = $state(false);
  let form = $state<ReminderForm>({
    batch_id: 0,
    title: '',
    reminder_date: new Date().toISOString().slice(0, 10),
  });

  let editingId = $state<number | null>(null);
  let editForm = $state<ReminderForm>({
    batch_id: 0,
    title: '',
    reminder_date: '',
  });

  let togglingId = $state<number | null>(null);
  let deletingId = $state<number | null>(null);
  let updatingId = $state<number | null>(null);

  const createMutation_ = createMutation({
    mutationFn: createReminder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
      showForm = false;
      form = {
        batch_id: 0,
        title: '',
        reminder_date: new Date().toISOString().slice(0, 10),
      };
    },
  });

  const updateMutation_ = createMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<ReminderForm> }) =>
      updateReminder(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
      editingId = null;
      updatingId = null;
    },
  });

  const toggleMutation_ = createMutation({
    mutationFn: toggleReminderCompleted,
    onMutate: (id) => {
      togglingId = id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
    },
    onSettled: () => {
      togglingId = null;
    },
  });

  const deleteMutation_ = createMutation({
    mutationFn: deleteReminder,
    onMutate: (id) => {
      deletingId = id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
    },
    onSettled: () => {
      deletingId = null;
    },
  });

  function handleSubmit(e: Event) {
    e.preventDefault();
    if (form.batch_id === 0) return;
    $createMutation_.mutate(form);
  }

  function startEdit(reminder: Reminder) {
    editingId = reminder.id;
    editForm = {
      batch_id: reminder.batch_id,
      title: reminder.title,
      reminder_date: reminder.reminder_date,
    };
  }

  function cancelEdit() {
    editingId = null;
  }

  function saveEdit() {
    if (editingId === null || editForm.batch_id === 0) return;
    updatingId = editingId;
    $updateMutation_.mutate({ id: editingId, payload: editForm });
  }

  function getBatchById(batchId: number): Batch | undefined {
    return ($batchesQuery.data ?? []).find((b) => b.id === batchId);
  }

  const pendingReminders = $derived(($remindersQuery.data ?? []).filter((r) => !r.completed));
  const completedReminders = $derived(($remindersQuery.data ?? []).filter((r) => r.completed));
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-lg font-semibold text-gray-800">提醒待办</h2>
    <Button color="amber" onclick={() => (showForm = !showForm)}>
      {showForm ? '取消' : '+ 新建提醒'}
    </Button>
  </div>

  {#if showForm}
    <form
      class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      onsubmit={handleSubmit}
    >
      <h3 class="mb-4 text-base font-medium text-gray-700">新建提醒</h3>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <Label for="reminder-batch">关联批次</Label>
          <select
            id="reminder-batch"
            bind:value={form.batch_id}
            class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-amber-500 focus:ring-amber-500"
            required
          >
            <option value={0} disabled>请选择批次</option>
            {#each $batchesQuery.data ?? [] as batch}
              <option value={batch.id}>{batch.type} (开始于 {batch.start_date})</option>
            {/each}
          </select>
        </div>
        <div>
          <Label for="reminder-title">提醒标题</Label>
          <Input
            id="reminder-title"
            bind:value={form.title}
            placeholder="如：测量 pH 值"
            required
          />
        </div>
        <div>
          <Label for="reminder-date">提醒日期</Label>
          <Input
            id="reminder-date"
            type="date"
            bind:value={form.reminder_date}
            required
          />
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <Button type="submit" color="amber" disabled={$createMutation_.isPending}>
          {$createMutation_.isPending ? '保存中…' : '保存'}
        </Button>
      </div>
      {#if $createMutation_.isError}
        <Alert color="red" class="mt-3">创建失败，请检查后端是否已启动。</Alert>
      {/if}
    </form>
  {/if}

  {#if $remindersQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $remindersQuery.isError}
    <Alert color="red">无法加载提醒列表，请确认后端运行在 http://localhost:5000</Alert>
  {:else}
    {#if pendingReminders.length === 0 && completedReminders.length === 0}
      <Alert color="yellow">暂无提醒，点击「新建提醒」开始记录。</Alert>
    {:else}
      {#if pendingReminders.length > 0}
        <div class="space-y-3">
          <h3 class="text-base font-medium text-gray-700">待完成 ({pendingReminders.length})</h3>
          <div class="space-y-2">
            {#each pendingReminders as reminder (reminder.id)}
              <div
                class="rounded-lg border border-amber-200 bg-amber-50 p-3 shadow-sm"
              >
                {#if editingId === reminder.id}
                  <div class="space-y-3">
                    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
                      <div>
                        <Label for={`edit-batch-${reminder.id}`}>关联批次</Label>
                        <select
                          id={`edit-batch-${reminder.id}`}
                          bind:value={editForm.batch_id}
                          class="block w-full rounded-lg border border-gray-300 bg-white p-2.5 text-sm text-gray-900 focus:border-amber-500 focus:ring-amber-500"
                          disabled={updatingId === reminder.id}
                        >
                          <option value={0} disabled>请选择批次</option>
                          {#each $batchesQuery.data ?? [] as batch}
                            <option value={batch.id}>{batch.type} (开始于 {batch.start_date})</option>
                          {/each}
                        </select>
                      </div>
                      <div>
                        <Label for={`edit-title-${reminder.id}`}>提醒标题</Label>
                        <Input
                          id={`edit-title-${reminder.id}`}
                          bind:value={editForm.title}
                          disabled={updatingId === reminder.id}
                        />
                      </div>
                      <div>
                        <Label for={`edit-date-${reminder.id}`}>提醒日期</Label>
                        <Input
                          id={`edit-date-${reminder.id}`}
                          type="date"
                          bind:value={editForm.reminder_date}
                          disabled={updatingId === reminder.id}
                        />
                      </div>
                    </div>
                    <div class="flex gap-2">
                      <Button
                        size="xs"
                        color="amber"
                        disabled={updatingId === reminder.id}
                        onclick={saveEdit}
                      >
                        {updatingId === reminder.id ? '保存中…' : '保存'}
                      </Button>
                      <Button
                        size="xs"
                        color="gray"
                        outline
                        disabled={updatingId === reminder.id}
                        onclick={cancelEdit}
                      >
                        取消
                      </Button>
                    </div>
                  </div>
                {:else}
                  <div class="flex items-center gap-3">
                    <input
                      type="checkbox"
                      class="h-5 w-5 cursor-pointer rounded border-gray-300 text-amber-600 focus:ring-amber-500"
                      checked={reminder.completed}
                      disabled={togglingId === reminder.id}
                      onchange={() => $toggleMutation_.mutate(reminder.id)}
                    />
                    <div class="flex-1 min-w-0">
                      <div class="flex flex-wrap items-center gap-2">
                        <span class="font-medium text-gray-900">{reminder.title}</span>
                        <RouterLink
                          to="/batches/{reminder.batch_id}"
                          class="text-sm text-amber-700 hover:underline"
                        >
                          批次：{getBatchById(reminder.batch_id)?.type ?? `#${reminder.batch_id}`}
                        </RouterLink>
                      </div>
                      <div class="mt-1 text-sm text-gray-600">
                        提醒日期：{reminder.reminder_date}
                      </div>
                    </div>
                    <div class="flex gap-1">
                      <Button
                        size="xs"
                        color="amber"
                        outline
                        onclick={() => startEdit(reminder)}
                      >
                        编辑
                      </Button>
                      <Button
                        size="xs"
                        color="red"
                        outline
                        disabled={deletingId === reminder.id}
                        onclick={() => {
                          if (confirm(`确定删除提醒「${reminder.title}」？`)) {
                            $deleteMutation_.mutate(reminder.id);
                          }
                        }}
                      >
                        删除
                      </Button>
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if completedReminders.length > 0}
        <div class="space-y-3 pt-4">
          <h3 class="text-base font-medium text-gray-500">已完成 ({completedReminders.length})</h3>
          <div class="space-y-2">
            {#each completedReminders as reminder (reminder.id)}
              <div
                class="rounded-lg border border-gray-200 bg-gray-50 p-3 shadow-sm opacity-70"
              >
                {#if editingId === reminder.id}
                  <div class="space-y-3">
                    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
                      <div>
                        <Label for={`edit-batch-${reminder.id}`}>关联批次</Label>
                        <select
                          id={`edit-batch-${reminder.id}`}
                          bind:value={editForm.batch_id}
                          class="block w-full rounded-lg border border-gray-300 bg-white p-2.5 text-sm text-gray-900 focus:border-amber-500 focus:ring-amber-500"
                          disabled={updatingId === reminder.id}
                        >
                          <option value={0} disabled>请选择批次</option>
                          {#each $batchesQuery.data ?? [] as batch}
                            <option value={batch.id}>{batch.type} (开始于 {batch.start_date})</option>
                          {/each}
                        </select>
                      </div>
                      <div>
                        <Label for={`edit-title-${reminder.id}`}>提醒标题</Label>
                        <Input
                          id={`edit-title-${reminder.id}`}
                          bind:value={editForm.title}
                          disabled={updatingId === reminder.id}
                        />
                      </div>
                      <div>
                        <Label for={`edit-date-${reminder.id}`}>提醒日期</Label>
                        <Input
                          id={`edit-date-${reminder.id}`}
                          type="date"
                          bind:value={editForm.reminder_date}
                          disabled={updatingId === reminder.id}
                        />
                      </div>
                    </div>
                    <div class="flex gap-2">
                      <Button
                        size="xs"
                        color="amber"
                        disabled={updatingId === reminder.id}
                        onclick={saveEdit}
                      >
                        {updatingId === reminder.id ? '保存中…' : '保存'}
                      </Button>
                      <Button
                        size="xs"
                        color="gray"
                        outline
                        disabled={updatingId === reminder.id}
                        onclick={cancelEdit}
                      >
                        取消
                      </Button>
                    </div>
                  </div>
                {:else}
                  <div class="flex items-center gap-3">
                    <input
                      type="checkbox"
                      class="h-5 w-5 cursor-pointer rounded border-gray-300 text-amber-600 focus:ring-amber-500"
                      checked={reminder.completed}
                      disabled={togglingId === reminder.id}
                      onchange={() => $toggleMutation_.mutate(reminder.id)}
                    />
                    <div class="flex-1 min-w-0">
                      <div class="flex flex-wrap items-center gap-2">
                        <span class="font-medium text-gray-500 line-through">{reminder.title}</span>
                        <RouterLink
                          to="/batches/{reminder.batch_id}"
                          class="text-sm text-gray-500 hover:underline line-through"
                        >
                          批次：{getBatchById(reminder.batch_id)?.type ?? `#${reminder.batch_id}`}
                        </RouterLink>
                        <Badge color="green">已完成</Badge>
                      </div>
                      <div class="mt-1 text-sm text-gray-400">
                        提醒日期：{reminder.reminder_date}
                      </div>
                    </div>
                    <div class="flex gap-1">
                      <Button
                        size="xs"
                        color="amber"
                        outline
                        onclick={() => startEdit(reminder)}
                      >
                        编辑
                      </Button>
                      <Button
                        size="xs"
                        color="red"
                        outline
                        disabled={deletingId === reminder.id}
                        onclick={() => {
                          if (confirm(`确定删除提醒「${reminder.title}」？`)) {
                            $deleteMutation_.mutate(reminder.id);
                          }
                        }}
                      >
                        删除
                      </Button>
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    {/if}
  {/if}
</div>
