<template>
  <div v-if="total > 0" class="pagination-wrap">
    <el-pagination
      layout="prev, pager, next"
      background
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="(p) => emit('change', p)"
    />
    <span class="page-info">共 {{ total }} 条</span>
  </div>
</template>

<script setup>
defineProps({
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
})

const emit = defineEmits(['change'])
</script>

<style scoped>
.pagination-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 24px 0;
}

.page-info {
  font-size: 0.85rem;
  color: var(--text-muted);
}
</style>
