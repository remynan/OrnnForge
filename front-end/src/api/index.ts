import axios from 'axios';
import type {
  ApiResponse,
} from '@/types/api';
import { CreationData } from '@/types/common';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: '/api', // 根据后端实际API路径调整
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    console.log(`Making API request to: ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API request failed:', error);
    
    if (error.response) {
      // 服务器返回了错误状态码
      const message = error.response.data?.message || `服务器错误: ${error.response.status}`;
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // 请求发送但没有收到响应
      return Promise.reject(new Error('网络连接失败，请检查网络连接'));
    } else {
      // 其他错误
      return Promise.reject(new Error('请求配置错误'));
    }
  }
);

class ForgeApi {
  // 获取搜索条件选项
  async getCreations(status: number = 0, source: string = '', page: number = 1, size: number = 10): Promise<ApiResponse<CreationData>> {
    try {
      let requestUrl = `/items?page=${page}&size=${size}&status=${status}`;
      if (source !== '') {
        requestUrl += `&source=${source}`;
      }
      const response = await apiClient.get<ApiResponse<CreationData>>(requestUrl);
      if (response.status === 200) {
        console.log('ResponseData:', response.data);
        return response.data;
      } else {
        throw new Error('请求失败.');
      }
    } catch (error) {
      throw new Error(`获取作品列表失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }
}

export const forgeApi = new ForgeApi();