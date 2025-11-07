/**
 * 时间处理工具函数
 */

/**
 * 格式化日期时间
 */
export function formatDateTime(date: string | Date, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 格式化为相对时间（多久之前）
 */
export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);
  
  if (seconds < 60) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  if (weeks < 4) return `${weeks}周前`;
  if (months < 12) return `${months}个月前`;
  return `${years}年前`;
}

/**
 * 获取日期范围（本周、本月等）
 */
export function getDateRange(period: 'today' | 'week' | 'month' | 'year'): { start: Date; end: Date } {
  const now = new Date();
  const end = new Date(now);
  let start = new Date(now);
  
  switch (period) {
    case 'today':
      start.setHours(0, 0, 0, 0);
      end.setHours(23, 59, 59, 999);
      break;
    case 'week':
      const dayOfWeek = now.getDay();
      start.setDate(now.getDate() - dayOfWeek);
      start.setHours(0, 0, 0, 0);
      break;
    case 'month':
      start.setDate(1);
      start.setHours(0, 0, 0, 0);
      break;
    case 'year':
      start.setMonth(0, 1);
      start.setHours(0, 0, 0, 0);
      break;
  }
  
  return { start, end };
}

/**
 * 判断是否是今天
 */
export function isToday(date: string | Date): boolean {
  const d = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  
  return (
    d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
  );
}

/**
 * 判断是否是本周
 */
export function isThisWeek(date: string | Date): boolean {
  const d = typeof date === 'string' ? new Date(date) : date;
  const { start, end } = getDateRange('week');
  
  return d >= start && d <= end;
}

/**
 * 格式化时间段（用于周报等）
 */
export function formatDateRangeText(start: Date, end: Date): string {
  const startStr = formatDateTime(start, 'YYYY-MM-DD');
  const endStr = formatDateTime(end, 'YYYY-MM-DD');
  
  return `${startStr} 至 ${endStr}`;
}

/**
 * 获取上周的日期范围
 */
export function getLastWeekRange(): { start: string; end: string } {
  const now = new Date();
  const dayOfWeek = now.getDay();
  
  const lastWeekEnd = new Date(now);
  lastWeekEnd.setDate(now.getDate() - dayOfWeek - 1);
  lastWeekEnd.setHours(23, 59, 59, 999);
  
  const lastWeekStart = new Date(lastWeekEnd);
  lastWeekStart.setDate(lastWeekEnd.getDate() - 6);
  lastWeekStart.setHours(0, 0, 0, 0);
  
  return {
    start: lastWeekStart.toISOString(),
    end: lastWeekEnd.toISOString(),
  };
}

/**
 * 解析ISO日期字符串
 */
export function parseISODate(isoString: string): Date {
  return new Date(isoString);
}
