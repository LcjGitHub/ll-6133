<script lang="ts">
  import {
    createQuery,
    createMutation,
    useQueryClient,
  } from '@tanstack/svelte-query';
  import RouterLink from '../components/RouterLink.svelte';
  import {
    Button,
    Input,
    Label,
    Textarea,
    Badge,
    Spinner,
    Alert,
    Card,
  } from 'flowbite-svelte';
  import { fetchRecipe, updateRecipe } from '../lib/api';
  import type { RecipeDetail, RecipeForm, RecipeStepForm } from '../lib/types';

  interface Props {
    id: string;
  }

  let { id }: Props = $props();

  const recipeId = $derived(parseInt(id, 10));
  const queryClient = useQueryClient();

  const recipeQuery = createQuery(() => ({
    queryKey: ['recipe', recipeId],
    queryFn: () => fetchRecipe(recipeId),
  }));

  const recipeData = $derived($recipeQuery.data as RecipeDetail | undefined);

  let editMode = $state(false);
  let form = $state<RecipeForm>({
    name: '',
    ferment_type: '',
    ingredients: '',
    steps: [],
  });

  const fermentTypeOptions = ['康普茶', '泡菜', '酸面包', '其他'];

  $effect(() => {
    const data = recipeData;
    if (data) {
      form = {
        name: data.name,
        ferment_type: data.ferment_type,
        ingredients: data.ingredients,
        steps: data.steps.map((s) => ({
          step_order: s.step_order,
          description: s.description,
        })),
      };
    }
  });

  const updateMutation_ = createMutation({
    mutationFn: (payload: Partial<RecipeForm>) =>
      updateRecipe(recipeId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipe', recipeId] });
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      editMode = false;
    },
  });

  function handleUpdate(e: Event) {
    e.preventDefault();
    const sortedSteps = [...form.steps].sort(
      (a, b) => a.step_order - b.step_order,
    );
    $updateMutation_.mutate({ ...form, steps: sortedSteps });
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

  function moveStepUp(index: number) {
    if (index === 0) return;
    const temp = form.steps[index];
    form.steps[index] = form.steps[index - 1];
    form.steps[index - 1] = temp;
    form.steps.forEach((s, i) => {
      s.step_order = i + 1;
    });
  }

  function moveStepDown(index: number) {
    if (index === form.steps.length - 1) return;
    const temp = form.steps[index];
    form.steps[index] = form.steps[index + 1];
    form.steps[index + 1] = temp;
    form.steps.forEach((s, i) => {
      s.step_order = i + 1;
    });
  }

  function formatTime(iso: string): string {
    return new Date(iso).toLocaleString('zh-CN');
  }
</script>

<div class="space-y-6">
  <RouterLink
    to="/recipes"
    class="inline-flex items-center text-sm text-green-600 hover:underline"
  >
    ← 返回列表
  </RouterLink>

  {#if Number.isNaN(recipeId)}
    <Alert color="red">无效的配方 ID</Alert>
  {:else if $recipeQuery.isPending}
    <div class="flex justify-center py-12">
      <Spinner size="8" />
    </div>
  {:else if $recipeQuery.isError}
    <Alert color="red">配方不存在或后端未启动</Alert>
  {:else if recipeData}
    {@const recipe = recipeData}

    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-800">{recipe.name}</h2>
      <div class="flex gap-2">
        <Badge color="green" large>{recipe.ferment_type}</Badge>
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
              <Label for="edit-name">配方名称</Label>
              <Input id="edit-name" bind:value={form.name} required />
            </div>
            <div>
              <Label for="edit-type">适用发酵类型</Label>
              <select
                id="edit-type"
                bind:value={form.ferment_type}
                class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500"
              >
                {#each fermentTypeOptions as type}
                  <option value={type}>{type}</option>
                {/each}
              </select>
            </div>
          </div>
          <div>
            <Label for="edit-ingredients">原料说明</Label>
            <Textarea
              id="edit-ingredients"
              bind:value={form.ingredients}
              rows={3}
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
                        required
                      />
                    </div>
                    <div class="flex flex-col gap-1">
                      <Button
                        type="button"
                        size="xs"
                        color="light"
                        disabled={index === 0}
                        onclick={() => moveStepUp(index)}
                      >
                        ↑
                      </Button>
                      <Button
                        type="button"
                        size="xs"
                        color="light"
                        disabled={index === form.steps.length - 1}
                        onclick={() => moveStepDown(index)}
                      >
                        ↓
                      </Button>
                      <Button
                        type="button"
                        size="xs"
                        color="red"
                        outline
                        onclick={() => removeStep(index)}
                      >
                        删除
                      </Button>
                    </div>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
          <Button type="submit" color="green" disabled={$updateMutation_.isPending}>
            {$updateMutation_.isPending ? '保存中…' : '保存修改'}
          </Button>
        </form>
      </Card>
    {:else}
      <Card class="max-w-none">
        <div class="space-y-4">
          <div>
            <dt class="text-sm text-gray-500">适用发酵类型</dt>
            <dd class="mt-1">
              <Badge color="green">{recipe.ferment_type}</Badge>
            </dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">原料说明</dt>
            <dd class="mt-1 whitespace-pre-wrap text-gray-700">
              {recipe.ingredients}
            </dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">创建时间</dt>
            <dd class="mt-1 font-medium text-gray-700">
              {formatTime(recipe.created_at)}
            </dd>
          </div>
        </div>
      </Card>

      <section class="space-y-4">
        <h3 class="text-base font-semibold text-gray-800">操作步骤</h3>

        {#if recipe.steps.length === 0}
          <Alert color="yellow">暂无操作步骤，点击「编辑」添加。</Alert>
        {:else}
          <ol class="space-y-4">
            {#each recipe.steps as step (step.id)}
              <li
                class="flex items-start gap-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
              >
                <span
                  class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-green-500 text-white font-bold"
                >
                  {step.step_order}
                </span>
                <div class="flex-1 pt-1">
                  <p class="whitespace-pre-wrap text-gray-700">
                    {step.description}
                  </p>
                </div>
              </li>
            {/each}
          </ol>
        {/if}
      </section>
    {/if}
  {/if}
</div>
