import { message } from 'antd';

/**
 * API 错误响应接口
 */
interface APIErrorResponse {
  detail?: string;
  message?: string;
  error?: string;
}

/**
 * 统一的错误处理函数
 * @param error - 错误对象
 * @param defaultMessage - 默认错误提示
 */
export function handleError(error: any, defaultMessage: string = '操作失败'): void {
  console.error('Error:', error);

  if (error.response) {
    // 服务器返回错误响应
    const data = error.response.data as APIErrorResponse;
    const errorMessage = data?.detail || data?.message || data?.error || defaultMessage;
    
    // 根据状态码显示不同的错误信息
    switch (error.response.status) {
      case 400:
        message.error(`请求错误: ${errorMessage}`);
        break;
      case 401:
        message.error('未授权，请先登录');
        break;
      case 403:
        message.error('没有权限访问');
        break;
      case 404:
        message.error('请求的资源不存在');
        break;
      case 500:
        message.error('服务器内部错误，请稍后重试');
        break;
      case 503:
        message.error('服务暂时不可用，请稍后重试');
        break;
      default:
        message.error(errorMessage);
    }
  } else if (error.request) {
    // 请求已发出但没有响应
    message.error('网络错误，请检查后端服务是否启动');
  } else {
    // 其他错误
    message.error(error.message || defaultMessage);
  }
}

/**
 * 获取错误消息
 * @param error - 错误对象
 * @param defaultMessage - 默认错误提示
 * @returns 错误消息字符串
 */
export function getErrorMessage(error: any, defaultMessage: string = '操作失败'): string {
  if (error.response) {
    const data = error.response.data as APIErrorResponse;
    return data?.detail || data?.message || data?.error || defaultMessage;
  } else if (error.request) {
    return '网络错误，请检查后端服务是否启动';
  } else {
    return error.message || defaultMessage;
  }
}

/**
 * 判断是否为网络错误
 */
export function isNetworkError(error: any): boolean {
  return error.request && !error.response;
}

/**
 * 判断是否为服务器错误
 */
export function isServerError(error: any): boolean {
  return error.response && error.response.status >= 500;
}

/**
 * 判断是否为客户端错误
 */
export function isClientError(error: any): boolean {
  return error.response && error.response.status >= 400 && error.response.status < 500;
}
