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

/** 温湿度测量记录 */
export interface Measurement {
  id: number;
  batch_id: number;
  recorded_at: string;
  temperature: number;
  ph: number | null;
  created_at: string;
}

/** 创建测量记录表单 */
export interface MeasurementForm {
  recorded_at: string;
  temperature: number;
  ph: number | null;
}

/** 批次详情（含笔记和测量记录） */
export interface BatchDetail extends Batch {
  notes: Note[];
  measurements: Measurement[];
}

/** 创建/更新批次表单 */
export interface BatchForm {
  type: string;
  start_date: string;
  temperature: number;
  status: string;
  ph: number | null;
}

/** 配方步骤 */
export interface RecipeStep {
  id: number;
  recipe_id: number;
  step_order: number;
  description: string;
  created_at: string;
}

/** 配方列表项 */
export interface Recipe {
  id: number;
  name: string;
  ferment_type: string;
  ingredients: string;
  created_at: string;
}

/** 配方详情（含步骤） */
export interface RecipeDetail extends Recipe {
  steps: RecipeStep[];
}

/** 创建/更新配方步骤 */
export interface RecipeStepForm {
  step_order: number;
  description: string;
}

/** 创建/更新配方表单 */
export interface RecipeForm {
  name: string;
  ferment_type: string;
  ingredients: string;
  steps: RecipeStepForm[];
}

/** 统计数据概览 */
export interface Statistics {
  status_counts: Record<string, number>;
  type_counts: Record<string, number>;
  recent_notes_count: number;
}
