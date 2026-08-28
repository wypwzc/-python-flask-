<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <div class="login-title">
          <el-icon :size="22" color="#409eff"><Monitor /></el-icon>
          <span>{{ isAdminPort ? '博客后台登录' : '登录' }}</span>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="submit">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="!isAdminPort" class="login-footer">
        <router-link :to="{ name: 'register', query: $route.query }">没有账号？注册 →</router-link>
      </div>
      <div v-else class="login-footer">
        <a href="http://localhost:5000">访问博客前台 →</a>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isAdminPort = window.location.port === '5888'

const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  remember: true,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await auth.login({ ...form })
    ElMessage.success('登录成功')
    if (route.query.redirect) {
      router.replace(route.query.redirect)
    } else if (auth.isAdmin) {
      // 管理员：5888 登录进后台；5000 登录后引导去 5888 后台
      isAdminPort ? router.replace('/admin') : window.location.href = 'http://localhost:5888'
    } else {
      router.replace('/')
    }
  } catch {
    // 错误信息已由拦截器提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 16px;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.login-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 1.1rem;
}

.login-btn {
  width: 100%;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.login-footer a:hover {
  color: var(--el-color-primary);
}
</style>
