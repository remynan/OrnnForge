<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessageBox, ElNotification, type TableInstance, type TabsPaneContext } from 'element-plus'
import {
  Delete,
  Share,
} from '@element-plus/icons-vue'
import GenerateFormDrawer from '@/components/GenerateFormDrawer.vue'
import { useForgeStore } from '@/stores/forgeStore'
import { CreationItem } from '@/types/common'
import { getSourceName, getStatusName, visitUrlAtBlank } from '@/utils'
import { forgeApi } from '@/api'
import { ApiResponse } from '@/types/api'

const forgeStore = useForgeStore()

const activeName = ref('all')

const setRow = ref(null as CreationItem)
const isNextVisible = ref(false)

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

const handleBatchDeleteButtonClick = async() => {
  const ids = multipleSelection.value.map((item) => item._id)
  console.log(ids)
  await forgeApi.batchDeleteCreation(ids).then(
    async(res: ApiResponse<null>) => {
    if (res.code === 200) {
      ElNotification.success('已删除')
      await forgeStore.fetchCreations()
    }
    }
  )
}

const handleBatchFinishButtonClick = async() => {
  const ids = multipleSelection.value.map((item) => item._id)
  console.log(ids)
  await forgeApi.batchFinishCreation(ids).then(
    async(res: ApiResponse<null>) => {
    if (res.code === 200) {
      ElNotification.success('已标记为已使用')
      await forgeStore.fetchCreations()
    }
    }
  )
}

const handleRowDoubleClick = (row: CreationItem) => {
  visitUrlAtBlank(`/web/creation/${row._id}`)
}

const handleNextVisible = (row: CreationItem) => {
  setRow.value = row
  isNextVisible.value = true
}
const handleCancelGenerate = async(creation_id: string) => {
  await forgeApi.cannelCreationGenerate(creation_id).then(
    async(res: ApiResponse<null>) => {
    if (res.code === 200) {
      ElNotification.success('已取消')
      await forgeStore.fetchCreations()
    } else { 
      ElMessageBox.alert('取消失败', '提示', {
        confirmButtonText: '确定',
      })
    }
    await forgeStore.fetchCreations()
  })
}

const handleCloseNextVisible = () => {
  setRow.value = null
  isNextVisible.value = false
  console.log('关闭了');
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


// 应用启动时的初始化逻辑
onMounted(async() => {
  // 这里可以加载应用设置、用户设置等
  await forgeStore.fetchCreations()
})

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
    <el-tab-pane label="微博（失效）" name="weibo"></el-tab-pane>
    <el-tab-pane label="知乎（失效）" name="zhihu"></el-tab-pane>
    <el-tab-pane label="腾讯新闻" name="qq-news"></el-tab-pane>
    <el-tab-pane label="新浪新闻" name="sina-news"></el-tab-pane>
    <el-tab-pane label="网易新闻" name="netease-news"></el-tab-pane>
    <el-tab-pane label="澎湃新闻" name="thepaper"></el-tab-pane>
    <el-tab-pane label="知乎日报" name="zhihu-daily"></el-tab-pane>
  </el-tabs>
  <div>
    <div style="display: flex; justify-content: space-between; padding: 10px;">
      <el-button-group class="ml-4">
        <!-- <el-button type="primary" :icon="Edit"> 编辑</el-button> -->
        <el-button type="primary" :icon="Delete" @click="handleBatchDeleteButtonClick"> 删除 </el-button>
        <el-button type="primary" :icon="Delete" @click="handleBatchFinishButtonClick"> 完成 </el-button>
      </el-button-group>
      <span> {{ showSource }} </span>
      <el-button-group class="ml-4">
        <el-button type="primary" :icon="Share" />
      </el-button-group>
    </div>
    <el-table
      ref="multipleTableRef"
      :data="creations"
      border
      max-height="650"
      style="width: 100%"
      @selection-change="handleSelectionChange"
      @row-dblclick="handleRowDoubleClick"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="source" label="来源" width="100">
        <template #default="scope">
          <span>{{ getSourceName(scope.row.source) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="状态" width="80">
        <template #default="scope">
          <span>{{ getStatusName(scope.row.status) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="缩略图" width="80">
        <template #default="scope">
          <template v-if="scope.row.cover == null">
            <span>无</span>
          </template>
          <template v-else>
            <el-popover placement="top">
              <template #reference>
                <el-text>预览</el-text>
              </template>
              <el-image style="width: 100px; height: 100px" :src="scope.row.cover" fit="fill" />
            </el-popover>
          </template>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" width="300" show-overflow-tooltip />
      <el-table-column prop="desc" label="描述" show-overflow-tooltip />
      <el-table-column prop="hot" label="热度" width="100" />
      <el-table-column prop="timestamp" label="发布时间" width="200" />
      <el-table-column prop="create_time" label="收录时间" width="200" />
      <el-table-column label="原帖" width="100">
        <template #default="scope">
          <el-button size="small" plain @click="visitUrlAtBlank(scope.row.url)">
            打开
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <template v-if="scope.row.status == 1"> 
            <el-button size="small" plain @click="handleCancelGenerate(scope.row._id)"> 取消生成 </el-button>
          </template>
          <template v-else> 
            <el-button size="small" plain @click="handleNextVisible(scope.row)">
              <span v-if="scope.row.status === 0">提交生成</span>
              <span v-else>重新生成</span>
            </el-button>
          </template>
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
  <template v-if="isNextVisible">
    <GenerateFormDrawer v-if="setRow.status === 0" :visible="isNextVisible" :creation_id="setRow._id" @close="handleCloseNextVisible" />
    <GenerateFormDrawer v-if="setRow.status === 2" :visible="isNextVisible" :creation_id="setRow._id" @close="handleCloseNextVisible" />
    <GenerateFormDrawer v-if="setRow.status === 3" :visible="isNextVisible" :creation_id="setRow._id" @close="handleCloseNextVisible" />
  </template>
</template>