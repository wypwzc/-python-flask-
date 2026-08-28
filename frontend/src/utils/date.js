/**
 * 日期时间工具（移植自 Python helpers.py 的逻辑）
 * 服务端统一返回 'YYYY-MM-DDTHH:mm:ss' 格式，JS Date 可直接解析（按本地时区）
 */

/** 格式化日期时间 */
export function formatDateTime(dt, format = 'YYYY-MM-DD HH:mm') {
  if (!dt) return ''
  const d = new Date(dt)
  if (isNaN(d.getTime())) return String(dt)
  const pad = (n) => String(n).padStart(2, '0')
  const map = {
    YYYY: d.getFullYear(),
    MM: pad(d.getMonth() + 1),
    DD: pad(d.getDate()),
    HH: pad(d.getHours()),
    mm: pad(d.getMinutes()),
    ss: pad(d.getSeconds()),
  }
  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, (k) => map[k])
}

/** 相对时间：刚刚/x 分钟前/x 小时前/x 天前/x 个月前/x 年前 */
export function timeAgo(dt) {
  if (!dt) return ''
  const time = new Date(dt).getTime()
  if (isNaN(time)) return String(dt)
  const diff = Date.now() - time
  const seconds = Math.floor(diff / 1000)

  if (seconds < 60) return '刚刚'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days} 天前`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months} 个月前`
  const years = Math.floor(months / 12)
  return `${years} 年前`
}
