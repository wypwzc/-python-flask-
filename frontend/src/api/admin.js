/** 后台管理 API */
import http from './http'

// 仪表盘
export const getDashboardStats = () => http.get('/admin/dashboard/stats')

// 文章
export const getAdminPosts = (params) => http.get('/admin/posts', { params })
export const getAdminPost = (id) => http.get(`/admin/posts/${id}`)
export const createAdminPost = (data) => http.post('/admin/posts', data)
export const updateAdminPost = (id, data) => http.put(`/admin/posts/${id}`, data)
export const deleteAdminPost = (id) => http.delete(`/admin/posts/${id}`)
export const batchDeletePosts = (ids) => http.post('/admin/posts/batch-delete', { ids })
export const toggleTop = (id) => http.post(`/admin/posts/${id}/toggle-top`)
export const togglePublish = (id) => http.post(`/admin/posts/${id}/toggle-publish`)

// 上传
export const uploadCover = (file) => {
  const form = new FormData()
  form.append('file', file)
  return http.post('/admin/upload/cover', form)
}
export const uploadAvatar = (file) => {
  const form = new FormData()
  form.append('file', file)
  return http.post('/admin/upload/avatar', form)
}

// 分类
export const getAdminCategories = () => http.get('/admin/categories')
export const createCategory = (data) => http.post('/admin/categories', data)
export const updateCategory = (id, data) => http.put(`/admin/categories/${id}`, data)
export const deleteCategory = (id) => http.delete(`/admin/categories/${id}`)

// 标签
export const getAdminTags = () => http.get('/admin/tags')
export const createTag = (data) => http.post('/admin/tags', data)
export const updateTag = (id, data) => http.put(`/admin/tags/${id}`, data)
export const deleteTag = (id) => http.delete(`/admin/tags/${id}`)

// 评论
export const getAdminComments = (params) => http.get('/admin/comments', { params })
export const approveComment = (id) => http.post(`/admin/comments/${id}/approve`)
export const deleteComment = (id) => http.delete(`/admin/comments/${id}`)
export const replyComment = (id, content) => http.post(`/admin/comments/${id}/reply`, { content })

// 友链
export const getAdminLinks = () => http.get('/admin/links')
export const createLink = (data) => http.post('/admin/links', data)
export const updateLink = (id, data) => http.put(`/admin/links/${id}`, data)
export const deleteLink = (id) => http.delete(`/admin/links/${id}`)

// 个人资料
export const getProfile = () => http.get('/admin/profile')
export const updateProfile = (data) => http.put('/admin/profile', data)
export const changePassword = (data) => http.post('/admin/profile/password', data)
