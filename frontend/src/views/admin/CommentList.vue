<template>
  <div class="comment-list-page">
    <!-- 筛选 -->
    <div class="toolbar">
      <el-radio-group v-model="status" @change="load(1)">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="pending">待审核</el-radio-button>
        <el-radio-button value="approved">已通过</el-radio-button>
      </el-radio-group>
    </div>

    <div class="table-card">
      <el-table v-loading="loading" :data="comments">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="作者" width="130">
          <template #default="{ row }">
            <div class="author-cell">
              <span>{{ row.author_name }}</span>
              <el-tag v-if="row.is_admin" type="danger" size="small" effect="dark">博主</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="comment-text">{{ row.content }}</span>
          </template>
        </el-table-column>
        <el-table-column label="所在位置" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="post-loc">{{ row.post_title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_approved ? 'success' : 'warning'" size="small">
              {{ row.is_approved ? '已通过' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="130">
          <template #default="{ row }">{{ formatDateTime(row.created_at, 'YYYY-MM-DD HH:mm') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" size="small" @click="toggleApprove(row)">
              {{ row.is_approved ? '取消审核' : '通过' }}
            </el-button>
            <el-button link type="primary" size="small" @click="openReply(row)">回复</el-button>
            <el-popconfirm title="确定删除该评论吗？" @confirm="remove(row)">
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

    <!-- 回复弹窗 -->
    <el-dialog v-model="replyOpen" title="博主回复" width="520px">
      <div class="reply-context">
        <b>{{ replyTarget?.author_name }}</b>：{{ replyTarget?.content }}
      </div>
      <el-input
        v-model="replyContent"
        type="textarea"
        :rows="4"
        maxlength="500"
        show-word-limit
        placeholder="回复将以博主身份发布，并通知对方"
      />
      <template #footer>
        <el-button @click="replyOpen = false">取消</el-button>
        <el-button type="primary" :loading="replying" @click="doReply">回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  approveComment, deleteComment, getAdminComments, replyComment,
} from '../../api/admin'
import { formatDateTime } from '../../utils/date'

const loading = ref(true)
const status = ref('all')
const comments = ref([])
const pagination = reactive({ total: 0, page: 1, per_page: 20 })

const replyOpen = ref(false)
const replying = ref(false)
const replyTarget = ref(null)
const replyContent = ref('')

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page, per_page: pagination.per_page }
    if (status.value !== 'all') params.status = status.value
    const { data } = await getAdminComments(params)
    comments.value = data.items
    Object.assign(pagination, data)
  } finally {
    loading.value = false
  }
}

async function toggleApprove(row) {
  const { data } = await approveComment(row.id)
  row.is_approved = data.is_approved
  ElMessage.success(data.message)
}

async function remove(row) {
  const { data } = await deleteComment(row.id)
  ElMessage.success(data.message)
  load(comments.value.length === 1 ? Math.max(1, pagination.page - 1) : pagination.page)
}

function openReply(row) {
  replyTarget.value = row
  replyContent.value = ''
  replyOpen.value = true
}

async function doReply() {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  replying.value = true
  try {
    const { data } = await replyComment(replyTarget.value.id, replyContent.value.trim())
    ElMessage.success(data.message)
    replyOpen.value = false
    load(pagination.page)
  } finally {
    replying.value = false
  }
}

onMounted(() => load(1))
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}

.table-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 16px;
}

.author-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.comment-text {
  color: var(--text-primary);
}

.post-loc {
  font-size: 0.9rem;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.reply-context {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  word-break: break-word;
}
</style>
