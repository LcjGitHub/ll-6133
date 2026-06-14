import axios from 'axios';
import type {
  Batch,
  BatchDetail,
  BatchForm,
  Note,
  Measurement,
  MeasurementForm,
  Recipe,
  RecipeDetail,
  RecipeForm,
  Reminder,
  ReminderForm,
  Statistics,
  ImportResult,
  Strain,
  StrainForm,
  Container,
  ContainerForm,
  SearchResult,
  BackupSummary,
  BackupRestoreResult,
  ChangeLogListResponse,
} from './types';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' },
});

/** 获取全部批次，可按状态、类型筛选，或按类型关键字模糊搜索 */
export async function fetchBatches(params?: {
  status?: string;
  type?: string;
  search?: string;
}): Promise<Batch[]> {
  const { data } = await api.get<Batch[]>('/batches', { params });
  return data;
}

/** 获取批次详情 */
export async function fetchBatch(id: number): Promise<BatchDetail> {
  const { data } = await api.get<BatchDetail>(`/batches/${id}`);
  return data;
}

/** 创建批次 */
export async function createBatch(payload: BatchForm): Promise<Batch> {
  const { data } = await api.post<Batch>('/batches', payload);
  return data;
}

/** 更新批次 */
export async function updateBatch(
  id: number,
  payload: Partial<BatchForm>,
): Promise<Batch> {
  const { data } = await api.put<Batch>(`/batches/${id}`, payload);
  return data;
}

/** 删除批次 */
export async function deleteBatch(id: number): Promise<void> {
  await api.delete(`/batches/${id}`);
}

/** 追加观察笔记 */
export async function createNote(
  batchId: number,
  content: string,
): Promise<Note> {
  const { data } = await api.post<Note>(`/batches/${batchId}/notes`, {
    content,
  });
  return data;
}

/** 更新笔记 */
export async function updateNote(
  noteId: number,
  content: string,
): Promise<Note> {
  const { data } = await api.put<Note>(`/notes/${noteId}`, { content });
  return data;
}

/** 删除笔记 */
export async function deleteNote(noteId: number): Promise<void> {
  await api.delete(`/notes/${noteId}`);
}

/** 按批次查询全部测量记录 */
export async function fetchMeasurements(batchId: number): Promise<Measurement[]> {
  const { data } = await api.get<Measurement[]>(`/batches/${batchId}/measurements`);
  return data;
}

/** 新增单条测量记录 */
export async function createMeasurement(
  batchId: number,
  payload: MeasurementForm,
): Promise<Measurement> {
  const { data } = await api.post<Measurement>(
    `/batches/${batchId}/measurements`,
    payload,
  );
  return data;
}

/** 更新指定批次下的测量记录 */
export async function updateMeasurement(
  batchId: number,
  measurementId: number,
  payload: Partial<MeasurementForm>,
): Promise<Measurement> {
  const { data } = await api.put<Measurement>(
    `/batches/${batchId}/measurements/${measurementId}`,
    payload,
  );
  return data;
}

/** 删除指定批次下的测量记录 */
export async function deleteMeasurement(
  batchId: number,
  measurementId: number,
): Promise<void> {
  await api.delete(`/batches/${batchId}/measurements/${measurementId}`);
}

/** 获取全部配方 */
export async function fetchRecipes(): Promise<Recipe[]> {
  const { data } = await api.get<Recipe[]>('/recipes');
  return data;
}

/** 获取配方详情 */
export async function fetchRecipe(id: number): Promise<RecipeDetail> {
  const { data } = await api.get<RecipeDetail>(`/recipes/${id}`);
  return data;
}

/** 创建配方 */
export async function createRecipe(payload: RecipeForm): Promise<RecipeDetail> {
  const { data } = await api.post<RecipeDetail>('/recipes', payload);
  return data;
}

/** 更新配方 */
export async function updateRecipe(
  id: number,
  payload: Partial<RecipeForm>,
): Promise<RecipeDetail> {
  const { data } = await api.put<RecipeDetail>(`/recipes/${id}`, payload);
  return data;
}

/** 删除配方 */
export async function deleteRecipe(id: number): Promise<void> {
  await api.delete(`/recipes/${id}`);
}

/** 获取统计数据概览 */
export async function fetchStatistics(): Promise<Statistics> {
  const { data } = await api.get<Statistics>('/statistics');
  return data;
}

/** 获取全部提醒 */
export async function fetchReminders(): Promise<Reminder[]> {
  const { data } = await api.get<Reminder[]>('/reminders');
  return data;
}

/** 创建提醒 */
export async function createReminder(payload: ReminderForm): Promise<Reminder> {
  const { data } = await api.post<Reminder>('/reminders', payload);
  return data;
}

/** 更新提醒 */
export async function updateReminder(
  id: number,
  payload: Partial<ReminderForm>,
): Promise<Reminder> {
  const { data } = await api.put<Reminder>(`/reminders/${id}`, payload);
  return data;
}

/** 切换提醒完成状态 */
export async function toggleReminderCompleted(id: number): Promise<Reminder> {
  const { data } = await api.patch<Reminder>(`/reminders/${id}/toggle`);
  return data;
}

/** 删除提醒 */
export async function deleteReminder(id: number): Promise<void> {
  await api.delete(`/reminders/${id}`);
}

/** 从任意错误响应中提取后端中文错误信息 */
export async function extractErrorDetail(error: any): Promise<string> {
  const response = error?.response;
  if (!response) return error?.message ?? '请求失败，请稍后重试';

  let data = response.data;

  if (data instanceof Blob) {
    try {
      const text = await data.text();
      data = JSON.parse(text);
    } catch {
      if (response.statusText) return `请求失败 (${response.status}: ${response.statusText})`;
      return error?.message ?? '请求失败，请稍后重试';
    }
  }

  if (typeof data?.detail === 'string') return data.detail;

  if (Array.isArray(data?.detail) && data.detail.length > 0) {
    const first = data.detail[0];
    if (typeof first === 'string') return first;
    if (first?.msg) return first.msg;
    if (first?.message) return first.message;
  }

  if (data?.message && typeof data.message === 'string') return data.message;
  if (data?.error && typeof data.error === 'string') return data.error;
  if (response.statusText) return `请求失败 (${response.status}: ${response.statusText})`;
  return error?.message ?? '请求失败，请稍后重试';
}

/** 导出全部批次及笔记 Excel 文件 */
export async function exportBatches(): Promise<void> {
  try {
    const response = await api.get('/batches/export', {
      responseType: 'blob',
    });
    const contentDisposition = response.headers['content-disposition'] ?? '';
    const match = contentDisposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : 'ferment_batches_export.xlsx';
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    const message = await extractErrorDetail(error);
    throw new Error(message);
  }
}

/** 从 Excel 文件导入批次及笔记 */
export async function importBatches(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const { data } = await api.post<ImportResult>(
      '/batches/import',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      },
    );
    return data;
  } catch (error: any) {
    const message = await extractErrorDetail(error);
    throw new Error(message);
  }
}

/** 获取全部菌种 */
export async function fetchStrains(): Promise<Strain[]> {
  const { data } = await api.get<Strain[]>('/strains');
  return data;
}

/** 创建菌种 */
export async function createStrain(payload: StrainForm): Promise<Strain> {
  const { data } = await api.post<Strain>('/strains', payload);
  return data;
}

/** 更新菌种 */
export async function updateStrain(
  id: number,
  payload: Partial<StrainForm>,
): Promise<Strain> {
  const { data } = await api.put<Strain>(`/strains/${id}`, payload);
  return data;
}

/** 删除菌种 */
export async function deleteStrain(id: number): Promise<void> {
  await api.delete(`/strains/${id}`);
}

/** 获取全部容器 */
export async function fetchContainers(): Promise<Container[]> {
  const { data } = await api.get<Container[]>('/containers');
  return data;
}

/** 创建容器 */
export async function createContainer(payload: ContainerForm): Promise<Container> {
  const { data } = await api.post<Container>('/containers', payload);
  return data;
}

/** 更新容器 */
export async function updateContainer(
  id: number,
  payload: Partial<ContainerForm>,
): Promise<Container> {
  const { data } = await api.put<Container>(`/containers/${id}`, payload);
  return data;
}

/** 删除容器 */
export async function deleteContainer(id: number): Promise<void> {
  await api.delete(`/containers/${id}`);
}

/** 全局搜索 */
export async function globalSearch(keyword: string): Promise<SearchResult> {
  const { data } = await api.get<SearchResult>('/search', {
    params: { q: keyword },
  });
  return data;
}

/** 下载全部数据备份文件 */
export async function downloadBackup(): Promise<void> {
  try {
    const response = await api.get('/backup', {
      responseType: 'blob',
    });
    const contentDisposition = response.headers['content-disposition'] ?? '';
    const match = contentDisposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : 'ferment_backup.json';
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    const message = await extractErrorDetail(error);
    throw new Error(message);
  }
}

/** 预览备份文件内容摘要（不写入数据库） */
export async function previewBackup(file: File): Promise<BackupSummary> {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const { data } = await api.post<BackupSummary>(
      '/backup/preview',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      },
    );
    return data;
  } catch (error: any) {
    const message = await extractErrorDetail(error);
    throw new Error(message);
  }
}

/** 从备份文件恢复数据 */
export async function restoreBackup(
  file: File,
  confirmOverwrite: boolean = false,
): Promise<BackupRestoreResult> {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const { data } = await api.post<BackupRestoreResult>(
      `/backup/restore?confirm_overwrite=${confirmOverwrite}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      },
    );
    return data;
  } catch (error: any) {
    const message = await extractErrorDetail(error);
    throw new Error(message);
  }
}

/** 分页查询变更记录 */
export async function fetchChangeLogs(params?: {
  page?: number;
  page_size?: number;
}): Promise<ChangeLogListResponse> {
  const { data } = await api.get<ChangeLogListResponse>('/change-logs', { params });
  return data;
}
