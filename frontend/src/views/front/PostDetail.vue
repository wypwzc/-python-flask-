<template>
  <div class="post-detail-page">
    <!-- 加载中 -->
    <div v-if="loading" class="detail-card">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 内容区 -->
    <template v-else-if="post">
      <el-row :gutter="20">
        <el-col :xs="24" :md="17">
          <article class="detail-card">
            <div class="detail-header">
              <h1 class="detail-title">{{ post.title }}</h1>
              <div class="detail-meta">
                <span v-if="post.category">
                  <router-link :to="{ name: 'category', params: { slug: post.category.slug } }">
                    <el-tag size="small" effect="plain">{{ post.category.name }}</el-tag>
                  </router-link>
                </span>
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDateTime(post.published_at, 'YYYY-MM-DD HH:mm') }}
                </span>
                <span class="meta-item">
                  <el-icon><View /></el-icon>
                  {{ post.views }} 阅读
                </span>
                <span class="meta-item">
                  <el-icon><Timer /></el-icon>
                  {{ minutes }} 分钟
                </span>
              </div>
            </div>

            <el-image
              v-if="post.cover_image"
              :src="post.cover_image"
              :preview-src-list="[post.cover_image]"
              fit="cover"
              class="detail-cover"
            />

            <div ref="contentRef" class="article-content" v-html="post.content_html"></div>

            <div class="detail-tags">
              <router-link
                v-for="tag in post.tags"
                :key="tag"
                :to="{ name: 'tag', params: { slug: tag } }"
                class="tag-cloud-item"
              >
                #{{ tag }}
              </router-link>
            </div>

            <div class="detail-actions">
              <el-button
                :type="liked ? 'danger' : 'primary'"
                :plain="!liked"
                round
                :loading="liking"
                @click="doLike"
              >
                <el-icon class="like-icon">
                  <StarFilled v-if="liked" />
                  <Star v-else />
                </el-icon>
                {{ liked ? '已点赞' : '点赞' }} {{ likes }}
              </el-button>
            </div>

            <!-- 上一篇/下一篇 -->
            <div class="prev-next">
              <router-link
                v-if="prevPost"
                :to="{ name: 'post-detail', params: { slug: prevPost.slug } }"
                class="prev-link"
              >
                <div class="pn-label">上一篇</div>
                <div class="pn-title">{{ prevPost.title }}</div>
              </router-link>
              <span v-else />
              <router-link
                v-if="nextPost"
                :to="{ name: 'post-detail', params: { slug: nextPost.slug } }"
                class="next-link"
              >
                <div class="pn-label">下一篇</div>
                <div class="pn-title">{{ nextPost.title }}</div>
              </router-link>
              <span v-else />
            </div>
          </article>

          <CommentList
            :post-id="post.id"
            :post-slug="post.slug"
            :allow-comment="post.allow_comment"
          />
        </el-col>

        <!-- 目录 -->
        <el-col :xs="24" :md="7">
          <aside v-if="toc.length" class="toc-card">
            <h4 class="toc-title">文章目录</h4>
            <ul class="toc-list">
              <li v-for="item in toc" :key="item.id">
                <a
                  :href="`#${item.id}`"
                  :class="{ active: activeTocId === item.id }"
                  :style="{ paddingLeft: (item.level - 1) * 12 + 'px' }"
                  @click.prevent="scrollToHeading(item.id)"
                >
                  {{ item.text }}
                </a>
              </li>
            </ul>
          </aside>

          <!-- 相关文章 -->
          <aside v-if="relatedPosts.length" class="toc-card">
            <h4 class="toc-title">相关文章</h4>
            <div class="related-list">
              <router-link
                v-for="p in relatedPosts"
                :key="p.id"
                :to="{ name: 'post-detail', params: { slug: p.slug } }"
                class="related-item"
              >
                {{ p.title }}
              </router-link>
            </div>
          </aside>
        </el-col>
      </el-row>
    </template>

    <el-empty v-else-if="!loading" description="文章不存在" />
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Calendar, View, Timer, Star, StarFilled } from '@element-plus/icons-vue'
import hljs from 'highlight.js'
import { getPost, likePost } from '../../api/front'
import { formatDateTime } from '../../utils/date'
import { wordCount } from '../../utils/text'
import CommentList from '../../components/CommentList.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const post = ref(null)
const prevPost = ref(null)
const nextPost = ref(null)
const relatedPosts = ref([])
const liked = ref(false)
const likes = ref(0)
const liking = ref(false)

const contentRef = ref()
const toc = ref([])
const activeTocId = ref('')

const minutes = computed(() => (post.value ? Math.max(1, Math.ceil(wordCount(post.value.content_html) / 300)) : 0))

async function load() {
  loading.value = true
  try {
    const { data } = await getPost(route.params.slug)
    post.value = data.post
    prevPost.value = data.prev_post
    nextPost.value = data.next_post
    relatedPosts.value = data.related_posts
    liked.value = data.is_liked
    likes.value = data.post.likes || 0

    document.title = `${data.post.title} - 个人博客`

    await nextTick()
    // 服务端渲染的代码块高亮
    contentRef.value?.querySelectorAll('pre code').forEach((el) => hljs.highlightElement(el))
    buildToc()
  } catch (e) {
    if (e?.response?.status === 404) {
      router.replace('/404')
    }
  } finally {
    loading.value = false
  }
}

/** 从 content_html 解析 h1-h3 构建目录（toc 扩展生成 id="_1" 形式） */
function buildToc() {
  const tmp = document.createElement('div')
  tmp.innerHTML = post.value.content_html || ''
  toc.value = [...tmp.querySelectorAll('h1,h2,h3')].map((el) => ({
    id: el.id,
    text: el.textContent.trim(),
    level: Number(el.tagName[1]),
  }))
}

function scrollToHeading(id) {
  activeTocId.value = id
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

/** 滚动监听：高亮当前章节 */
function onScroll() {
  if (!toc.value.length) return
  const offset = window.scrollY + 120
  let current = ''
  for (const item of toc.value) {
    const el = document.getElementById(item.id)
    if (el && el.offsetTop <= offset) current = item.id
  }
  activeTocId.value = current
}

async function doLike() {
  if (liking.value) return
  liking.value = true
  try {
    const { data } = await likePost(post.value.slug)
    likes.value = data.likes
    liked.value = data.liked
    if (!data.liked) ElMessage.warning(data.message || '您已经赞过了')
  } finally {
    liking.value = false
  }
}

onMounted(() => {
  load()
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.detail-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 24px;
  margin-bottom: 20px;
}

.detail-header {
  margin-bottom: 16px;
}

.detail-title {
  font-size: 1.7rem;
  font-weight: 700;
  margin: 0 0 12px;
  line-height: 1.4;
}

.detail-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.detail-cover {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 20px;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-color);
}

.detail-actions {
  text-align: center;
  margin-top: 24px;
}

.like-icon {
  margin-right: 4px;
}

.prev-next {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 28px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-color);
}

.prev-link,
.next-link {
  flex: 1;
  max-width: 48%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-primary);
  transition: box-shadow 0.2s;
}

.prev-link:hover,
.next-link:hover {
  box-shadow: var(--shadow);
  color: var(--text-primary);
}

.next-link {
  text-align: right;
}

.pn-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.pn-title {
  font-size: 0.92rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toc-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 16px;
  margin-bottom: 20px;
  position: sticky;
  top: 76px;
}

.toc-title {
  margin: 0 0 12px;
  font-size: 1rem;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.related-item {
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.related-item:hover {
  color: var(--link-color);
}

@media (max-width: 768px) {
  .detail-card {
    padding: 16px;
  }

  .detail-title {
    font-size: 1.4rem;
  }

  .toc-card {
    position: static;
  }
}
</style>
