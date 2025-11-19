import { defineConfig } from 'vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Icons from "unplugin-icons/vite";
import IconsResolver from "unplugin-icons/resolver";
import UnoCSS from "unocss/vite";
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { viteCommonjs } from '@originjs/vite-plugin-commonjs'
import vue from '@vitejs/plugin-vue'
import path from "path"
const pathSrc = path.resolve(__dirname, "src")

// https://vite.dev/config/
export default defineConfig({
  base: '/web',
  plugins: [
    vue(),
    viteCommonjs(),
    UnoCSS({}),
    AutoImport({
      // 自动导入 Vue 相关函数，如：ref, reactive, toRef 等
      imports: ["vue", "@vueuse/core"],
      eslintrc: {
        enabled: false,
        filepath: "./.eslintrc-auto-import.json",
        globalsPropValue: true,
      },
      resolvers: [
        // 自动导入 Element Plus 相关函数，如：ElMessage, ElMessageBox... (带样式)
        ElementPlusResolver(),
        IconsResolver({
          prefix: 'Icon',
        }),
      ],
      vueTemplate: true,
      // 配置文件生成位置(false:关闭自动生成)
      dts: false,
      // dts: "src/types/auto-imports.d.ts",
    }),
  ],
  resolve: {
    alias: {
      "@": pathSrc,
    },
  },
  server: {
    host: "0.0.0.0",
    open: false, // 运行是否自动打开浏览器
    proxy: {
      '/api/': {
        target: 'http://127.0.0.1:8000/',
        changeOrigin: true,
        rewrite: (path) =>
          path.replace(new RegExp("^/api/"), ""), // 替换 /dev-api 为 target 接口地址
      },
    },
  },
})
