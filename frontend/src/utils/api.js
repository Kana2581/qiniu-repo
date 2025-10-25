const BASE_URL = import.meta.env.VITE_API_BASE_URL;

/**
 * 基于原生 fetch 的统一请求封装
 * @param {string} path - 请求路径
 * @param {object} options - fetch 配置项
 */
export function apiFetch(path, options = {}) {
  const url = `${BASE_URL}${path.startsWith("/") ? path : "/" + path}`;
  return fetch(url, options); // 直接返回 Response
}