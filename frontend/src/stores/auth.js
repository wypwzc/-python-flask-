/**
 * 登录态 store
 * 启动时调用 getSession() 通过 /api/auth/me 恢复登录状态
 */
import { defineStore } from 'pinia'
import * as authApi from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loaded: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
    isAdmin: (state) => !!state.user?.is_admin,
  },
  actions: {
    async getSession() {
      try {
        const { data } = await authApi.getMe()
        this.user = data.authenticated ? data.user : null
      } catch {
        this.user = null
      }
      this.loaded = true
    },
    async login(form) {
      const { data } = await authApi.login(form)
      this.user = data.user
      return data
    },
    async logout() {
      try {
        await authApi.logout()
      } catch {
        // 忽略登出失败
      }
      this.user = null
    },
    clear() {
      this.user = null
    },
  },
})
