<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import {
    Button,
    Input,
    Label,
    Textarea,
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
  import {
    fetchStrains,
    createStrain,
    updateStrain,
    deleteStrain,
  } from '../lib/api';
  import type { Strain, StrainForm } from '../lib/types';

  const queryClient = useQueryClient();

  const strainsQuery = createQuery({
    queryKey: ['strains'],
    queryFn: fetchStrains,
  });

  let showForm = $state(false);
  let form = $state<StrainForm>({
    name: '',
    ferment_type: '',
    activation_date: new Date().toISOString().slice(0, 10),
    storage_location: '',
    notes: '',
  });

  let editingId = $state<number | null>(null);
  let editForm = $state<StrainForm>({
    name: '',
    ferment_type: '',
    activation_date: '',
    storage_location: '',
    notes: '',
  });
  let updatingId = $state<number | null>(null);
  let deletingId = $state<number | null>(null);

  const fermentTypeOptions = ['康普茶', '泡菜', '酸面包', '其他'];

  const createMutation_ = createMutation({
    mutationFn: createStrain,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strains'] });
      showForm = false;
      form = {
        name: '',
        ferment_type: '',
        activation_date: new Date().toISOString().slice(0, 10),
        storage_location: '',
        notes: '',
      };
    },
  });

  const updateMutation_ = createMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<StrainForm> }) =>
      updateStrain(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strains'] });
      editingId = null;
      updatingId = null;
    },
  });

  const deleteMutation_ = createMutation({
    mutationFn: deleteStrain,
    onMutate: (id) => {
      deletingId = id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strains'] });
    },
    onSettled: () => {
      deletingId = null;
    },
  });

  function handleSubmit(e: Event) {
    e.preventDefault();
    if (!form.ferment_type) return;
    const payload = { ...form, notes: form.notes || null };
    $createMutation_.mutate(payload);
  }

  function startEdit(strain: Strain) {
    editingId = strain.id;
    editForm = {
      name: strain.name,
      ferment_type: strain.ferment_type,
      activation_date: strain.activation_date,
      storage_location: strain.storage_location,
      notes: strain.notes ?? '',
    };
  }

  function cancelEdit() {
    editingId = null;
  }

  function saveEdit() {
    if (editingId === null || !editForm.ferment_type) return;
    updatingId = editingId;
    const payload = { ...editForm, notes: editForm.notes || null };
    $updateMutation_.mutate({ id: editingId, payload });
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-lg font-semibold text-gray-800">菌种管理</h2>
    <Button color="cyan" onclick={() => (showForm = !showForm)}>
      {showForm ? '取消' : '+ 新建菌种'}
    </Button>
  </div>

  {#if showForm}
    <form
      class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      onsubmit={handleSubmit}
    >
      <h3 class="mb-4 text-base font-medium text-gray-700">新建菌种</h3>
      <div class="space-y-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label for="strain-name">菌种名称</Label>
            <Input
              id="strain-name"
              bind:value={form.name}
              placeholder="如：康普茶 SCOBY 初代"
              required
            />
          </div>
          <div>
            <Label for="strain-ferment-type">适用发酵类型</Label>
            <select
              id="strain-ferment-type"
              bind:value={form.ferment_type}
              class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-cyan-500 focus:ring-cyan-500"
              required
            >
              <option value="" disabled>请选择类型</option>
              {#each fermentTypeOptions as type}
                <option value={type}>{type}</option>
              {/each}
            </select>
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label for="strain-activation-date">激活日期</Label>
            <Input
              id="strain-activation-date"
              type="date"
              bind:value={form.activation_date}
              required
            />
          </div>
          <div>
            <Label for="strain-storage">存放位置</Label>
            <Input
              id="strain-storage"
              bind:value={form.storage_location}
              placeholder="如：冰箱冷藏室 4°C"
              required
            />
          </div>
        </div>
        <div>
          <Label for="strain-notes">备注说明</Label>
          <Textarea
            id="strain-notes"
            bind:value={form.notes}
            rows={3}
            placeholder="菌种来源、使用方法、注意事项等…"
          />
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <Button type="submit" color="cyan" disabled={$createMutation_.isPending}>
          {$createMutation_.isPending ? '保存中…' : '保存'}
        </Button>
      </div>
      {#if $createMutation_.isError}
        <Alert color="red" class="mt-3">创建失败，请检查后端是否已启动。</Alert>
      {/if}
    </form>
  {/if}

  {#if $strainsQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $strainsQuery.isError}
    <Alert color="red">无法加载菌种列表，请确认后端运行在 http://localhost:5000</Alert>
  {:else if ($strainsQuery.data ?? []).length === 0}
    <Alert color="yellow">暂无菌种，点击「新建菌种」开始记录。</Alert>
  {:else}
    <div class="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
      <Table hoverable>
        <TableHead>
          <TableHeadCell>菌种名称</TableHeadCell>
          <TableHeadCell>适用类型</TableHeadCell>
          <TableHeadCell>激活日期</TableHeadCell>
          <TableHeadCell>存放位置</TableHeadCell>
          <TableHeadCell>备注说明</TableHeadCell>
          <TableHeadCell>操作</TableHeadCell>
        </TableHead>
        <TableBody>
          {#each $strainsQuery.data ?? [] as strain (strain.id)}
            {#if editingId === strain.id}
              <TableBodyRow class="bg-cyan-50">
                <TableBodyCell>
                  <Input
                    bind:value={editForm.name}
                    size="sm"
                    disabled={updatingId === strain.id}
                  />
                </TableBodyCell>
                <TableBodyCell>
                  <select
                    bind:value={editForm.ferment_type}
                    class="block w-full rounded-lg border border-gray-300 bg-white p-2 text-xs text-gray-900 focus:border-cyan-500 focus:ring-cyan-500"
                    disabled={updatingId === strain.id}
                  >
                    {#each fermentTypeOptions as type}
                      <option value={type}>{type}</option>
                    {/each}
                  </select>
                </TableBodyCell>
                <TableBodyCell>
                  <Input
                    type="date"
                    bind:value={editForm.activation_date}
                    size="sm"
                    disabled={updatingId === strain.id}
                  />
                </TableBodyCell>
                <TableBodyCell>
                  <Input
                    bind:value={editForm.storage_location}
                    size="sm"
                    disabled={updatingId === strain.id}
                  />
                </TableBodyCell>
                <TableBodyCell>
                  <Textarea
                    bind:value={editForm.notes}
                    rows={1}
                    disabled={updatingId === strain.id}
                  />
                </TableBodyCell>
                <TableBodyCell>
                  <div class="flex gap-1 whitespace-nowrap">
                    <Button
                      size="xs"
                      color="cyan"
                      disabled={updatingId === strain.id}
                      onclick={saveEdit}
                    >
                      {updatingId === strain.id ? '保存中…' : '保存'}
                    </Button>
                    <Button
                      size="xs"
                      color="gray"
                      outline
                      disabled={updatingId === strain.id}
                      onclick={cancelEdit}
                    >
                      取消
                    </Button>
                  </div>
                </TableBodyCell>
              </TableBodyRow>
            {:else}
              <TableBodyRow>
                <TableBodyCell class="font-medium text-gray-900">
                  {strain.name}
                </TableBodyCell>
                <TableBodyCell>
                  <Badge color="cyan">{strain.ferment_type}</Badge>
                </TableBodyCell>
                <TableBodyCell class="text-gray-500">
                  {strain.activation_date}
                </TableBodyCell>
                <TableBodyCell class="text-gray-600">
                  {strain.storage_location}
                </TableBodyCell>
                <TableBodyCell class="max-w-xs truncate text-gray-500">
                  {strain.notes ?? '—'}
                </TableBodyCell>
                <TableBodyCell>
                  <div class="flex gap-1 whitespace-nowrap">
                    <Button
                      size="xs"
                      color="cyan"
                      outline
                      onclick={() => startEdit(strain)}
                    >
                      编辑
                    </Button>
                    <Button
                      size="xs"
                      color="red"
                      outline
                      disabled={deletingId === strain.id}
                      onclick={() => {
                        if (confirm(`确定删除菌种「${strain.name}」？`)) {
                          $deleteMutation_.mutate(strain.id);
                        }
                      }}
                    >
                      删除
                    </Button>
                  </div>
                </TableBodyCell>
              </TableBodyRow>
            {/if}
          {/each}
        </TableBody>
      </Table>
    </div>
  {/if}
</div>
