/**
 * 主题 store - 日间/夜间切换
 * localStorage 保存用户选择；未选择时跟随系统偏好
 * 同时设置 html.dark class（Element Plus 暗色）和 data-theme 属性（自定义 CSS 变量）
 */
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: 'light',
  }),
  getters: {
    isDark: (state) => state.theme === 'dark',
  },
  actions: {
    init() {
      const saved = localStorage.getItem('blog-theme')
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      this.theme = saved || (systemDark ? 'dark' : 'light')
      this.apply()

      // 跟随系统（用户未手动选择时）
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('blog-theme')) {
          this.theme = e.matches ? 'dark' : 'light'
          this.apply()
        }
      })
    },
    toggle() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      this.apply()
    },
    set(theme) {
      this.theme = theme
      this.apply()
    },
    apply() {
      const isDark = this.theme === 'dark'
      document.documentElement.classList.toggle('dark', isDark)
      document.documentElement.setAttribute('data-theme', this.theme)
      localStorage.setItem('blog-theme', this.theme)
    },
  },
})
