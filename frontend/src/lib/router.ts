import { get, writable } from 'svelte/store';

/** 当前路径 */
export const pathname = writable<string>(
  typeof window !== 'undefined' ? window.location.pathname : '/',
);

/**
 * 初始化浏览器路由监听。
 * @returns 清理函数
 */
export function initRouter(): () => void {
  const onPopState = () => {
    pathname.set(window.location.pathname);
  };

  window.addEventListener('popstate', onPopState);
  return () => window.removeEventListener('popstate', onPopState);
}

/**
 * 编程式导航。
 * @param to - 目标路径
 */
export function navigate(to: string): void {
  if (get(pathname) === to) return;
  window.history.pushState({}, '', to);
  pathname.set(to);
}

/**
 * 从路径解析批次编号。
 * @param path - 当前路径
 */
export function parseBatchId(path: string): string | null {
  const match = path.match(/^\/batches\/(\d+)$/);
  return match ? match[1] : null;
}

/**
 * 从路径解析配方编号。
 * @param path - 当前路径
 */
export function parseRecipeId(path: string): string | null {
  const match = path.match(/^\/recipes\/(\d+)$/);
  return match ? match[1] : null;
}

/**
 * 判断是否为配方列表页。
 * @param path - 当前路径
 */
export function isRecipeList(path: string): boolean {
  return path === '/recipes';
}

/**
 * 判断是否为概览页。
 * @param path - 当前路径
 */
export function isOverview(path: string): boolean {
  return path === '/overview';
}

/**
 * 判断是否为提醒列表页。
 * @param path - 当前路径
 */
export function isReminderList(path: string): boolean {
  return path === '/reminders';
}
