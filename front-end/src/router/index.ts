import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/web/creations',
    name: 'creation-list',
    component: () => import('@/views/CreationList.vue'),
    meta: {
      title: '作品列表'
    }
  },
  {
    path: '/web/creation/:id',
    name: 'creation-info',
    component: () => import('@/views/CreationInfo.vue'),
    meta: {
      title: '作品内容'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/web/creations'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ルートガード - ページタイトル更新
router.beforeEach((to) => {
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
})

export default router