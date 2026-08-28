<template>
  <div class="front-layout">
    <!-- 顶部导航 -->
    <header class="front-nav">
      <div class="nav-inner">
        <router-link to="/" class="brand">
          {{ sidebar.blog_admin?.display_name || sidebar.blog_admin?.nickname || '我的博客' }}
        </router-link>
        <nav class="nav-links">
          <router-link to="/" exact-active-class="active">首页</router-link>
          <router-link to="/archive" active-class="active">归档</router-link>
          <router-link to="/message" active-class="active">留言板</router-link>
          <router-link to="/links" active-class="active">友链</router-link>
          <router-link to="/about" active-class="active">关于</router-link>
        </nav>
        <div class="nav-actions">
          <el-input
            v-model="keyword"
            class="search-input"
            placeholder="搜索文章…"
            clearable
            size="small"
            @keyup.enter="doSearch"
            @clear="doSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-tooltip :content="theme.isDark ? '切换到日间模式' : '切换到夜间模式'">
            <el-button circle text size="small" class="theme-btn" @click="theme.toggle()">
              <el-icon :size="18">
                <Sunny v-if="!theme.isDark" />
                <Moon v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
          <template v-if="auth.isAuthenticated">
            <el-dropdown trigger="click" class="user-dropdown" @command="onUserCommand">
              <span class="user-chip">
                <el-avatar v-if="auth.user?.avatar" :src="auth.user.avatar" :size="26" />
                <el-avatar v-else :size="26" class="user-avatar-fallback">{{ userInitial }}</el-avatar>
                <span class="user-name">{{ auth.user?.display_name || auth.user?.nickname || auth.user?.username }}</span>
                <el-icon :size="12" class="caret"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="auth.isAdmin" command="admin">
                    <el-icon><Monitor /></el-icon>后台管理
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-auth-link">登录</router-link>
            <router-link to="/register" class="nav-auth-link nav-register">注册</router-link>
          </template>
        </div>
      </div>
    </header>

    <!-- 主体 -->
    <main class="front-main">
      <el-row :gutter="20">
        <el-col :xs="24" :md="showSidebar ? 17 : 24">
          <router-view />
        </el-col>
        <el-col v-if="showSidebar" :xs="24" :md="7">
          <Sidebar
            :categories="sidebar.categories"
            :recent-posts="sidebar.recent_posts"
            :recent-comments="sidebar.recent_comments"
            :total-stats="sidebar.total_stats"
          />
        </el-col>
      </el-row>
    </main>

    <!-- 页脚 -->
    <footer class="front-footer">
      <div>
        © {{ year }}
        <router-link to="/">{{ sidebar.blog_admin?.display_name || sidebar.blog_admin?.nickname || '博客' }}</router-link>
        <span class="footer-stats">
          本站已运行 · 总访问 {{ sidebar.total_stats?.total_pv || 0 }} PV /
          {{ sidebar.total_stats?.total_uv || 0 }} UV
        </span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Sunny, Moon, ArrowDown, Monitor, SwitchButton } from '@element-plus/icons-vue'
import { getSidebar } from '../api/front'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import Sidebar from '../components/Sidebar.vue'
import { adminUrl } from '../utils/urls'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const theme = useThemeStore()

const keyword = ref('')
const sidebar = ref({
  categories: [],
  recent_posts: [],
  recent_comments: [],
  total_stats: { total_pv: 0, total_uv: 0 },
  blog_admin: null,
})

const year = new Date().getFullYear()
// 文章详情页自带 TOC 布局，隐藏共享侧边栏
const showSidebar = computed(() => route.name !== 'post-detail')

const userInitial = computed(() => {
  const name = auth.user?.display_name || auth.user?.nickname || auth.user?.username || 'U'
  return name[0]
})

async function onUserCommand(command) {
  if (command === 'admin') {
    // 后台只在 5888 端口提供
    window.location.href = adminUrl
  } else if (command === 'logout') {
    await auth.logout()
    ElMessage.success('已退出登录')
    router.replace('/')
  }
}

function doSearch() {
  const q = keyword.value.trim()
  router.push({ name: 'search', query: q ? { q } : {} })
}

onMounted(async () => {
  try {
    const { data } = await getSidebar()
    sidebar.value = data
  } catch {
    // 侧边栏加载失败不阻塞页面
  }
})
</script>

<style scoped>
.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 16px;
  height: 56px;
}

.brand {
  color: #fff;
  font-size: 1.25rem;
  font-weight: 700;
  white-space: nowrap;
}

.brand:hover {
  color: #fff;
}

.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-links a {
  color: #adb5bd;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.95rem;
}

.nav-links a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.nav-links a.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  width: 200px;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  box-shadow: none;
  border-radius: 16px;
}

.search-input :deep(.el-input__inner) {
  color: #fff;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: #adb5bd;
}

.theme-btn {
  color: #adb5bd;
}

.theme-btn:hover {
  color: #fff;
}

.user-dropdown {
  outline: none;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 16px;
}

.user-chip:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar-fallback {
  background: #6ea8fe;
  color: #fff;
  font-size: 13px;
}

.user-name {
  color: #adb5bd;
  font-size: 0.9rem;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.caret {
  color: #adb5bd;
}

.nav-auth-link {
  color: #adb5bd;
  font-size: 0.9rem;
  white-space: nowrap;
  padding: 4px 8px;
  border-radius: 6px;
}

.nav-auth-link:hover {
  color: #fff;
}

.nav-register {
  color: #6ea8fe;
  border: 1px solid rgba(110, 168, 254, 0.5);
  border-radius: 14px;
}

.nav-register:hover {
  color: #8bb9fe;
  border-color: #8bb9fe;
}

.footer-stats {
  margin-left: 12px;
  font-size: 0.8rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .nav-inner {
    height: auto;
    flex-wrap: wrap;
    padding: 8px 12px;
    gap: 8px;
  }

  .search-input {
    width: 100%;
    order: 3;
  }

  .nav-links {
    overflow-x: auto;
    white-space: nowrap;
  }
}
</style>
