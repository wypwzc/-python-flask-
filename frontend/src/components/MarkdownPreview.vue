<template>
  <div class="markdown-preview">
    <div v-if="loading" class="preview-loading">
      <el-skeleton :rows="8" animated />
    </div>
    <div v-else-if="error" class="preview-error">{{ error }}</div>
    <div v-else ref="contentRef" class="article-content" v-html="html"></div>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import hljs from 'highlight.js'
import { renderPreview } from '../api/admin'

const props = defineProps({
  /** Markdown 原文（变化时自动重新渲染） */
  content: { type: String, default: '' },
  /** 渲染防抖延迟（毫秒） */
  debounce: { type: Number, default: 400 },
})

const html = ref('')
const loading = ref(false)
const error = ref('')
const contentRef = ref()
let timer = null
let seq = 0

async function render() {
  loading.value = true
  error.value = ''
  const mySeq = ++seq
  clearTimeout(timer)
  timer = setTimeout(async () => {
    try {
      const { data } = await renderPreview({ content: props.content })
      if (mySeq !== seq) return
      html.value = data.html
      await nextTick()
      // 服务端渲染的代码块做高亮
      contentRef.value?.querySelectorAll('pre code').forEach((el) => {
        hljs.highlightElement(el)
      })
    } catch (e) {
      if (mySeq !== seq) return
      error.value = '预览渲染失败'
    } finally {
      if (mySeq === seq) loading.value = false
    }
  }, props.debounce)
}

watch(() => props.content, render, { immediate: true })
</script>

<style scoped>
.markdown-preview {
  min-height: 120px;
}

.preview-loading {
  padding: 8px;
}

.preview-error {
  color: var(--el-color-danger);
  text-align: center;
  padding: 40px 0;
}
</style>
