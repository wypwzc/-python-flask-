<template>
  <div class="tag-page">
    <div class="page-header">
      <h1>标签：#{{ route.params.slug }}</h1>
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

    <el-empty v-else description="该标签下暂无文章" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPosts } from '../../api/front'
import PostCard from '../../components/PostCard.vue'
import Pagination from '../../components/Pagination.vue'

const route = useRoute()
const loading = ref(true)
const posts = ref([])
const pagination = reactive({ total: 0, page: 1, per_page: 10 })

async function load(page = 1) {
  loading.value = true
  try {
    const { data } = await getPosts({ page, per_page: pagination.per_page, tag: route.params.slug })
    posts.value = data.items
    Object.assign(pagination, data)
  } finally {
    loading.value = false
  }
}

watch(() => route.params.slug, () => {
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
  margin: 0;
  font-size: 1.4rem;
}

.skeleton-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
</style>
