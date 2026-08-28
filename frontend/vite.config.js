import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vue 3 SPA 构建配置
// 开发模式：Vite dev server 代理 /api 到 Flask(5000)
// 生产模式：npm run build 产物 frontend/dist 由 Flask 托管
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: false,
      },
    },
  },
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        // 拆分第三方大包，利用浏览器缓存
        manualChunks: {
          'element-plus': ['element-plus', '@element-plus/icons-vue'],
          echarts: ['echarts'],
          'highlight.js': ['highlight.js'],
        },
      },
    },
  },
})
