/**
 * 格式化工具函数
 */

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

/**
 * 格式化数字（添加千分位）
 */
export function formatNumber(num: number): string {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * 高亮关键词
 */
export function highlightKeyword(text: string, keyword: string): string {
  if (!keyword) return text;
  
  const regex = new RegExp(`(${keyword})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}

/**
 * 格式化百分比
 */
export function formatPercentage(value: number, total: number, decimals: number = 2): string {
  if (total === 0) return '0%';
  return `${((value / total) * 100).toFixed(decimals)}%`;
}

/**
 * 生成随机颜色
 */
export function generateRandomColor(): string {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

/**
 * 根据字符串生成固定颜色（用于标签等）
 */
export function stringToColor(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
  return '#' + '00000'.substring(0, 6 - c.length) + c;
}

/**
 * 格式化情绪为emoji
 */
export function formatEmotionToEmoji(emotion?: string): string {
  if (!emotion) return '😐';
  
  const emotionMap: Record<string, string> = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    excited: '🤩',
    anxious: '😰',
    calm: '😌',
    neutral: '😐',
    confused: '😕',
    love: '❤️',
    fear: '😨',
  };
  
  return emotionMap[emotion.toLowerCase()] || '😐';
}
