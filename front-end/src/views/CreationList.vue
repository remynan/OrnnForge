<script lang="ts" setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import type { TableInstance, TabsPaneContext } from 'element-plus'
import {
  Delete,
  Edit,
  Share,
} from '@element-plus/icons-vue'
import { useForgeStore } from '@/stores/forgeStore'
import { CreationItem } from '@/types/common'

const forgeStore = useForgeStore()

const activeName = ref('all')

const { creations, showSource, totalCreations, currentPage, pageSize } = storeToRefs(forgeStore)

const handleClick = async(tab: TabsPaneContext, event: Event) => {
  console.log(tab, event)
  console.log(tab.paneName)
  if (tab.paneName === 'all') {
    showSource.value = ''
  } else {
    showSource.value = tab.paneName.toString()
  }
  console.log(showSource.value)
  await forgeStore.fetchCreations()
  console.log(creations.value)
}

const multipleTableRef = ref<TableInstance>()
const multipleSelection = ref<CreationItem[]>([])
const toggleSelection = (rows?: CreationItem[], ignoreSelectable?: boolean) => {
  if (rows) {
    rows.forEach((row) => {
      multipleTableRef.value!.toggleRowSelection(
        row,
        undefined,
        ignoreSelectable
      )
    })
  } else {
    multipleTableRef.value!.clearSelection()
  }
}
const handleSelectionChange = (val: CreationItem[]) => {
  multipleSelection.value = val
}


const handleEdit = (index: number, row: CreationItem) => {
  console.log(index, row)
}

const handleCurrentChange = async(val: number) => {
  console.log(`当前页: ${val}`)
  currentPage.value = val
  await forgeStore.fetchCreations()
}

const handleSizeChange = async(val: number) => {
  console.log(`每页 ${val} 条`)
  pageSize.value = val
  await forgeStore.fetchCreations()
}

const getSourceName = (source: string) => {
  switch (source) {
    case 'baidu':
      return '百度'
    case 'bilibili':
      return '哔哩哔哩'
    case 'douyin':
      return '抖音'
    case 'douban-group':
      return '豆瓣小组'
    case 'douban-movie':
      return '豆瓣电影'
    case 'hupu':
      return '虎扑'
    case 'sina':
      return '新浪'
    case 'tieba':
      return '贴吧'
    case 'toutiao':
      return '头条'
    case 'weibo':
      return '微博'
    case 'zhihu':
      return '知乎'
    case 'qq-news':
      return '腾讯新闻'
    case 'sina-news':
      return '新浪新闻'
    case 'netease-news':
      return '网易新闻'
    case 'thepaper':
      return '澎湃新闻'
    case 'zhihu-daily':
      return '知乎日报'
    default:
      return source
  }
}

const getStatusName = (status: number) => {
  switch (status) {
    case 0:
      return '待确认'
    case 1:
      return '已确认'
    case 2:
      return '生成中'
    case 3:
      return '可发布'
    case 4:
      return '已使用'
    default:
      return status
  }
}

</script>


<template>
  <el-tabs
    v-model="activeName"
    type="card"
    class="demo-tabs"
    @tab-click="handleClick"
  >
    <el-tab-pane label="全部" name="all"></el-tab-pane>
    <el-tab-pane label="百度" name="baidu"></el-tab-pane>
    <el-tab-pane label="哔哩哔哩" name="bilibili"></el-tab-pane>
    <el-tab-pane label="抖音" name="douyin"></el-tab-pane>
    <el-tab-pane label="豆瓣小组" name="douban-group"></el-tab-pane>
    <el-tab-pane label="豆瓣电影" name="douban-movie"></el-tab-pane>
    <el-tab-pane label="虎扑" name="hupu"></el-tab-pane>
    <el-tab-pane label="新浪" name="sina"></el-tab-pane>
    <el-tab-pane label="贴吧" name="tieba"></el-tab-pane>
    <el-tab-pane label="头条" name="toutiao"></el-tab-pane>
    <el-tab-pane label="微博" name="weibo" disabled></el-tab-pane>
    <el-tab-pane label="知乎" name="zhihu" disabled></el-tab-pane>
    <el-tab-pane label="腾讯新闻" name="qq-news"></el-tab-pane>
    <el-tab-pane label="新浪新闻" name="sina-news"></el-tab-pane>
    <el-tab-pane label="网易新闻" name="netease-news"></el-tab-pane>
    <el-tab-pane label="澎湃新闻" name="thepaper"></el-tab-pane>
    <el-tab-pane label="知乎日报" name="zhihu-daily"></el-tab-pane>
  </el-tabs>
  <div>
    <div style="display: flex; justify-content: space-between; padding: 10px;">
      <el-button-group class="ml-4">
        <el-button type="primary" :icon="Edit" />
        <el-button type="primary" :icon="Share" />
        <el-button type="primary" :icon="Delete" />
      </el-button-group>
      <span> {{ showSource }} </span>
      <el-button-group class="ml-4">
        <el-button type="primary" :icon="Edit" />
        <el-button type="primary" :icon="Share" />
        <el-button type="primary" :icon="Delete" />
      </el-button-group>
    </div>
    <el-table
      ref="multipleTableRef"
      :data="creations"
      border
      height="650" 
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="_id" label="ID" width="210" />
      <el-table-column prop="source" label="来源" width="100">
        <template #default="scope">
          <span>{{ getSourceName(scope.row.source) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="100">
        <template #default="scope">
          <span>{{ getStatusName(scope.row.status) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="缩略图" width="125">
        <template #default="scope">
          <template v-if="scope.row.cover == null">
            <el-image style="width: 100px; height: 100px" src="" fit="fill" />
          </template>
          <template v-else>
            <el-image style="width: 100px; height: 100px" :src="getSourceName(scope.row.cover)" fit="fill" />
          </template>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" width="300" show-overflow-tooltip />
      <el-table-column prop="desc" label="描述" show-overflow-tooltip />
      <el-table-column prop="url" label="原帖地址" width="100">
        <template #default="scope">
          <el-button size="small" type="success" plain @click="handleEdit(scope.$index, scope.row)">
            打开
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="totalCreations"
      :page-sizes="[10, 20, 50, 100]"
      layout="prev, pager, next, jumper, sizes"
      size="small"
      background
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>