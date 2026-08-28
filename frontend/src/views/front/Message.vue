<template>
  <div class="message-page">
    <div class="page-header">
      <h1>留言板</h1>
      <p class="page-desc">有什么想说的都可以在这里留言～</p>
    </div>
    <CommentList mode="message" />
  </div>
</template>

<script setup>
import CommentList from '../../components/CommentList.vue'
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
</style>
