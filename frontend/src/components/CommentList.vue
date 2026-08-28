<template>
  <div class="comment-section">
    <h3 class="comment-title">
      {{ title }}
      <span v-if="pagination.total" class="comment-count">{{ pagination.total }}</span>
    </h3>

    <!-- 评论区主体 -->
    <template v-if="postId || mode === 'message'">
      <!-- 评论列表 -->
      <div v-if="tree.length" class="comment-tree">
        <div v-for="item in tree" :key="item.id" class="comment-item">
          <CommentNode :comment="item" :can-reply="mode === 'post'" @reply="startReply" />
          <div v-if="item.children.length" class="comment-replies">
            <div v-for="child in item.children" :key="child.id" class="comment-reply">
              <CommentNode :comment="child" />
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="还没有评论，快来抢沙发～" :image-size="64" />

      <Pagination
        :total="pagination.total"
        :page="pagination.page"
        :page-size="pagination.per_page"
        @change="load"
      />

      <!-- 提交表单 -->
      <div v-if="!closed" class="comment-form">
        <div v-if="replyTo" class="reply-hint">
          回复 <b>@{{ replyTo.author_name }}</b>
          <el-button link type="primary" @click="replyTo = null">取消回复</el-button>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <div class="commenter-hint">
            <el-icon><UserFilled /></el-icon>
            以 <b>{{ auth.user?.display_name || auth.user?.nickname || auth.user?.username }}</b>
            的身份{{ mode === 'post' ? '评论' : '留言' }}
          </div>
          <el-form-item prop="content">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="4"
              maxlength="500"
              show-word-limit
              placeholder="写下你的想法…"
            />
          </el-form-item>
          <div class="form-actions">
            <el-button type="primary" :loading="submitting" @click="submit">
              {{ mode === 'post' ? '发表评论' : '提交留言' }}
            </el-button>
          </div>
        </el-form>
      </div>
      <el-alert v-else type="info" :closable="false" title="本文已关闭评论" class="closed-alert" />
    </template>

    <el-skeleton v-else :rows="3" animated />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { getComments, getMessages, submitComment, submitMessage } from '../api/front'
import { useAuthStore } from '../stores/auth'
import Pagination from './Pagination.vue'
import CommentNode from './CommentNode.vue'

const props = defineProps({
  /** 'post' 帖子评论 | 'message' 留言板 */
  mode: { type: String, default: 'post' },
  /** 帖子 slug（post 模式提交评论用） */
  postSlug: { type: String, default: '' },
  /** 帖子 id（post 模式拉取列表用；message 模式无需） */
  postId: { type: Number, default: null },
  /** 是否允许评论 */
  allowComment: { type: Boolean, default: true },
})

const formRef = ref()
const submitting = ref(false)
const replyTo = ref(null)
const auth = useAuthStore()
const pagination = reactive({ total: 0, page: 1, per_page: 20, items: [] })
const tree = ref([])
const closed = computed(() => props.mode === 'post' && !props.allowComment)

const title = computed(() => (props.mode === 'post' ? '评论' : '留言板'))

const form = reactive({
  content: '',
})

const rules = {
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
}

/** 平铺列表 → 2 层树（回复挂到父评论下） */
function buildTree(items) {
  const roots = []
  const byId = new Map()
  for (const item of items) {
    byId.set(item.id, { ...item, children: [] })
  }
  for (const node of byId.values()) {
    if (node.parent_id && byId.has(node.parent_id)) {
      byId.get(node.parent_id).children.push(node)
    } else {
      roots.push(node)
    }
  }
  return roots
}

async function load(page = pagination.page) {
  if (props.mode === 'message') {
    const { data } = await getMessages({ page })
    Object.assign(pagination, data)
    tree.value = data.items
  } else if (props.postId) {
    const { data } = await getComments({ post_id: props.postId, page })
    Object.assign(pagination, data)
    tree.value = buildTree(data.items)
  }
}

function startReply(comment) {
  replyTo.value = comment
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { content: form.content }
    if (props.mode === 'post') {
      if (replyTo.value) payload.parent_id = replyTo.value.id
      await submitComment(props.postSlug, payload)
    } else {
      await submitMessage(payload)
    }
    ElMessage.success(props.mode === 'post' ? '评论发布成功！' : '留言发布成功！')
    form.content = ''
    replyTo.value = null
    await load(1)
  } finally {
    submitting.value = false
  }
}

onMounted(() => load(1))
watch(() => props.postId, () => { if (props.postId) load(1) })
</script>

<style scoped>
.comment-section {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 20px;
  margin-top: 24px;
}

.comment-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-count {
  background: var(--link-color);
  color: #fff;
  font-size: 0.8rem;
  border-radius: 10px;
  padding: 1px 8px;
}

.comment-replies {
  margin-left: 44px;
}

.comment-form {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-color);
}

.reply-hint {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.commenter-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.commenter-hint b {
  color: var(--text-primary);
}

.form-actions {
  text-align: right;
}

.closed-alert {
  margin-top: 16px;
}
</style>
