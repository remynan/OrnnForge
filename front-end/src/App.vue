<script lang="ts" setup>
import { handleError, onMounted } from 'vue'
import { useForgeStore } from '@/stores/forgeStore'
import { storeToRefs } from 'pinia'

const forgeStore = useForgeStore()

const { showCreationStatus } = storeToRefs(forgeStore)

const handleRaidoGroupChange = async(val: number) => {
  showCreationStatus.value = val
  await forgeStore.fetchCreations()
}

// 应用启动时的初始化逻辑
onMounted(async() => {
  // 这里可以加载应用设置、用户设置等
  await forgeStore.fetchCreations()
})
</script>

<template>
  <div id="app">
    <!-- 应用头部（可选） -->
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <span class="title-main">OrnnForge</span>
          <span class="title-sub">数字内容创作的熔炉</span>
        </h1>
        <div>
          <el-radio-group
            v-model="showCreationStatus"
            text-color="#626aef"
            fill="rgb(239, 240, 253)"
            @change="handleRaidoGroupChange"
          >
            <el-radio-button label="未确认" :value="0" />
            <el-radio-button label="已确认" :value="1" />
            <el-radio-button label="生成中" :value="2" />
            <el-radio-button label="可发布" :value="3" />
            <el-radio-button label="已使用" :value="4" />
          </el-radio-group>
        </div>
        <div class="header-actions">
          <!-- 这里可以添加用户菜单、设置按钮等 -->
          <el-button text>
            <el-icon><User /></el-icon>
            用户
          </el-button>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="app-main">
      <router-view />
    </main>

    <!-- 全局消息显示位置 -->
    <div id="global-message-container"></div>
  </div>
</template>

<style scoped>
#app {
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  /* z-index: 1000; */
  width: 100%;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0px 40px;
  height: 70px;
}

.app-title {
  margin: 0;
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.title-main {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.title-sub {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.header-actions .el-button) {
  color: white;
}

:deep(.header-actions .el-button:hover) {
  background: rgba(255, 255, 255, 0.1);
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 70px);
  padding: 20px;
}

.app-main.no-header {
  padding: 0;
}

.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 12px 16px;
  }
  
  .title-main {
    font-size: 20px;
  }
  
  .title-sub {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .app-title {
    flex-direction: column;
  }
  
  .header-content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}

/* 全局滚动条样式 */
:deep(::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
}

/* 全局元素样式重置 */
:deep(.el-pagination) {
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-card) {
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

:deep(.el-button) {
  border-radius: 6px;
}
</style>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 路由切换时的平滑过渡效果 */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 自定义Element Plus主题变量 */
:root {
  --el-color-primary: #409eff;
  --el-color-success: #67c23a;
  --el-color-warning: #e6a23c;
  --el-color-danger: #f56c6c;
  --el-color-info: #909399;
}
</style>