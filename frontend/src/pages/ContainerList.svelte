<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import {
    Button,
    Input,
    Label,
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
    Badge,
    Spinner,
    Alert,
    Checkbox,
  } from 'flowbite-svelte';
  import {
    fetchContainers,
    createContainer,
    updateContainer,
    deleteContainer,
    fetchBatches,
  } from '../lib/api';
  import { navigate } from '../lib/router';
  import type { Container, ContainerForm, Batch } from '../lib/types';

  const queryClient = useQueryClient();

  const containersQuery = createQuery({
    queryKey: ['containers'],
    queryFn: fetchContainers,
  });

  const batchesQuery = createQuery({
    queryKey: ['batches'],
    queryFn: () => fetchBatches(),
  });

  let showForm = $state(false);
  let form = $state<ContainerForm>({
    name: '',
    capacity_ml: 1000,
    material: '',
    in_use: false,
    current_batch_id: null,
  });

  let editingId = $state<number | null>(null);
  let editForm = $state<ContainerForm>({
    name: '',
    capacity_ml: 0,
    material: '',
    in_use: false,
    current_batch_id: null,
  });
  let updatingId = $state<number | null>(null);
  let deletingId = $state<number | null>(null);

  const materialOptions = ['玻璃', '陶瓷', '不锈钢', '塑料', '其他'];

  const createMutation_ = createMutation({
    mutationFn: createContainer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['containers'] });
      showForm = false;
      form = {
        name: '',
        capacity_ml: 1000,
        material: '',
        in_use: false,
        current_batch_id: null,
      };
    },
  });

  const updateMutation_ = createMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<ContainerForm> }) =>
      updateContainer(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['containers'] });
      editingId = null;
      updatingId = null;
    },
  });

  const deleteMutation_ = createMutation({
    mutationFn: deleteContainer,
    onMutate: (id) => {
      deletingId = id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['containers'] });
    },
    onSettled: () => {
      deletingId = null;
    },
  });

  function handleSubmit(e: Event) {
    e.preventDefault();
    if (!form.material) return;
    const payload = { ...form };
    if (!payload.in_use) {
      payload.current_batch_id = null;
    }
    $createMutation_.mutate(payload);
  }

  function startEdit(container: Container) {
    editingId = container.id;
    editForm = {
      name: container.name,
      capacity_ml: container.capacity_ml,
      material: container.material,
      in_use: container.in_use,
      current_batch_id: container.current_batch_id,
    };
  }

  function cancelEdit() {
    editingId = null;
  }

  function saveEdit() {
    if (editingId === null || !editForm.material) return;
    updatingId = editingId;
    const payload = { ...editForm };
    if (!payload.in_use) {
      payload.current_batch_id = null;
    }
    $updateMutation_.mutate({ id: editingId, payload });
  }

  function goToBatch(batchId: number) {
    navigate(`/batches/${batchId}`);
  }

  function getBatchType(batchId: number | null): string {
    if (batchId === null) return '';
    const batch = ($batchesQuery.data ?? []).find((b) => b.id === batchId);
    return batch ? batch.type : '';
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-lg font-semibold text-gray-800">容器管理</h2>
    <Button color="teal" onclick={() => (showForm = !showForm)}>
      {showForm ? '取消' : '+ 新建容器'}
    </Button>
  </div>

  {#if showForm}
    <form
      class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      onsubmit={handleSubmit}
    >
      <h3 class="mb-4 text-base font-medium text-gray-700">新建容器</h3>
      <div class="space-y-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label for="container-name">容器名称</Label>
            <Input
              id="container-name"
              bind:value={form.name}
              placeholder="如：1号发酵罐"
              required
            />
          </div>
          <div>
            <Label for="container-capacity">容量 (毫升)</Label>
            <Input
              id="container-capacity"
              type="number"
              min="1"
              bind:value={form.capacity_ml}
              required
            />
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label for="container-material">材质</Label>
            <select
              id="container-material"
              bind:value={form.material}
              class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-teal-500 focus:ring-teal-500"
              required
            >
              <option value="" disabled>请选择材质</option>
              {#each materialOptions as material}
                <option value={material}>{material}</option>
              {/each}
            </select>
          </div>
          <div class="flex items-end">
            <Checkbox
              id="container-in-use"
              bind:checked={form.in_use}
              label="是否正在使用中"
            />
          </div>
        </div>
        {#if form.in_use}
          <div>
            <Label for="container-batch">关联批次</Label>
            <select
              id="container-batch"
              bind:value={form.current_batch_id}
              class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-teal-500 focus:ring-teal-500"
            >
              <option value={null}>请选择批次</option>
              {#each $batchesQuery.data ?? [] as batch}
                <option value={batch.id}>{batch.id} - {batch.type}</option>
              {/each}
            </select>
          </div>
        {/if}
      </div>
      <div class="mt-4 flex gap-2">
        <Button type="submit" color="teal" disabled={$createMutation_.isPending}>
          {$createMutation_.isPending ? '保存中…' : '保存'}
        </Button>
      </div>
      {#if $createMutation_.isError}
        <Alert color="red" class="mt-3">创建失败，请检查后端是否已启动。</Alert>
      {/if}
    </form>
  {/if}

  {#if $containersQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $containersQuery.isError}
    <Alert color="red">无法加载容器列表，请确认后端运行在 http://localhost:5000</Alert>
  {:else if ($containersQuery.data ?? []).length === 0}
    <Alert color="yellow">暂无容器，点击「新建容器」开始记录。</Alert>
  {:else}
    <div class="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
      <Table hoverable>
        <TableHead>
          <TableHeadCell>容器名称</TableHeadCell>
          <TableHeadCell>容量</TableHeadCell>
          <TableHeadCell>材质</TableHeadCell>
          <TableHeadCell>使用状态</TableHeadCell>
          <TableHeadCell>关联批次</TableHeadCell>
          <TableHeadCell>操作</TableHeadCell>
        </TableHead>
        <TableBody>
          {#each $containersQuery.data ?? [] as container (container.id)}
            {#if editingId === container.id}
              <TableBodyRow class="bg-teal-50">
                <TableBodyCell>
                  <Input
                    bind:value={editForm.name}
                    size="sm"
                    disabled={updatingId === container.id}
                  />
                </TableBodyCell>
                <TableBodyCell>
                  <Input
                    type="number"
                    min="1"
                    bind:value={editForm.capacity_ml}
                    size="sm"
                    disabled={updatingId === container.id}
                  />
                </TableBodyCell>
                <TableBodyCell>
                  <select
                    bind:value={editForm.material}
                    class="block w-full rounded-lg border border-gray-300 bg-white p-2 text-xs text-gray-900 focus:border-teal-500 focus:ring-teal-500"
                    disabled={updatingId === container.id}
                  >
                    {#each materialOptions as material}
                      <option value={material}>{material}</option>
                    {/each}
                  </select>
                </TableBodyCell>
                <TableBodyCell>
                  <Checkbox
                    bind:checked={editForm.in_use}
                    disabled={updatingId === container.id}
                  />
                </TableBodyCell>
                <TableBodyCell>
                  {#if editForm.in_use}
                    <select
                      bind:value={editForm.current_batch_id}
                      class="block w-full rounded-lg border border-gray-300 bg-white p-2 text-xs text-gray-900 focus:border-teal-500 focus:ring-teal-500"
                      disabled={updatingId === container.id}
                    >
                      <option value={null}>请选择批次</option>
                      {#each $batchesQuery.data ?? [] as batch}
                        <option value={batch.id}>{batch.id} - {batch.type}</option>
                      {/each}
                    </select>
                  {:else}
                    <span class="text-gray-400">—</span>
                  {/if}
                </TableBodyCell>
                <TableBodyCell>
                  <div class="flex gap-1 whitespace-nowrap">
                    <Button
                      size="xs"
                      color="teal"
                      disabled={updatingId === container.id}
                      onclick={saveEdit}
                    >
                      {updatingId === container.id ? '保存中…' : '保存'}
                    </Button>
                    <Button
                      size="xs"
                      color="gray"
                      outline
                      disabled={updatingId === container.id}
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
                  {container.name}
                </TableBodyCell>
                <TableBodyCell class="text-gray-600">
                  {container.capacity_ml} mL
                </TableBodyCell>
                <TableBodyCell>
                  <Badge color="teal">{container.material}</Badge>
                </TableBodyCell>
                <TableBodyCell>
                  {#if container.in_use}
                    <Badge color="green">使用中</Badge>
                  {:else}
                    <Badge color="gray">空闲</Badge>
                  {/if}
                </TableBodyCell>
                <TableBodyCell>
                  {#if container.in_use && container.current_batch_id}
                    <button
                      class="text-teal-600 hover:text-teal-800 hover:underline text-sm font-medium"
                      onclick={() => goToBatch(container.current_batch_id!)}
                    >
                      批次 #{container.current_batch_id} - {getBatchType(container.current_batch_id)}
                    </button>
                  {:else}
                    <span class="text-gray-400">—</span>
                  {/if}
                </TableBodyCell>
                <TableBodyCell>
                  <div class="flex gap-1 whitespace-nowrap">
                    <Button
                      size="xs"
                      color="teal"
                      outline
                      onclick={() => startEdit(container)}
                    >
                      编辑
                    </Button>
                    <Button
                      size="xs"
                      color="red"
                      outline
                      disabled={container.in_use || deletingId === container.id}
                      title={container.in_use ? '使用中的容器无法删除' : '删除容器'}
                      onclick={() => {
                        if (confirm(`确定删除容器「${container.name}」？`)) {
                          $deleteMutation_.mutate(container.id);
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
