<template>
  <div class="sidebar">
    <!-- 博客统计 -->
    <div class="sidebar-section">
      <h3 class="section-title">博客统计</h3>
      <div class="section-body stats">
        <span>总访问量 {{ totalStats.total_pv || 0 }} PV</span>
        <span>访客数 {{ totalStats.total_uv || 0 }} UV</span>
      </div>
    </div>

    <!-- 分类 -->
    <div class="sidebar-section">
      <h3 class="section-title">分类</h3>
      <div class="section-body">
        <div v-for="cat in categories" :key="cat.id" class="sidebar-list-item">
          <router-link :to="{ name: 'category', params: { slug: cat.slug } }">
            {{ cat.name }}
          </router-link>
          <span class="count">{{ cat.post_count }}</span>
        </div>
        <el-empty v-if="!categories.length" description="暂无分类" :image-size="48" />
      </div>
    </div>

    <!-- 最新文章 -->
    <div class="sidebar-section">
      <h3 class="section-title">最新文章</h3>
      <div class="section-body">
        <div v-for="post in recentPosts" :key="post.id" class="sidebar-list-item">
          <router-link :to="{ name: 'post-detail', params: { slug: post.slug } }">
            {{ post.title }}
          </router-link>
          <span class="count">{{ formatDateTime(post.published_at, 'MM-DD') }}</span>
        </div>
        <el-empty v-if="!recentPosts.length" description="暂无文章" :image-size="48" />
      </div>
    </div>

    <!-- 最新留言 -->
    <div class="sidebar-section">
      <h3 class="section-title">最新留言</h3>
      <div class="section-body">
        <div v-for="c in recentComments" :key="c.id" class="comment-excerpt">
          <span class="comment-author">{{ c.author_name }}：</span>
          <span class="comment-content">{{ truncate(c.content, 30) }}</span>
        </div>
        <el-empty v-if="!recentComments.length" description="暂无留言" :image-size="48" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatDateTime } from '../utils/date'
import { truncate } from '../utils/text'

defineProps({
  categories: { type: Array, default: () => [] },
  recentPosts: { type: Array, default: () => [] },
  recentComments: { type: Array, default: () => [] },
  totalStats: { type: Object, default: () => ({ total_pv: 0, total_uv: 0 }) },
})
</script>

<style scoped>
.stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.comment-excerpt {
  padding: 6px 0;
  font-size: 0.88rem;
  line-height: 1.5;
  border-bottom: 1px dashed var(--border-color);
}

.comment-excerpt:last-child {
  border-bottom: none;
}

.comment-author {
  color: var(--link-color);
}

.comment-content {
  color: var(--text-secondary);
}
</style>
