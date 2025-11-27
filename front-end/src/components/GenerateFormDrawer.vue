<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessageBox, ElNotification } from 'element-plus'
import { useForgeStore } from '@/stores/forgeStore'
import { CreationItem } from '@/types/common'
import { getSourceName } from '@/utils'
import { forgeApi } from '@/api'
import { ApiResponse } from '@/types/api'

const forgeStore = useForgeStore()

const props = defineProps<
{ 
  visible: boolean,
  creation_id: string
}>()

const emits = defineEmits<{
  (e: 'close'): void
}>()

const isDrawerVisible = ref(props.visible)

const { creations, showSource, totalCreations, currentPage, pageSize } = storeToRefs(forgeStore)

// do not use same name with ref
const form = reactive({
  id: props.creation_id,
  title: '',
  source: '',
  author: '',
  url: '',
  mobileUrl: '',
  type: '',
  html: '',
  idea: '',
})

const resetForm = () => {
  form.id = ''
  form.title = ''
  form.source = ''
  form.author = ''
  form.type = ''
  form.html = ''
  form.idea = ''
}

const onSubmit = async() => {
  if (!form.type) {
    ElMessageBox.alert('请选择类型', '提示', {
      confirmButtonText: '确定',
    })
    return
  }
  if (!form.html || form.html.trim() === '') {
    form.html = ''
  }
  if (!form.idea || form.idea.trim() === '') {
    form.idea = ''
  }
  await forgeApi.submitCreationGenerate(
    form.id,
    {
      type: form.type,
      html: form.html,
      idea: form.idea,
    }
  ).then(async(res: ApiResponse<null>) => {
    if (res.code === 200) { 
      ElNotification.success('提交成功')
      await forgeStore.fetchCreations()
      onCancel()
    } else { 
      ElMessageBox.alert('提交失败', '提示', {
        confirmButtonText: '确定',
      })
    }
  })
  console.log('submit!')
}

const handleBeforeClose = (done) => {
  ElMessageBox.confirm('确定要关闭抽屉吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    onCancel()
    done() // 调用 done 来关闭抽屉
  }).catch(() => {
    // 取消关闭，不调用 done
  })
}

const onCancel = () => {
  emits('close')
  isDrawerVisible.value = false
  resetForm()
}

onMounted(async() => {

  await forgeApi.getCreationGenerateForm(props.creation_id).then(res => {
    if (res.code === 200) { 
      form.id = res.data._id
      form.title = res.data.title
      form.source = res.data.source
      form.author = res.data.author
      form.url = res.data.url
      form.mobileUrl = res.data.mobileUrl
      form.type = res.data.formForGenerate.type
      form.html = res.data.formForGenerate.html
      form.idea = res.data.formForGenerate.idea
    } else { 
      onCancel()
    }
  })
})

</script>

<template>
  <el-drawer
    v-model="isDrawerVisible"
    title="作品内容生成 - 提供信息"
    direction="rtl"
    size="30%"
    :before-close="handleBeforeClose"
  >
    <el-form :model="form" label-width="auto" style="max-width: 600px">
      <el-form-item label="标题">
        <el-text class="mx-1">{{form.title}}</el-text>
      </el-form-item>
      <el-form-item label="来源平台">
        <el-text class="mx-1">{{getSourceName(form.source)}}</el-text>
      </el-form-item>
      <el-form-item label="作者">
        <el-text v-if="form.author" class="mx-1">{{form.author}}</el-text>
        <el-text v-else class="mx-1"> 未记录 </el-text>
      </el-form-item>
      <el-form-item label="原帖">
        <el-link type="primary" :href="form.url" target="_blank">新标签页打开</el-link>
      </el-form-item>
      <el-form-item label="原帖移动端">
        <el-link type="primary" :href="form.mobileUrl" target="_blank">新标签页打开</el-link>
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="form.type" placeholder="请选择当前作品的类型">
          <el-option label="图文分享" value="tuwen" />
          <el-option label="图文讨论帖" value="tuwen-tiezi" />
          <el-option label="视频分享" value="video" />
          <el-option label="视频讨论帖" value="video-tiezi" />
          <el-option label="资料页" value="info-page" />
        </el-select>
      </el-form-item>
      <el-form-item label="原帖HTML内容">
        <el-input v-model="form.html" type="textarea" :rows="5" />
      </el-form-item>
      <el-form-item label="额外的生成想法">
        <el-input v-model="form.idea" type="textarea" :autosize="{minRows: 2, maxRows: 10}" />
      </el-form-item>
      <div style="display: flex; justify-content: center; padding: 20px;">
        <el-button type="primary" @click="onSubmit">提交</el-button>
        <el-button @click="onCancel">取消</el-button>
      </div>
    </el-form>
  </el-drawer>
</template>