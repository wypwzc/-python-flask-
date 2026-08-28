<template>
  <div class="crud-page">
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>新建标签
      </el-button>
    </div>

    <div class="table-card">
      <el-table v-loading="loading" :data="tags">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="slug" label="URL 别名" min-width="150" />
        <el-table-column prop="post_count" label="文章数" width="90" align="center" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该标签吗？（不会删除文章）" @confirm="remove(row)">
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogOpen" :title="editing ? '编辑标签' : '新建标签'" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" maxlength="50" />
        </el-form-item>
        <el-form-item label="URL 别名" prop="slug">
          <el-input v-model="form.slug" maxlength="50" placeholder="仅小写字母、数字、短横线" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { createTag, deleteTag, getAdminTags, updateTag } from '../../api/admin'

const loading = ref(true)
const saving = ref(false)
const dialogOpen = ref(false)
const editing = ref(null)
const tags = ref([])
const formRef = ref()

const form = reactive({ name: '', slug: '' })

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  slug: [
    { required: true, message: '请输入 URL 别名', trigger: 'blur' },
    { pattern: /^[a-z0-9-]+$/, message: '仅支持小写字母、数字和短横线', trigger: 'blur' },
  ],
}

async function load() {
  loading.value = true
  try {
    const { data } = await getAdminTags()
    tags.value = data.items
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  editing.value = row || null
  Object.assign(form, { name: row?.name || '', slug: row?.slug || '' })
  dialogOpen.value = true
}

async function save() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (editing.value) {
      await updateTag(editing.value.id, { ...form })
      ElMessage.success('标签更新成功')
    } else {
      await createTag({ ...form })
      ElMessage.success('标签创建成功')
    }
    dialogOpen.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  const { data } = await deleteTag(row.id)
  ElMessage.success(data.message)
  load()
}

onMounted(load)
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
</style>
