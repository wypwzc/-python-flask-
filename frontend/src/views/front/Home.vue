<template>
  <div class="home-page">
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

    <el-empty v-else description="还没有文章，敬请期待" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getPosts } from '../../api/front'
import PostCard from '../../components/PostCard.vue'
import Pagination from '../../components/Pagination.vue'

const loading = ref(true)
const posts = ref([])
const pagination = reactive({ total: 0, page: 1, per_page: 10 })

async function load(page = 1) {
  loading.value = true
  try {
    const { data } = await getPosts({ page, per_page: pagination.per_page })
    posts.value = data.items
    Object.assign(pagination, data)
  } finally {
    loading.value = false
  }
}

onMounted(() => load(1))
</script>

<style scoped>
.skeleton-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
</style>
