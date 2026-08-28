<template>
  <div class="links-page">
    <div class="page-header">
      <h1>友情链接</h1>
      <p class="page-desc">推荐一些有趣的网站</p>
    </div>

    <div v-if="loading">
      <el-skeleton :rows="4" animated class="skeleton-card" />
    </div>

    <div v-else-if="links.length" class="link-grid">
      <a
        v-for="link in links"
        :key="link.id"
        :href="link.url"
        target="_blank"
        rel="noopener noreferrer"
        class="link-card"
      >
        <div class="link-icon">{{ (link.name || '友')[0] }}</div>
        <div class="link-info">
          <div class="link-name">{{ link.name }}</div>
          <div class="link-desc">{{ link.description || link.url }}</div>
        </div>
      </a>
    </div>

    <el-empty v-else description="暂无友情链接" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getLinks } from '../../api/front'

const loading = ref(true)
const links = ref([])

onMounted(async () => {
  try {
    const { data } = await getLinks()
    links.value = data
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

.link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.link-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.3s, transform 0.2s;
  color: var(--text-primary);
}

.link-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  color: var(--text-primary);
}

.link-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, #409eff, #7c4dff);
  color: #fff;
  font-size: 1.2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.link-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.link-desc {
  font-size: 0.82rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.skeleton-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
}
</style>
