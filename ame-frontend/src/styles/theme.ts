/**
 * 全局样式常量
 * 统一管理应用中的颜色、间距、字体等样式
 */

export const colors = {
  primary: '#1890ff',
  success: '#52c41a',
  warning: '#faad14',
  error: '#ff4d4f',
  info: '#1890ff',
  
  text: {
    primary: 'rgba(0, 0, 0, 0.85)',
    secondary: 'rgba(0, 0, 0, 0.65)',
    disabled: 'rgba(0, 0, 0, 0.25)',
    placeholder: '#999',
  },
  
  background: {
    default: '#fff',
    light: '#f5f5f5',
    dark: '#001529',
  },
  
  border: {
    default: '#d9d9d9',
    light: '#f0f0f0',
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 16,
};

export const fontSize = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  xxl: 24,
};

export const shadows = {
  sm: '0 2px 8px rgba(0, 0, 0, 0.08)',
  md: '0 4px 12px rgba(0, 0, 0, 0.12)',
  lg: '0 8px 24px rgba(0, 0, 0, 0.16)',
};

/**
 * 常用布局样式
 */
export const layouts = {
  flexCenter: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  flexBetween: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  
  flexColumn: {
    display: 'flex',
    flexDirection: 'column' as const,
  },
  
  fullHeight: {
    height: '100%',
  },
  
  fullWidth: {
    width: '100%',
  },
};

/**
 * 卡片样式
 */
export const cardStyles = {
  default: {
    borderRadius: borderRadius.md,
    boxShadow: shadows.sm,
  },
  
  hover: {
    borderRadius: borderRadius.md,
    boxShadow: shadows.sm,
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    ':hover': {
      boxShadow: shadows.md,
      transform: 'translateY(-2px)',
    },
  },
};

/**
 * 文本省略样式
 */
export const textEllipsis = {
  singleLine: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap' as const,
  },
  
  multiLine: (lines: number) => ({
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: lines,
    WebkitBoxOrient: 'vertical' as const,
  }),
};

/**
 * 响应式断点
 */
export const breakpoints = {
  xs: 480,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1600,
};
