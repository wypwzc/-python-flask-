/**
 * 文本工具（移植自 Python helpers.py 的逻辑）
 */

/** 去除 Markdown 标记和 HTML 标签后统计字数 */
export function wordCount(text) {
  if (!text) return 0
  let plain = text.replace(/[#*>`\-\d\.\[\]\(\)_!|{}]/g, '')
  plain = plain.replace(/<[^>]+>/g, '')
  return plain.trim().length
}

/** 估算阅读时长（分钟，至少 1 分钟） */
export function readingTime(text, wpm = 300) {
  const count = wordCount(text)
  return Math.max(1, Math.round(count / wpm))
}

/** 截断文本（去除 HTML 标签后按长度截断） */
export function truncate(text, length = 150, suffix = '...') {
  if (!text) return ''
  const plain = String(text).replace(/<[^>]+>/g, '')
  if (plain.length <= length) return plain
  return plain.slice(0, length).replace(/\s+\S*$/, '') + suffix
}
