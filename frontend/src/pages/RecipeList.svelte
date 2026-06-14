<script lang="ts">
  import {
    createQuery,
    createMutation,
    useQueryClient,
  } from '@tanstack/svelte-query';
  import { derived, writable } from 'svelte/store';
  import RouterLink from '../components/RouterLink.svelte';
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
  import { fetchRecipes, createRecipe, deleteRecipe } from '../lib/api';
  import type { RecipeForm, RecipeStepForm } from '../lib/types';

  const queryClient = useQueryClient();

  const fermentTypeFilter = writable<string>('');
  const searchKeyword = writable<string>('');

  let searchInput = $state('');
  let searchTimer: ReturnType<typeof setTimeout> | null = null;

  function onSearchInput(value: string) {
    searchInput = value;
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      searchKeyword.set(value.trim());
    }, 500);
  }

  const fermentTypeOptions = ['康普茶', '泡菜', '酸面包', '其他'];

  const recipesQueryOptions = derived(
    [fermentTypeFilter, searchKeyword],
    ([$fermentType, $search]) => ({
      queryKey: ['recipes', { ferment_type: $fermentType, search: $search }] as const,
      queryFn: () =>
        fetchRecipes({
          ferment_type: $fermentType || undefined,
          search: $search || undefined,
        }),
    }),
  );

  const recipesQuery = createQuery(recipesQueryOptions);

  let showForm = $state(false);
  let form = $state<RecipeForm>({
    name: '',
    ferment_type: '',
    ingredients: '',
    steps: [],
  });

  const createMutation_ = createMutation({
    mutationFn: createRecipe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'], exact: false });
      showForm = false;
      form = {
        name: '',
        ferment_type: '',
        ingredients: '',
        steps: [],
      };
    },
  });

  const deleteMutation_ = createMutation({
    mutationFn: deleteRecipe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'], exact: false });
    },
  });

  function handleSubmit(e: Event) {
    e.preventDefault();
    const sortedSteps = [...form.steps].sort(
      (a, b) => a.step_order - b.step_order,
    );
    $createMutation_.mutate({ ...form, steps: sortedSteps });
  }

  function addStep() {
    form.steps.push({
      step_order: form.steps.length + 1,
      description: '',
    });
  }

  function removeStep(index: number) {
    form.steps.splice(index, 1);
    form.steps.forEach((s, i) => {
      s.step_order = i + 1;
    });
  }
</script>

<div class="space-y-6">
  <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-6 sm:flex-wrap">
    <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:gap-2">
      <Label for="search-keyword" class="text-sm font-medium text-gray-700 whitespace-nowrap">关键字搜索</Label>
      <Input
        id="search-keyword"
        value={searchInput}
        oninput={(e) => onSearchInput((e.target as HTMLInputElement).value)}
        placeholder="按配方名称模糊搜索"
        class="sm:w-56"
      />
    </div>
    <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:gap-2">
      <Label for="filter-ferment-type" class="text-sm font-medium text-gray-700 whitespace-nowrap">发酵类型</Label>
      <select
        id="filter-ferment-type"
        bind:value={$fermentTypeFilter}
        class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 sm:w-40"
      >
        <option value="">全部类型</option>
        {#each fermentTypeOptions as type}
          <option value={type}>{type}</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="flex items-center justify-between">
    <h2 class="text-lg font-semibold text-gray-800">配方列表</h2>
    <Button color="green" onclick={() => (showForm = !showForm)}>
      {showForm ? '取消' : '+ 新建配方'}
    </Button>
  </div>

  {#if showForm}
    <form
      class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      onsubmit={handleSubmit}
    >
      <h3 class="mb-4 text-base font-medium text-gray-700">新建配方</h3>
      <div class="space-y-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label for="recipe-name">配方名称</Label>
            <Input
              id="recipe-name"
              bind:value={form.name}
              placeholder="如：经典康普茶"
              required
            />
          </div>
          <div>
            <Label for="ferment-type">适用发酵类型</Label>
            <select
              id="ferment-type"
              bind:value={form.ferment_type}
              class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="" disabled>请选择类型</option>
              {#each fermentTypeOptions as type}
                <option value={type}>{type}</option>
              {/each}
            </select>
          </div>
        </div>
        <div>
          <Label for="ingredients">原料说明</Label>
          <Textarea
            id="ingredients"
            bind:value={form.ingredients}
            rows={3}
            placeholder="列出所需原料及用量…"
            required
          />
        </div>
        <div>
          <div class="mb-2 flex items-center justify-between">
            <Label>操作步骤</Label>
            <Button type="button" size="xs" color="light" onclick={addStep}>
              + 添加步骤
            </Button>
          </div>
          {#if form.steps.length === 0}
            <p class="text-sm text-gray-400">暂无步骤，点击上方按钮添加</p>
          {:else}
            <ul class="space-y-3">
              {#each form.steps as step, index}
                <li
                  class="flex items-start gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3"
                >
                  <span
                    class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-green-100 text-sm font-medium text-green-700"
                  >
                    {step.step_order}
                  </span>
                  <div class="flex-1">
                    <Textarea
                      bind:value={step.description}
                      rows={2}
                      placeholder="描述这一步的操作…"
                      required
                    />
                  </div>
                  <Button
                    type="button"
                    size="xs"
                    color="red"
                    outline
                    onclick={() => removeStep(index)}
                  >
                    删除
                  </Button>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <Button type="submit" color="green" disabled={$createMutation_.isPending}>
          {$createMutation_.isPending ? '保存中…' : '保存'}
        </Button>
      </div>
      {#if $createMutation_.isError}
        <Alert color="red" class="mt-3">创建失败，请检查后端是否已启动。</Alert>
      {/if}
    </form>
  {/if}

  {#if $recipesQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $recipesQuery.isError}
    <Alert color="red">无法加载配方列表，请确认后端运行在 http://localhost:5000</Alert>
  {:else if ($recipesQuery.data ?? []).length === 0}
    <Alert color="yellow">暂无配方，点击「新建配方」开始记录。</Alert>
  {:else}
    <div class="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
      <Table hoverable>
        <TableHead>
          <TableHeadCell>配方名称</TableHeadCell>
          <TableHeadCell>适用发酵类型</TableHeadCell>
          <TableHeadCell>原料说明</TableHeadCell>
          <TableHeadCell>创建时间</TableHeadCell>
          <TableHeadCell>操作</TableHeadCell>
        </TableHead>
        <TableBody>
          {#each $recipesQuery.data ?? [] as recipe (recipe.id)}
            <TableBodyRow>
              <TableBodyCell>
                <RouterLink
                  to="/recipes/{recipe.id}"
                  class="font-medium text-green-600 hover:underline"
                >
                  {recipe.name}
                </RouterLink>
              </TableBodyCell>
              <TableBodyCell>
                <Badge color="green">{recipe.ferment_type}</Badge>
              </TableBodyCell>
              <TableBodyCell class="max-w-xs truncate text-gray-600">
                {recipe.ingredients}
              </TableBodyCell>
              <TableBodyCell class="text-gray-500">
                {new Date(recipe.created_at).toLocaleDateString('zh-CN')}
              </TableBodyCell>
              <TableBodyCell>
                <div class="flex gap-2">
                  <RouterLink to="/recipes/{recipe.id}">
                    <Button size="xs" color="light">详情</Button>
                  </RouterLink>
                  <Button
                    size="xs"
                    color="red"
                    outline
                    disabled={$deleteMutation_.isPending}
                    onclick={() => {
                      if (confirm(`确定删除「${recipe.name}」配方？`)) {
                        $deleteMutation_.mutate(recipe.id);
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
