<template>
  <div class="category-page">
    <div class="page-header">
      <h1>分类：{{ category?.name || route.params.slug }}</h1>
      <p v-if="category?.description" class="page-desc">{{ category.description }}</p>
    </div>

    <div v-if="loading" class="post-list">
      <el-skeleton v-for="i in 5" :key="i" :rows="3" animated class="skeleton-card" />
    </div>

    <template v-else-if="posts.length">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
      <Pagination
        :total="pagination.total"
        :page="pagination.page"
        :page-size="pagination.per_page"
        @change="load"
      />
    </template>

    <el-empty v-else description="该分类下暂无文章" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getCategories, getPosts } from '../../api/front'
import PostCard from '../../components/PostCard.vue'
import Pagination from '../../components/Pagination.vue'

const route = useRoute()
const loading = ref(true)
const posts = ref([])
const category = ref(null)
const pagination = reactive({ total: 0, page: 1, per_page: 10 })

async function load(page = 1) {
  loading.value = true
  try {
    const { data } = await getPosts({ page, per_page: pagination.per_page, category: route.params.slug })
    posts.value = data.items
    Object.assign(pagination, data)
  } finally {
    loading.value = false
  }
}

async function fetchCategory() {
  try {
    const { data } = await getCategories()
    category.value = data.find((c) => c.slug === route.params.slug) || null
  } catch {
    category.value = null
  }
}

watch(() => route.params.slug, () => {
  posts.value = []
  fetchCategory()
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

.page-desc {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.skeleton-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
</style>
