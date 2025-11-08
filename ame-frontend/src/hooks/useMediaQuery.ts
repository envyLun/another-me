import { useState, useEffect } from 'react';

/**
 * 响应式媒体查询 Hook
 * 
 * @param query - CSS 媒体查询字符串
 * @returns 是否匹配当前媒体查询
 * 
 * @example
 * const isMobile = useMediaQuery('(max-width: 768px)');
 * const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
 * const isDesktop = useMediaQuery('(min-width: 1025px)');
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState<boolean>(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    
    // 初始化状态
    setMatches(media.matches);

    // 监听变化
    const listener = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    // 兼容不同浏览器
    if (media.addEventListener) {
      media.addEventListener('change', listener);
    } else {
      // @ts-ignore - 兼容旧版浏览器
      media.addListener(listener);
    }

    return () => {
      if (media.removeEventListener) {
        media.removeEventListener('change', listener);
      } else {
        // @ts-ignore - 兼容旧版浏览器
        media.removeListener(listener);
      }
    };
  }, [query]);

  return matches;
}

/**
 * 响应式断点 Hook
 * 返回当前设备类型
 */
export function useResponsive() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
  const isDesktop = useMediaQuery('(min-width: 1025px)');

  return {
    isMobile,
    isTablet,
    isDesktop,
    device: isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop',
  };
}
