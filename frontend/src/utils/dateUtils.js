import dayjs from 'dayjs'

/**
 * 格式化日期时间
 * @param {string|number|Date} input - 支持 ISO 字符串、时间戳、Date 对象
 * @param {string} format - dayjs 格式模板，默认 YYYY-MM-DD HH:mm:ss
 * @returns {string} 格式化后的字符串，若无效输入则返回空串
 */
export function formatDateTime(input, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!input && input !== 0) return ''
  const d = dayjs(input)
  return d.isValid() ? d.format(format) : ''
}

/**
 * 格式化日期（不含时间）
 * @param {string|number|Date} input
 * @param {string} format - 默认 YYYY-MM-DD
 * @returns {string}
 */
export function formatDate(input, format = 'YYYY-MM-DD') {
  if (!input && input !== 0) return ''
  const d = dayjs(input)
  return d.isValid() ? d.format(format) : ''
}