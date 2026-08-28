<template>
  <div class="dashboard-page">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card">
          <div class="stat-card-value">{{ counts.posts }}</div>
          <div class="stat-card-label">文章总数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card">
          <div class="stat-card-value">{{ counts.pending_comments }}</div>
          <div class="stat-card-label">待审核评论</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card">
          <div class="stat-card-value">{{ counts.comments }}</div>
          <div class="stat-card-label">评论总数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card">
          <div class="stat-card-value">{{ counts.categories }}</div>
          <div class="stat-card-label">分类数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card">
          <div class="stat-card-value">{{ counts.tags }}</div>
          <div class="stat-card-label">标签数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card">
          <div class="stat-card-value">{{ totalStats.total_pv || 0 }}</div>
          <div class="stat-card-label">累计 PV</div>
        </div>
      </el-col>
    </el-row>

    <!-- 访问趋势 -->
    <div class="panel">
      <h3 class="panel-title">最近 7 天访问趋势</h3>
      <div ref="chartRef" class="chart"></div>
    </div>

    <!-- 最新数据 -->
    <el-row :gutter="16">
      <el-col :xs="24" :md="12">
        <div class="panel">
          <h3 class="panel-title">最新文章</h3>
          <div v-for="p in recentPosts" :key="p.id" class="panel-item">
            <router-link :to="{ name: 'admin-post-edit', params: { id: p.id } }" class="item-title">
              {{ p.title }}
            </router-link>
            <span class="item-meta">
              {{ p.views }} 阅读 · {{ formatDateTime(p.created_at, 'MM-DD HH:mm') }}
            </span>
          </div>
          <el-empty v-if="!recentPosts.length" description="暂无文章" :image-size="48" />
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="panel">
          <h3 class="panel-title">最新评论</h3>
          <div v-for="c in recentComments" :key="c.id" class="panel-item">
            <div class="item-title">
              {{ c.author_name }}：{{ truncate(c.content, 40) }}
            </div>
            <span class="item-meta">{{ c.post_title }} · {{ timeAgo(c.created_at) }}</span>
          </div>
          <el-empty v-if="!recentComments.length" description="暂无评论" :image-size="48" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getDashboardStats } from '../../api/admin'
import { formatDateTime, timeAgo } from '../../utils/date'
import { truncate } from '../../utils/text'

const counts = ref({ posts: 0, categories: 0, tags: 0, comments: 0, pending_comments: 0 })
const totalStats = ref({ total_pv: 0, total_uv: 0 })
const recentPosts = ref([])
const recentComments = ref([])

const chartRef = ref()
let chart = null

async function load() {
  const { data } = await getDashboardStats()
  counts.value = data.counts
  totalStats.value = data.total_stats
  recentPosts.value = data.recent_posts
  recentComments.value = data.recent_comments
  await nextTick()
  renderChart(data.recent_stats)
}

function renderChart(stats) {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  const dark = document.documentElement.classList.contains('dark')
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['PV', 'UV'], textStyle: { color: dark ? '#b0b3b8' : '#6c757d' } },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category',
      data: stats.map((s) => s.date.slice(5)),
      axisLine: { lineStyle: { color: dark ? '#3a3b3c' : '#dee2e6' } },
      axisLabel: { color: dark ? '#b0b3b8' : '#6c757d' },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: { color: dark ? '#b0b3b8' : '#6c757d' },
      splitLine: { lineStyle: { color: dark ? '#3a3b3c' : '#f0f0f0' } },
    },
    series: [
      {
        name: 'PV',
        type: 'line',
        smooth: true,
        data: stats.map((s) => s.pv),
        itemStyle: { color: '#409eff' },
        areaStyle: { opacity: 0.15 },
      },
      {
        name: 'UV',
        type: 'line',
        smooth: true,
        data: stats.map((s) => s.uv),
        itemStyle: { color: '#67c23a' },
        areaStyle: { opacity: 0.15 },
      },
    ],
  })
}

onMounted(() => {
  load()
  window.addEventListener('resize', resizeChart)
})

function resizeChart() {
  chart?.resize()
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
})
</script>

<style scoped>
.stat-cards {
  margin-bottom: 16px;
}

.stat-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 20px;
  text-align: center;
  margin-bottom: 16px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--link-color);
  margin-bottom: 4px;
}

.stat-card-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.panel {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 20px;
  margin-bottom: 16px;
}

.panel-title {
  margin: 0 0 16px;
  font-size: 1.05rem;
  font-weight: 600;
}

.chart {
  height: 320px;
}

.panel-item {
  padding: 10px 0;
  border-bottom: 1px dashed var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

.panel-item:last-child {
  border-bottom: none;
}

.item-title {
  font-size: 0.95rem;
  color: var(--text-primary);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.item-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
  white-space: nowrap;
}
</style>
