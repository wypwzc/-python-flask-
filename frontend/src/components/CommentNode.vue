<template>
  <div class="comment-node">
    <div class="comment-avatar">{{ (comment.author_name || '匿')[0] }}</div>
    <div class="comment-body">
      <div class="comment-header">
        <span class="author-name">
          {{ comment.author_name }}
          <el-tag v-if="comment.is_admin" type="danger" size="small" effect="dark">博主</el-tag>
        </span>
        <span class="comment-time">{{ timeAgo(comment.created_at) }}</span>
        <el-button v-if="canReply" link type="primary" size="small" @click="$emit('reply', comment)">
          回复
        </el-button>
      </div>
      <div class="comment-content">{{ comment.content }}</div>
    </div>
  </div>
</template>

<script setup>
import { timeAgo } from '../utils/date'

defineProps({
  comment: { type: Object, required: true },
  canReply: { type: Boolean, default: false },
})

defineEmits(['reply'])
</script>

<style scoped>
.comment-node {
  display: flex;
  gap: 12px;
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.author-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.comment-time {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.comment-content {
  font-size: 0.95rem;
  color: var(--text-primary);
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
