/** 批次列表项 */
export interface Batch {
  id: number;
  type: string;
  start_date: string;
  temperature: number;
  status: string;
  ph: number | null;
  created_at: string;
}

/** 观察笔记 */
export interface Note {
  id: number;
  batch_id: number;
  content: string;
  created_at: string;
}

/** 批次详情（含笔记） */
export interface BatchDetail extends Batch {
  notes: Note[];
}

/** 创建/更新批次表单 */
export interface BatchForm {
  type: string;
  start_date: string;
  temperature: number;
  status: string;
  ph: number | null;
}
