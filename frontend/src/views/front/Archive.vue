<template>
  <div class="archive-page">
    <div class="page-header">
      <h1>文章归档</h1>
      <p class="page-desc">共 {{ totalPosts }} 篇文章，按时间倒序排列</p>
    </div>

    <div v-if="loading">
      <el-skeleton :rows="6" animated class="skeleton-card" />
    </div>

    <el-empty v-else-if="!years.length" description="暂无文章" />

    <el-collapse v-else v-model="openYears" class="archive-collapse">
      <el-collapse-item v-for="year in years" :key="year" :name="String(year)">
        <template #title>
          <span class="archive-year-title">{{ year }} 年（{{ yearCount(year) }} 篇）</span>
        </template>
        <div class="archive-month">
          <div v-for="month in monthsOf(year)" :key="month.month" class="archive-month-block">
            <h3 class="archive-month-title">{{ month.month }} 月（{{ month.count }} 篇）</h3>
            <div v-for="post in month.posts" :key="post.id" class="archive-post">
              <span class="date">{{ formatDateTime(post.published_at, 'MM-DD') }}</span>
              <router-link :to="{ name: 'post-detail', params: { slug: post.slug } }">
                {{ post.title }}
              </router-link>
            </div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getArchive } from '../../api/front'
import { formatDateTime } from '../../utils/date'

const loading = ref(true)
const archives = ref({})
const openYears = ref([])

const years = computed(() => Object.keys(archives.value).sort((a, b) => b - a))
const totalPosts = computed(() => years.value.reduce((sum, y) => sum + yearCount(y), 0))

function yearCount(year) {
  return Object.values(archives.value[year] || {}).reduce((sum, m) => sum + (m.count || 0), 0)
}

function monthsOf(year) {
  return Object.entries(archives.value[year] || {})
    .map(([month, data]) => ({ month, ...data }))
    .sort((a, b) => Number(b.month) - Number(a.month))
}

onMounted(async () => {
  try {
    const { data } = await getArchive()
    archives.value = data.archives || {}
    // 默认展开最近一年
    if (years.value.length) openYears.value = [String(years.value[0])]
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-header {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}

.page-header h1 {
  margin: 0 0 8px;
  font-size: 1.4rem;
}

.page-desc {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.archive-collapse {
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  border: none;
  padding: 8px 16px;
}

.archive-collapse :deep(.el-collapse-item__header) {
  background: transparent;
  border-bottom-color: var(--border-color);
}

.archive-collapse :deep(.el-collapse-item__wrap) {
  background: transparent;
  border-bottom: none;
}

.archive-collapse :deep(.el-collapse-item__content) {
  padding-bottom: 12px;
}

.skeleton-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
}
</style>
