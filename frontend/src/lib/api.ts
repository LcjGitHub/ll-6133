import axios from 'axios';
import type { Batch, BatchDetail, BatchForm, Note } from './types';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' },
});

/** 获取全部批次 */
export async function fetchBatches(): Promise<Batch[]> {
  const { data } = await api.get<Batch[]>('/batches');
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
export async function updateBatch(id: number, payload: Partial<BatchForm>): Promise<Batch> {
  const { data } = await api.put<Batch>(`/batches/${id}`, payload);
  return data;
}

/** 删除批次 */
export async function deleteBatch(id: number): Promise<void> {
  await api.delete(`/batches/${id}`);
}

/** 追加观察笔记 */
export async function createNote(batchId: number, content: string): Promise<Note> {
  const { data } = await api.post<Note>(`/batches/${batchId}/notes`, { content });
  return data;
}

/** 删除笔记 */
export async function deleteNote(noteId: number): Promise<void> {
  await api.delete(`/notes/${noteId}`);
}
