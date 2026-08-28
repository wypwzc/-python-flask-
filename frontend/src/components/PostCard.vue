<template>
  <article class="post-card fade-in">
    <router-link v-if="post.cover_image" :to="detailLink" class="cover-link">
      <el-image
        class="cover-image"
        :src="post.cover_image"
        :preview-src-list="[post.cover_image]"
        fit="cover"
        lazy
      />
    </router-link>
    <div class="card-body">
      <div class="card-top">
        <router-link
          v-if="post.category"
          :to="{ name: 'category', params: { slug: post.category.slug } }"
          class="category-badge"
        >
          {{ post.category.name }}
        </router-link>
        <el-tag v-if="post.is_top" type="danger" size="small" effect="dark">置顶</el-tag>
      </div>
      <router-link :to="detailLink" class="post-title">{{ post.title }}</router-link>
      <p class="post-summary">{{ post.summary }}</p>
      <div class="post-meta">
        <span class="meta-item">
          <el-icon><Calendar /></el-icon>
          {{ formatDateTime(post.published_at, 'YYYY-MM-DD') }}
        </span>
        <span class="meta-item">
          <el-icon><View /></el-icon>
          {{ post.views }} 阅读
        </span>
        <span class="meta-item">
          <el-icon><Star /></el-icon>
          {{ post.likes }} 点赞
        </span>
        <span v-for="tag in post.tags" :key="tag" class="meta-tag">
          <router-link :to="{ name: 'tag', params: { slug: tag } }">#{{ tag }}</router-link>
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { Calendar, View, Star } from '@element-plus/icons-vue'
import { formatDateTime } from '../utils/date'

const props = defineProps({
  post: { type: Object, required: true },
})

const detailLink = computed(() => ({
  name: 'post-detail',
  params: { slug: props.post.slug },
}))
</script>

<style scoped>
.post-card {
  margin-bottom: 20px;
}

.cover-link {
  display: block;
}

.cover-image {
  width: 100%;
  height: 180px;
  border-radius: 12px 12px 0 0;
}

.card-body {
  padding: 16px 20px 20px;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.category-badge {
  font-size: 0.8rem;
  color: var(--link-color);
  background: var(--bg-secondary);
  padding: 1px 10px;
  border-radius: 10px;
}

.category-badge:hover {
  color: var(--link-hover-color);
}

.post-title {
  display: block;
  margin-bottom: 8px;
}

.post-summary {
  margin: 0 0 12px;
}

.post-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.meta-tag a {
  color: var(--link-color);
  font-size: 0.85rem;
}
</style>
