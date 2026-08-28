<template>
  <div class="post-edit-page">
    <div v-if="loading" class="edit-card">
      <el-skeleton :rows="8" animated />
    </div>

    <el-form v-else ref="formRef" :model="form" :rules="rules" label-position="top" class="edit-card">
      <el-row :gutter="20">
        <el-col :xs="24" :md="16">
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" maxlength="200" show-word-limit placeholder="文章标题" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item label="URL 别名（slug）" prop="slug">
            <el-input v-model="form.slug" placeholder="留空自动生成">
              <template #suffix>
                <el-tooltip content="从标题生成 slug" placement="top">
                  <el-button link type="primary" @click="generateSlug">
                    <el-icon><MagicStick /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <el-form-item label="分类" prop="category_id">
            <el-select v-model="form.category_id" placeholder="选择分类" clearable class="full-width">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item label="标签（逗号分隔）">
            <el-input v-model="tagsText" placeholder="如：Vue, Python, 随笔" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item label="封面图">
            <CoverUpload v-model="form.cover_image" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="摘要">
        <el-input
          v-model="form.summary"
          type="textarea"
          :rows="2"
          maxlength="500"
          show-word-limit
          placeholder="文章摘要（留空则自动截取正文）"
        />
      </el-form-item>

      <el-form-item label="正文（Markdown）" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="16"
          class="content-input"
          placeholder="支持 Markdown 语法，代码块可指定语言，如 ```python"
        />
      </el-form-item>

      <div class="editor-actions">
        <el-checkbox v-model="form.is_top">置顶</el-checkbox>
        <el-checkbox v-model="form.allow_comment">允许评论</el-checkbox>
        <div class="editor-buttons">
          <el-button @click="previewOpen = true">预览</el-button>
          <el-button @click="save(false)">存为草稿</el-button>
          <el-button type="primary" :loading="saving" @click="save(true)">
            {{ isEdit ? '更新并发布' : '发布' }}
          </el-button>
        </div>
      </div>
    </el-form>

    <!-- 预览抽屉 -->
    <el-drawer v-model="previewOpen" title="Markdown 预览" size="50%">
      <MarkdownPreview :content="form.content" />
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { createAdminPost, getAdminCategories, getAdminPost, updateAdminPost } from '../../api/admin'
import CoverUpload from '../../components/CoverUpload.vue'
import MarkdownPreview from '../../components/MarkdownPreview.vue'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const loading = ref(true)
const saving = ref(false)
const previewOpen = ref(false)
const categories = ref([])
const formRef = ref()

const form = reactive({
  title: '',
  slug: '',
  summary: '',
  content: '',
  category_id: null,
  cover_image: '',
  tags: [],
  is_published: true,
  is_top: false,
  allow_comment: true,
})

const tagsText = computed({
  get: () => form.tags.join(', '),
  set: (val) => {
    form.tags = val.split(/[,，]/).map((t) => t.trim()).filter(Boolean)
  },
})

const rules = {
  title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }],
}

/** 中文标题生成 slug 会为空，直接交给后端兜底 */
function generateSlug() {
  if (!form.title.trim()) {
    ElMessage.warning('请先填写标题')
    return
  }
  form.slug = form.title
    .toLowerCase()
    .replace(/[^a-z0-9一-龥]+/g, '-')
    .replace(/^-+|-+$/g, '')
  ElMessage.info('slug 已根据标题生成，可手动修改（仅支持小写字母、数字、短横线）')
}

async function load() {
  try {
    const { data } = await getAdminCategories()
    categories.value = data.items || data
  } catch {
    // 忽略
  }
  if (isEdit.value) {
    const { data } = await getAdminPost(route.params.id)
    const post = data.post
    Object.assign(form, {
      title: post.title,
      slug: post.slug,
      summary: post.summary || '',
      content: post.content || '',
      category_id: post.category?.id ?? null,
      cover_image: post.cover_image_path || '',
      tags: [...(post.tags || [])],
      is_published: !!post.is_published,
      is_top: !!post.is_top,
      allow_comment: !!post.allow_comment,
    })
  }
  loading.value = false
}

async function save(publish) {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = {
      title: form.title,
      slug: form.slug,
      summary: form.summary,
      content: form.content,
      category_id: form.category_id,
      cover_image: form.cover_image,
      tags: form.tags,
      is_published: publish,
      is_top: form.is_top,
      allow_comment: form.allow_comment,
    }
    if (isEdit.value) {
      await updateAdminPost(route.params.id, payload)
      ElMessage.success(publish ? '文章已更新并发布' : '草稿已保存')
    } else {
      const { data } = await createAdminPost(payload)
      ElMessage.success('文章创建成功！')
      router.replace(`/admin/posts/${data.post.id}/edit`)
    }
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.edit-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 24px;
}

.full-width {
  width: 100%;
}

.content-input :deep(.el-textarea__inner) {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  line-height: 1.7;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 8px;
}

.editor-buttons {
  margin-left: auto;
}
</style>
