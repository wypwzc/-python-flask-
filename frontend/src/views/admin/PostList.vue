<template>
  <div class="post-list-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="filters.q"
        placeholder="搜索文章标题…"
        clearable
        class="toolbar-search"
        :prefix-icon="Search"
        @keyup.enter="load(1)"
        @clear="load(1)"
      />
      <el-select v-model="filters.category_id" placeholder="全部分类" clearable class="toolbar-select">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select v-model="filters.status" placeholder="全部状态" class="toolbar-select">
        <el-option label="全部状态" value="all" />
        <el-option label="已发布" value="published" />
        <el-option label="草稿" value="draft" />
      </el-select>
      <el-button type="primary" @click="load(1)">查询</el-button>
      <div class="toolbar-right">
        <el-button type="danger" plain :disabled="!selected.length" @click="batchDelete">
          批量删除（{{ selected.length }}）
        </el-button>
        <el-button type="primary" @click="router.push('/admin/posts/create')">
          <el-icon><Plus /></el-icon>写文章
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table v-loading="loading" :data="posts" @selection-change="onSelectionChange">
        <el-table-column type="selection" width="45" />
        <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="title-cell">
              <span>{{ row.title }}</span>
              <el-tag v-if="row.is_top" type="danger" size="small" effect="dark">置顶</el-tag>
              <el-tag v-if="!row.is_published" type="info" size="small">草稿</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="110">
          <template #default="{ row }">{{ row.category?.name || '—' }}</template>
        </el-table-column>
        <el-table-column label="标签" min-width="140">
          <template #default="{ row }">
            <el-tag v-for="t in row.tags.slice(0, 3)" :key="t" size="small" class="tag-cell">
              {{ t }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="阅读" width="70" align="center" />
        <el-table-column prop="likes" label="点赞" width="70" align="center" />
        <el-table-column label="发布时间" width="130">
          <template #default="{ row }">
            {{ formatDateTime(row.published_at, 'YYYY-MM-DD') || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="router.push(`/admin/posts/${row.id}/edit`)">
              编辑
            </el-button>
            <el-button link type="warning" size="small" @click="togglePublish(row)">
              {{ row.is_published ? '下架' : '发布' }}
            </el-button>
            <el-button link type="danger" size="small" @click="toggleTop(row)">
              {{ row.is_top ? '取消置顶' : '置顶' }}
            </el-button>
            <el-popconfirm title="确定删除该文章吗？" @confirm="remove(row)">
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <el-pagination
          layout="total, prev, pager, next"
          background
          :total="pagination.total"
          :page-size="pagination.per_page"
          :current-page="pagination.page"
          @current-change="load"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import {
  batchDeletePosts, deleteAdminPost, getAdminCategories, getAdminPosts,
  togglePublish as apiTogglePublish, toggleTop as apiToggleTop,
} from '../../api/admin'
import { formatDateTime } from '../../utils/date'

const router = useRouter()
const loading = ref(true)
const posts = ref([])
const categories = ref([])
const selected = ref([])
const filters = reactive({ q: '', category_id: null, status: 'all' })
const pagination = reactive({ total: 0, page: 1, per_page: 15 })

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page, per_page: pagination.per_page }
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.status !== 'all') params.status = filters.status
    const { data } = await getAdminPosts(params)
    posts.value = data.items
    Object.assign(pagination, data)
  } finally {
    loading.value = false
  }
}

function onSelectionChange(rows) {
  selected.value = rows
}

async function togglePublish(row) {
  const { data } = await apiTogglePublish(row.id)
  row.is_published = !row.is_published
  ElMessage.success(data.message)
}

async function toggleTop(row) {
  const { data } = await apiToggleTop(row.id)
  row.is_top = !row.is_top
  ElMessage.success(data.message)
}

async function remove(row) {
  const { data } = await deleteAdminPost(row.id)
  ElMessage.success(data.message)
  load(posts.value.length === 1 ? Math.max(1, pagination.page - 1) : pagination.page)
}

async function batchDelete() {
  await ElMessageBox.confirm(`确定删除选中的 ${selected.value.length} 篇文章吗？此操作不可恢复。`, '批量删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  const ids = selected.value.map((p) => p.id)
  const { data } = await batchDeletePosts(ids)
  ElMessage.success(data.message)
  load(1)
}

onMounted(async () => {
  load(1)
  try {
    const { data } = await getAdminCategories()
    categories.value = data
  } catch {
    // 分类加载失败不阻塞列表
  }
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.toolbar-search {
  width: 220px;
}

.toolbar-select {
  width: 140px;
}

.toolbar-right {
  margin-left: auto;
  display: flex;
  gap: 12px;
}

.table-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 16px;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-cell {
  margin-right: 4px;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
