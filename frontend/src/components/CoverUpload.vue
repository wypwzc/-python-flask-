<template>
  <div class="cover-upload">
    <el-upload
      :show-file-list="false"
      accept="image/*"
      :http-request="doUpload"
      :disabled="uploading"
    >
      <div class="upload-box" :class="{ 'has-preview': !!previewUrl }">
        <template v-if="previewUrl">
          <el-image :src="previewUrl" fit="cover" class="preview-img" />
          <div class="upload-mask">
            <el-icon><Camera /></el-icon>
            <span>点击更换</span>
          </div>
        </template>
        <template v-else>
          <el-icon :size="28"><Plus /></el-icon>
          <span>上传封面图（可选，建议 16:9）</span>
        </template>
      </div>
    </el-upload>
    <el-button v-if="modelValue" link type="danger" size="small" @click="remove">
      移除封面
    </el-button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Camera } from '@element-plus/icons-vue'
import { uploadCover } from '../api/admin'

const props = defineProps({
  /** 封面相对路径（'uploads/covers/xxx.jpg'） */
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const uploading = ref(false)

const previewUrl = computed(() =>
  props.modelValue ? `/static/${props.modelValue.replace(/^\/static\//, '')}` : ''
)

async function doUpload({ file }) {
  uploading.value = true
  try {
    const { data } = await uploadCover(file)
    emit('update:modelValue', data.path)
    ElMessage.success('封面上传成功')
  } finally {
    uploading.value = false
  }
}

function remove() {
  emit('update:modelValue', '')
}
</script>

<style scoped>
.upload-box {
  width: 320px;
  height: 160px;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.85rem;
  cursor: pointer;
  transition: border-color 0.2s;
  overflow: hidden;
  position: relative;
}

.upload-box:hover {
  border-color: var(--link-color);
}

.upload-box.has-preview {
  padding: 0;
}

.preview-img {
  width: 100%;
  height: 100%;
}

.upload-mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s;
}

.upload-box.has-preview:hover .upload-mask {
  opacity: 1;
}
</style>
