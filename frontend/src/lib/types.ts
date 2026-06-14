/** 批次列表项 */
export interface Batch {
  id: number;
  type: string;
  start_date: string;
  temperature: number;
  status: string;
  ph: number | null;
  created_at: string;
  fermentation_days: number;
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

/** 提醒待办 */
export interface Reminder {
  id: number;
  batch_id: number;
  title: string;
  reminder_date: string;
  completed: boolean;
  created_at: string;
}

/** 创建/更新提醒表单 */
export interface ReminderForm {
  batch_id: number;
  title: string;
  reminder_date: string;
}

/** 数据导入结果 */
export interface ImportResult {
  inserted_batches: number;
  skipped_batches: number;
  inserted_notes: number;
  skipped_notes: number;
  total_batches_in_file: number;
  total_notes_in_file: number;
}

/** 发酵菌种 */
export interface Strain {
  id: number;
  name: string;
  ferment_type: string;
  activation_date: string;
  storage_location: string;
  notes: string | null;
  created_at: string;
}

/** 创建/更新菌种表单 */
export interface StrainForm {
  name: string;
  ferment_type: string;
  activation_date: string;
  storage_location: string;
  notes: string | null;
}

/** 批次搜索结果项 */
export interface SearchBatchItem {
  id: number;
  type: string;
  start_date: string;
  status: string;
  fermentation_days: number;
}

/** 配方搜索结果项 */
export interface SearchRecipeItem {
  id: number;
  name: string;
  ferment_type: string;
}

/** 笔记搜索结果项 */
export interface SearchNoteItem {
  id: number;
  batch_id: number;
  content: string;
  created_at: string;
}

/** 全局搜索结果 */
export interface SearchResult {
  batches: SearchBatchItem[];
  recipes: SearchRecipeItem[];
  notes: SearchNoteItem[];
  batch_count: number;
  recipe_count: number;
  note_count: number;
  total_count: number;
}

/** 备份文件摘要信息 */
export interface BackupSummary {
  batches: number;
  notes: number;
  measurements: number;
  recipes: number;
  recipe_steps: number;
  reminders: number;
  strains: number;
}

/** 数据恢复结果 */
export interface BackupRestoreResult {
  success: boolean;
  message: string;
  summary: BackupSummary;
}
