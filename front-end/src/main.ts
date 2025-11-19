import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'
import axios from 'axios';
import router from './router'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 设置全局axios配置（可选）
axios.defaults.baseURL = '/api';
axios.defaults.timeout = 10000;

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { 
  // size: 'small', 
  zIndex: 3000 
})

app.mount('#app')