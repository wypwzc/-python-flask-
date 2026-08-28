<template>
  <div class="crud-page">
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>新建友链
      </el-button>
    </div>

    <div class="table-card">
      <el-table v-loading="loading" :data="links">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="130" />
        <el-table-column label="地址" min-width="200">
          <template #default="{ row }">
            <a :href="row.url" target="_blank" rel="noopener noreferrer" class="link-url">{{ row.url }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.description || '—' }}</template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '显示' : '隐藏' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该友链吗？" @confirm="remove(row)">
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogOpen" :title="editing ? '编辑友链' : '新建友链'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="站点名称" prop="name">
          <el-input v-model="form.name" maxlength="50" />
        </el-form-item>
        <el-form-item label="站点地址" prop="url">
          <el-input v-model="form.url" maxlength="200" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" maxlength="200" />
        </el-form-item>
        <el-form-item label="Logo 地址">
          <el-input v-model="form.logo" maxlength="255" placeholder="https://（可选）" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" :max="999" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch v-model="form.is_active" active-text="显示" inactive-text="隐藏" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { createLink, deleteLink, getAdminLinks, updateLink } from '../../api/admin'

const loading = ref(true)
const saving = ref(false)
const dialogOpen = ref(false)
const editing = ref(null)
const links = ref([])
const formRef = ref()

const form = reactive({
  name: '',
  url: '',
  description: '',
  logo: '',
  sort_order: 0,
  is_active: true,
})

const rules = {
  name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
  url: [
    { required: true, message: '请输入站点地址', trigger: 'blur' },
    { pattern: /^https?:\/\//, message: '需以 http:// 或 https:// 开头', trigger: 'blur' },
  ],
}

async function load() {
  loading.value = true
  try {
    const { data } = await getAdminLinks()
    links.value = data.items
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  editing.value = row || null
  Object.assign(form, {
    name: row?.name || '',
    url: row?.url || '',
    description: row?.description || '',
    logo: row?.logo || '',
    sort_order: row?.sort_order ?? 0,
    is_active: row ? !!row.is_active : true,
  })
  dialogOpen.value = true
}

async function save() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (editing.value) {
      await updateLink(editing.value.id, { ...form })
      ElMessage.success('友链更新成功')
    } else {
      await createLink({ ...form })
      ElMessage.success('友链创建成功')
    }
    dialogOpen.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  const { data } = await deleteLink(row.id)
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

.link-url {
  color: var(--link-color);
  font-size: 0.9rem;
}
</style>
