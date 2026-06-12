<script lang="ts">
  import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
  import { Router, Route } from 'svelte-routing';
  import BatchList from './pages/BatchList.svelte';
  import BatchDetail from './pages/BatchDetail.svelte';

  interface Props {
    url?: string;
  }

  let { url = '' }: Props = $props();

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 1,
      },
    },
  });
</script>

<QueryClientProvider client={queryClient}>
  <div class="min-h-screen bg-gray-50">
    <header class="border-b border-gray-200 bg-white shadow-sm">
      <div class="mx-auto flex max-w-5xl items-center px-4 py-4">
        <h1 class="text-xl font-bold text-gray-900">🧪 家庭发酵实验日志</h1>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-6">
      <Router {url}>
        <Route path="/" component={BatchList} />
        <Route path="/batches/:id" let:params>
          <BatchDetail id={params.id} />
        </Route>
      </Router>
    </main>
  </div>
</QueryClientProvider>
