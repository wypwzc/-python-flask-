<template>
  <div class="search-page">
    <div class="page-header">
      <h1>
        搜索：
        <span v-if="q" class="highlight-word">{{ q }}</span>
        <template v-else>全部文章</template>
      </h1>
      <p v-if="q && !loading" class="page-desc">找到 {{ pagination.total }} 条结果</p>
    </div>

    <div v-if="loading" class="post-list">
      <el-skeleton v-for="i in 5" :key="i" :rows="3" animated class="skeleton-card" />
    </div>

    <template v-else-if="posts.length">
      <div v-for="post in posts" :key="post.id" class="search-result post-card">
        <h3 class="result-title">
          <router-link :to="{ name: 'post-detail', params: { slug: post.slug } }"
            v-html="highlight(post.title)" />
        </h3>
        <p class="result-summary" v-html="highlight(post.summary)" />
        <div class="result-meta">
          <span>{{ formatDateTime(post.published_at, 'YYYY-MM-DD') }}</span>
          <span>{{ post.views }} 阅读</span>
        </div>
      </div>
      <Pagination
        :total="pagination.total"
        :page="pagination.page"
        :page-size="pagination.per_page"
        @change="load"
      />
    </template>

    <el-empty v-else-if="!loading" description="没有找到相关文章" />
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPosts } from '../../api/front'
import { formatDateTime } from '../../utils/date'
import Pagination from '../../components/Pagination.vue'

const route = useRoute()
const loading = ref(true)
const posts = ref([])
const pagination = reactive({ total: 0, page: 1, per_page: 10 })

const q = computed(() => (route.query.q || '').trim())

/** 关键词高亮（转义后包裹 mark，防 XSS） */
function highlight(text) {
  if (!text || !q.value) return text || ''
  const escaped = String(text).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[c])
  const pattern = q.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return escaped.replace(new RegExp(pattern, 'gi'), (m) => `<mark>${m}</mark>`)
}

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page, per_page: pagination.per_page }
    if (q.value) params.q = q.value
    const { data } = await getPosts(params)
    posts.value = data.items
    Object.assign(pagination, data)
  } finally {
    loading.value = false
  }
}

watch(q, () => {
  posts.value = []
  load(1)
}, { immediate: true })
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

.highlight-word {
  color: var(--link-color);
}

.page-desc {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.search-result {
  padding: 16px 20px;
  margin-bottom: 16px;
}

.result-title {
  margin: 0 0 8px;
  font-size: 1.15rem;
}

.result-summary {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 0.95rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
  display: flex;
  gap: 14px;
}

:deep(mark) {
  background: rgba(255, 193, 7, 0.4);
  color: inherit;
  border-radius: 2px;
  padding: 0 2px;
}

.skeleton-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
</style>
