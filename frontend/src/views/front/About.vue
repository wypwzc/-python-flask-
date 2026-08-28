<template>
  <div class="about-page">
    <div class="about-card">
      <div v-if="loading">
        <el-skeleton :rows="5" animated />
      </div>
      <template v-else-if="admin">
        <div class="about-header">
          <el-avatar v-if="admin.avatar" :src="admin.avatar" :size="120" class="about-avatar" />
          <el-avatar v-else :size="120" class="about-avatar fallback">
            {{ (admin.display_name || admin.nickname || admin.username || '博')[0] }}
          </el-avatar>
          <h2 class="about-name">{{ admin.display_name || admin.nickname }}</h2>
          <p class="about-email">{{ admin.email }}</p>
        </div>

        <div v-if="admin.bio" class="about-section">
          <h4>关于我</h4>
          <p class="about-bio">{{ admin.bio }}</p>
        </div>

        <div class="about-section">
          <h4>联系我</h4>
          <p>邮箱：<a :href="`mailto:${admin.email}`">{{ admin.email }}</a></p>
        </div>

        <el-divider />

        <div class="about-stats">
          <div class="stat-item">
            <div class="stat-num">{{ totalPosts }}</div>
            <div class="stat-label">文章</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{{ categories.length }}</div>
            <div class="stat-label">分类</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{{ tags.length }}</div>
            <div class="stat-label">标签</div>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无介绍信息" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getCategories, getPosts, getSidebar, getTags } from '../../api/front'

const loading = ref(true)
const admin = ref(null)
const categories = ref([])
const tags = ref([])
const totalPosts = ref(0)

onMounted(async () => {
  try {
    const [sidebar, cats, tgs, posts] = await Promise.all([
      getSidebar(), getCategories(), getTags(), getPosts({ per_page: 1 }),
    ])
    admin.value = sidebar.data.blog_admin
    categories.value = cats.data
    tags.value = tgs.data
    totalPosts.value = posts.data.total || 0
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.about-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 40px 32px;
  text-align: center;
}

.about-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.about-avatar {
  margin-bottom: 8px;
  box-shadow: var(--shadow);
}

.about-avatar.fallback {
  background: var(--link-color);
  color: #fff;
  font-size: 3rem;
}

.about-name {
  margin: 0;
  font-size: 1.5rem;
}

.about-email {
  margin: 0;
  color: var(--text-muted);
}

.about-section {
  text-align: left;
  margin-top: 24px;
}

.about-section h4 {
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.about-bio {
  color: var(--text-secondary);
  line-height: 1.8;
  white-space: pre-wrap;
}

.about-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
}

.stat-num {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--link-color);
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.9rem;
}
</style>
