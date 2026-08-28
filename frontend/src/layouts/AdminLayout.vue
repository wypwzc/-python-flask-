<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="admin-aside">
      <div class="admin-brand">
        <el-icon :size="22" color="#6ea8fe"><Monitor /></el-icon>
        <span>博客后台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#212529"
        text-color="#adb5bd"
        active-text-color="#fff"
        class="admin-menu"
      >
        <el-menu-item index="/admin">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/admin/posts">
          <el-icon><Document /></el-icon>
          <span>文章管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/posts/create">
          <el-icon><EditPen /></el-icon>
          <span>写文章</span>
        </el-menu-item>
        <el-menu-item index="/admin/categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/tags">
          <el-icon><PriceTag /></el-icon>
          <span>标签管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/comments">
          <el-icon><ChatDotRound /></el-icon>
          <span>评论管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/links">
          <el-icon><Link /></el-icon>
          <span>友链管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/profile">
          <el-icon><User /></el-icon>
          <span>个人设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶栏 -->
      <el-header class="admin-header">
        <h2 class="page-title">{{ route.meta.title || '后台管理' }}</h2>
        <div class="header-actions">
          <a :href="frontUrl" class="view-site">前台首页</a>
          <el-dropdown trigger="click" @command="onCommand">
            <span class="user-info">
              <el-avatar v-if="auth.user?.avatar" :src="auth.user.avatar" :size="28" />
              <el-avatar v-else :size="28" class="user-avatar-fallback">
                {{ (auth.user?.display_name || auth.user?.nickname || auth.user?.username || 'A')[0] }}
              </el-avatar>
              <span class="user-name">{{ auth.user?.display_name || auth.user?.nickname || auth.user?.username }}</span>
              <el-icon class="caret"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人设置
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Monitor, Odometer, Document, EditPen, Folder, PriceTag,
  ChatDotRound, Link, User, ArrowDown, SwitchButton,
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { frontUrl } from '../utils/urls'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// 写文章/编辑文章共用"写文章"菜单高亮
const activeMenu = computed(() => {
  const p = route.path
  if (p === '/admin/posts/create' || /^\/admin\/posts\/\d+\/edit$/.test(p)) return '/admin/posts/create'
  return p
})

async function onCommand(command) {
  if (command === 'profile') {
    router.push('/admin/profile')
  } else if (command === 'logout') {
    await auth.logout()
    ElMessage.success('已退出登录')
    router.push('/master')
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.admin-aside {
  background-color: #212529;
  display: flex;
  flex-direction: column;
}

.admin-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 1.1rem;
  font-weight: 700;
  padding: 18px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.admin-menu {
  border-right: none;
  flex: 1;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.12);
}

.admin-header {
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.page-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.view-site {
  font-size: 0.9rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}

.user-avatar-fallback {
  background: var(--link-color);
  color: #fff;
  font-size: 14px;
}

.user-name {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.caret {
  font-size: 12px;
  color: var(--text-muted);
}

.admin-main {
  background-color: var(--bg-secondary);
  padding: 20px;
}

@media (max-width: 768px) {
  .admin-aside {
    width: 64px !important;
  }

  .admin-brand span {
    display: none;
  }

  .admin-menu :deep(.el-menu-item span) {
    display: none;
  }

  .admin-menu :deep(.el-menu-item) {
    justify-content: center;
  }
}
</style>
