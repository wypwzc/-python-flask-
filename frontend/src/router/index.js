/**
 * 路由配置
 * 前台页面挂在 FrontLayout 下（公共导航/页脚）；后台挂在 AdminLayout 下（侧边栏）
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { recordPv } from '../api/front'

import FrontLayout from '../layouts/FrontLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'

// 前台页面
import Home from '../views/front/Home.vue'
import PostDetail from '../views/front/PostDetail.vue'
import Category from '../views/front/Category.vue'
import Tag from '../views/front/Tag.vue'
import Archive from '../views/front/Archive.vue'
import Search from '../views/front/Search.vue'
import Links from '../views/front/Links.vue'
import Message from '../views/front/Message.vue'
import About from '../views/front/About.vue'
import NotFound from '../views/front/NotFound.vue'

// 登录/注册
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'

// 后台页面
import Dashboard from '../views/admin/Dashboard.vue'
import PostList from '../views/admin/PostList.vue'
import PostEdit from '../views/admin/PostEdit.vue'
import CategoryList from '../views/admin/CategoryList.vue'
import TagList from '../views/admin/TagList.vue'
import CommentList from '../views/admin/CommentList.vue'
import LinkList from '../views/admin/LinkList.vue'
import Profile from '../views/admin/Profile.vue'

const routes = [
  {
    path: '/',
    component: FrontLayout,
    children: [
      { path: '', name: 'home', component: Home },
      { path: 'post/:slug', name: 'post-detail', component: PostDetail },
      { path: 'category/:slug', name: 'category', component: Category },
      { path: 'tag/:slug', name: 'tag', component: Tag },
      { path: 'archive', name: 'archive', component: Archive },
      { path: 'search', name: 'search', component: Search },
      { path: 'links', name: 'links', component: Links },
      { path: 'message', name: 'message', component: Message },
      { path: 'about', name: 'about', component: About },
    ],
  },
  { path: '/login', name: 'login', component: Login },
  { path: '/master', name: 'master-login', component: Login },
  { path: '/register', name: 'register', component: Register },
  { path: '/404', name: 'not-found', component: NotFound },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'admin-dashboard', component: Dashboard, meta: { title: '仪表盘', admin: true } },
      { path: 'posts', name: 'admin-posts', component: PostList, meta: { title: '文章管理', admin: true } },
      { path: 'posts/create', name: 'admin-post-create', component: PostEdit, meta: { title: '写文章', admin: true } },
      { path: 'posts/:id/edit', name: 'admin-post-edit', component: PostEdit, meta: { title: '编辑文章', admin: true } },
      { path: 'categories', name: 'admin-categories', component: CategoryList, meta: { title: '分类管理', admin: true } },
      { path: 'tags', name: 'admin-tags', component: TagList, meta: { title: '标签管理', admin: true } },
      { path: 'comments', name: 'admin-comments', component: CommentList, meta: { title: '评论管理', admin: true } },
      { path: 'links', name: 'admin-links', component: LinkList, meta: { title: '友链管理', admin: true } },
      { path: 'profile', name: 'admin-profile', component: Profile, meta: { title: '个人设置', admin: true } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/404' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 端口分流：5000 = 前台（公开浏览 + 普通用户登录/注册），5888 = 后台（管理员登录/管理）
const IS_ADMIN_PORT = window.location.port === '5888'
export { IS_ADMIN_PORT }

// 登录守卫
// - 5888 后台端口：除登录页外一律要求登录；仅管理员可进 /admin
// - 5000 前台端口：公开浏览；后台路由统一引导到 5888；已登录访问登录/注册页回首页
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  // 首次进入等待 /auth/me 恢复登录态，避免刷新后被误判为未登录踢回登录页
  if (!auth.loaded) await auth.getSession()

  if (IS_ADMIN_PORT) {
    if (to.name === 'master-login') {
      return auth.isAuthenticated ? (auth.isAdmin ? { path: '/admin' } : { path: '/' }) : undefined
    }
    if (to.name === 'register') return { path: '/master' }
    if (!auth.isAuthenticated) {
      return { name: 'master-login', query: { redirect: to.fullPath } }
    }
    if (to.matched.some((r) => r.meta.requiresAuth) && !auth.isAdmin) {
      // 非管理员登录了 5888 → 引导到前台注册/浏览
      return { path: '/' }
    }
    if (to.name === 'home') return { path: '/admin' }
    return undefined
  }

  // ── 前台端口 5000 ──
  if (to.name === 'login' || to.name === 'register') {
    if (auth.isAuthenticated) return { path: '/' }
    return undefined
  }
  if (to.name === 'master-login') {
    // 5000 上访问 /master → 引导到 5888 后台登录
    window.location.replace('http://localhost:5888/master')
    return false
  }
  if (to.matched.some((r) => r.meta.requiresAuth)) {
    // 后台路由（/admin/*）只在 5888 提供，前台端口一律引导过去
    window.location.replace(`http://localhost:5888${to.fullPath}`)
    return false
  }
  return undefined
})

// 路由切换后记录 PV（fire-and-forget）
router.afterEach(() => {
  recordPv()
})

export default router
