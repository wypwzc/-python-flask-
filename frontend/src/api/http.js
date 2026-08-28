/**
 * Axios 实例 - 统一的 CSRF、错误处理
 * - 请求拦截器：从 cookie 读取 csrf_token 并携带 X-CSRFToken 头（CSRFProtect 校验）
 * - 响应拦截器：401 清理登录态并跳转登录页；其余错误弹出 ElMessage
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  return match ? decodeURIComponent(match[2]) : null
}

http.interceptors.request.use((config) => {
  const token = getCookie('csrf_token')
  if (token) {
    config.headers['X-CSRFToken'] = token
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    // 静默请求（如 PV 统计）：失败不提示
    if (error.config?.silent) {
      return Promise.reject(error)
    }
    const { response } = error
    if (response) {
      if (response.status === 401) {
        const url = error.config?.url || ''
        // 登录失败（用户名/密码错误）只提示，不跳转
        if (!url.includes('/auth/login')) {
          // 登录态失效：清空并按端口跳登录页（登录/注册页本身除外，避免循环）
          const isAdminPort = window.location.port === '5888'
          const loginPath = isAdminPort ? '/master' : '/login'
          const { useAuthStore } = await import('../stores/auth')
          useAuthStore().clear()
          const { default: router } = await import('../router')
          const current = router.currentRoute.value
          if (!['/master', '/login', '/register'].includes(current.path)) {
            router.replace({ path: loginPath, query: { redirect: current.fullPath } })
          }
        }
        ElMessage.error(response.data?.message || '请先登录')
      } else if (response.status === 400 && response.data?.message?.includes('CSRF')) {
        ElMessage.error('会话已过期，请刷新页面后重试')
      } else {
        const msg = response.data?.message || `请求失败 (${response.status})`
        ElMessage.error(msg)
      }
    } else {
      ElMessage.error('网络错误，请确认后端服务已启动')
    }
    return Promise.reject(error)
  },
)

export default http
