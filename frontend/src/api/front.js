/** 前台 API */
import http from './http'

// 文章
export const getPosts = (params) => http.get('/posts', { params })
export const getPost = (slug) => http.get(`/posts/${slug}`)
export const likePost = (slug) => http.post(`/posts/${slug}/like`)
export const submitComment = (slug, data) => http.post(`/posts/${slug}/comment`, data)

// 评论与留言
export const getComments = (params) => http.get('/comments', { params })
export const getMessages = (params) => http.get('/messages', { params })
export const submitMessage = (data) => http.post('/messages', data)

// 分类/标签/友链/归档/侧边栏
export const getCategories = () => http.get('/categories')
export const getTags = () => http.get('/tags')
export const getLinks = () => http.get('/links')
export const getArchive = () => http.get('/archive')
export const getSidebar = () => http.get('/sidebar')

// PV 统计（fire-and-forget，失败静默）
export const recordPv = () => http.post('/pv', null, { silent: true }).catch(() => {})
