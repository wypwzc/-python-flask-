/**
 * 前后台跨区跳转地址
 * - 生产（域名部署）：前台 = https://域名（443），后台 = https://域名:5888
 * - 本地开发：前台 = http://localhost:5000，后台 = http://localhost:5888
 * 跟随当前页面的协议与主机名动态生成，本地/服务器通用。
 */
const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname)
const protocol = window.location.protocol
const hostname = window.location.hostname

/** 博客前台地址 */
export const frontUrl = isLocal ? `${protocol}//${hostname}:5000` : `${protocol}//${hostname}`
/** 博客后台地址（固定 5888 端口） */
export const adminUrl = `${protocol}//${hostname}:5888`
