<template>
  <div class="profile-page">
    <el-row :gutter="16">
      <!-- 个人资料 -->
      <el-col :xs="24" :md="14">
        <div class="panel">
          <h3 class="panel-title">个人资料</h3>
          <div v-if="loading">
            <el-skeleton :rows="5" animated />
          </div>
          <el-form v-else ref="profileRef" :model="profile" :rules="profileRules" label-width="80px">
            <el-form-item label="用户名">
              <el-input :model-value="profile.username" disabled />
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="profile.nickname" maxlength="50" placeholder="显示在前台的名字" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profile.email" maxlength="100" />
            </el-form-item>
            <el-form-item label="简介" prop="bio">
              <el-input
                v-model="profile.bio"
                type="textarea"
                :rows="4"
                maxlength="500"
                show-word-limit
                placeholder="一句话介绍自己（显示在「关于我」页面）"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingProfile" @click="saveProfile">
                保存资料
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <!-- 头像 + 密码 -->
      <el-col :xs="24" :md="10">
        <div class="panel">
          <h3 class="panel-title">头像</h3>
          <div class="avatar-area">
            <el-avatar v-if="avatarUrl" :src="avatarUrl" :size="96" class="avatar-preview" />
            <el-avatar v-else :size="96" class="avatar-preview fallback">
              {{ (profile.nickname || profile.username || 'A')[0] }}
            </el-avatar>
            <el-upload :show-file-list="false" accept="image/*" :http-request="doUploadAvatar">
              <el-button :loading="uploadingAvatar">更换头像</el-button>
            </el-upload>
          </div>
        </div>

        <div class="panel">
          <h3 class="panel-title">修改密码</h3>
          <el-form ref="pwdRef" :model="pwd" :rules="pwdRules" label-width="80px">
            <el-form-item label="当前密码" prop="old_password">
              <el-input v-model="pwd.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="pwd.new_password" type="password" show-password placeholder="至少 6 位" />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm">
              <el-input v-model="pwd.confirm" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingPwd" @click="savePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword, getProfile, updateProfile, uploadAvatar } from '../../api/admin'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const savingProfile = ref(false)
const savingPwd = ref(false)
const uploadingAvatar = ref(false)
const profileRef = ref()
const pwdRef = ref()

const profile = reactive({
  username: '',
  nickname: '',
  email: '',
  bio: '',
  avatar_path: '',
})

const avatarUrl = computed(() =>
  profile.avatar_path ? `/static/${profile.avatar_path.replace(/^\/static\//, '')}` : ''
)

const profileRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

const pwd = reactive({ old_password: '', new_password: '', confirm: '' })

const pwdRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少 6 位', trigger: 'blur' },
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_, value, cb) => {
        if (value !== pwd.new_password) cb(new Error('两次输入的密码不一致'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
}

async function load() {
  loading.value = true
  try {
    const { data } = await getProfile()
    const user = data.user
    Object.assign(profile, {
      username: user.username,
      nickname: user.nickname || '',
      email: user.email || '',
      bio: user.bio || '',
      avatar_path: user.avatar_path || '',
    })
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  const valid = await profileRef.value.validate().catch(() => false)
  if (!valid) return
  savingProfile.value = true
  try {
    const { data } = await updateProfile({
      nickname: profile.nickname,
      email: profile.email,
      bio: profile.bio,
      avatar_path: profile.avatar_path,
    })
    // 同步侧边栏等处的登录态昵称
    auth.user = { ...auth.user, ...data.user }
    ElMessage.success(data.message)
  } finally {
    savingProfile.value = false
  }
}

async function doUploadAvatar({ file }) {
  uploadingAvatar.value = true
  try {
    const { data } = await uploadAvatar(file)
    profile.avatar_path = data.path
    auth.user = { ...auth.user, avatar: `/static/${data.path.replace(/^\/static\//, '')}` }
    ElMessage.success('头像上传成功')
  } finally {
    uploadingAvatar.value = false
  }
}

async function savePassword() {
  const valid = await pwdRef.value.validate().catch(() => false)
  if (!valid) return
  savingPwd.value = true
  try {
    const { data } = await changePassword({
      old_password: pwd.old_password,
      new_password: pwd.new_password,
    })
    ElMessage.success(data.message)
    pwd.old_password = ''
    pwd.new_password = ''
    pwd.confirm = ''
  } finally {
    savingPwd.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.panel {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 20px;
  margin-bottom: 16px;
}

.panel-title {
  margin: 0 0 16px;
  font-size: 1.05rem;
  font-weight: 600;
}

.avatar-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
}

.avatar-preview {
  box-shadow: var(--shadow);
}

.avatar-preview.fallback {
  background: var(--link-color);
  color: #fff;
  font-size: 2.5rem;
}
</style>
