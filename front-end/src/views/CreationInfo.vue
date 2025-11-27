<script lang="ts" setup>
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { handleError, onMounted, reactive, ref } from 'vue'
import { CreationItem, ResultForGenerate } from '@/types/common'
import { getSourceName, getStatusName } from '@/utils'
import { forgeApi } from '@/api'
import { ApiResponse } from '@/types/api'
import { useRoute } from 'vue-router'

const route = useRoute()

const creation_id = ref(route.params.id as string)

const activeTabName = ref('base')

const activeResultTabName = ref('none')

const md = new MarkdownIt({
  html: true,        // 允许 HTML 标签
  breaks: true,      // 转换换行符为 <br>
  linkify: true,     // 自动链接 URL
  typographer: true  // 一些语言替换
})

const renderMarkdown = (content: string | undefined): string => {
  if (!content) return ''
  
  const rawHtml = md.render(content)
  // 安全过滤
  return DOMPurify.sanitize(rawHtml)
}


const info = reactive({
  id: '',
  title: '',
  cover: '',
  source: '',
  author: '',
  timestamp: '',
  status: 0,
  hot: 0,
  desc: '',
  url: '',
  mobileUrl: '',
  type: '',
  html: '',
  idea: ''
})

const infoResult = ref<ResultForGenerate[]>([])

onMounted(async() => {

  console.log('creation_id', creation_id.value)
  await forgeApi.getCreationGenerateInfo(creation_id.value).then(res => {
    if (res.code === 200) { 
      info.id = res.data._id
      info.title = res.data.title
      info.cover = res.data.cover
      info.source = res.data.source
      info.author = res.data.author
      info.hot = res.data.hot
      info.desc = res.data.desc
      info.url = res.data.url
      info.mobileUrl = res.data.mobileUrl
      infoResult.value = res.data.result
      if (infoResult.value.length > 0) {
        activeResultTabName.value = infoResult.value[0].to
      } else {
        activeResultTabName.value = 'none'
      }
    }
  })
})

</script>

<template>
  <el-tabs
    v-model="activeTabName"
    type="card"
    class="demo-tabs"
  >
    <el-tab-pane label="作品信息" name="base">
      <div style="display: flex; justify-content: center;">
        <div>
          <el-image style="width: 350px; height: 350px" :src="info.cover" fit="fill" />
        </div>
        <div style="padding: 0px 20px;">
          <el-form :model="info" label-width="auto" style="max-width: 600px">
            <el-form-item label="状态">
              <el-text class="mx-1">{{getStatusName(info.status)}}</el-text>
            </el-form-item>
            <el-form-item label="来源平台">
              <el-text class="mx-1">{{getSourceName(info.source)}}</el-text>
            </el-form-item>
            <el-form-item label="标题">
              <el-text class="mx-1">{{info.title}}</el-text>
            </el-form-item>
            <el-form-item label="原帖">
              <el-link type="primary" :href="info.url" target="_blank">PC端网页</el-link>
              <span style="width: 20px;"> &nbsp;</span>
              <el-link type="primary" :href="info.mobileUrl" target="_blank">移动端网页</el-link>
            </el-form-item>
            <el-form-item label="热度">
              <el-text class="mx-1">{{info.hot}}</el-text>
            </el-form-item>
            <el-form-item label="作者">
              <el-text v-if="info.author" class="mx-1">{{info.author}}</el-text>
              <el-text v-else class="mx-1"> - </el-text>
            </el-form-item>
            <el-form-item label="发布时间">
              <el-text v-if="info.timestamp" class="mx-1">{{info.timestamp}}</el-text>
              <el-text v-else class="mx-1"> - </el-text>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <div style="padding: 20px 50px;">
        <el-form :model="info" label-width="auto">
          <el-form-item label="作品描述">
            <el-text class="mx-1">{{info.desc}}</el-text>
          </el-form-item>
        </el-form>
      </div>
    </el-tab-pane>
    <el-tab-pane v-if="infoResult.length > 0" label="发布内容" name="result">
      <el-tabs v-model="activeResultTabName" tab-position="left">
        <template v-for="(item, index) in infoResult" :key="item.to"> 
          <el-tab-pane :label="getSourceName(item.to)" :name="item.to">
            <div style="max-height: 700px; overflow-y: auto; margin: 0px 20px; background-color: white; border: 1px solid #ddd; border-radius: 15px; padding: 10px 20px;">
              <div class="markdown-content" v-html="renderMarkdown(item.content)" />
            </div>
          </el-tab-pane>
        </template>
      </el-tabs>
    </el-tab-pane>
  </el-tabs>
</template>


<style scoped>
.markdown-content {
  line-height: 1.6;
  text-align: start;
}

.markdown-content :deep(h1) {
  font-size: 1.5em;
  margin: 16px 0 8px 0;
  font-weight: bold;
}

.markdown-content :deep(h2) {
  font-size: 1.3em;
  margin: 14px 0 7px 0;
  font-weight: bold;
}

.markdown-content :deep(h3) {
  font-size: 1.1em;
  margin: 12px 0 6px 0;
  font-weight: bold;
}

.markdown-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.markdown-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 12px;
  margin: 8px 0;
  color: #666;
}

.markdown-content :deep(ul) {
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
}
</style>