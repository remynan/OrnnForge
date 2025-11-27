import axios from 'axios';
import type {
  ApiResponse,
} from '@/types/api';
import { CreationsTable, CreationItem, FormForGenerate } from '@/types/common';

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
  async getCreations(status: number = 0, source: string = '', page: number = 1, size: number = 10): Promise<ApiResponse<CreationsTable>> {
    try {
      let requestUrl = `/items?page=${page}&size=${size}&status=${status}`;
      if (source !== '') {
        requestUrl += `&source=${source}`;
      }
      const response = await apiClient.get<ApiResponse<CreationsTable>>(requestUrl);
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

  async getCreationGenerateInfo(creation_id: string): Promise<ApiResponse<CreationItem>> {
    try {
      const response = await apiClient.get<ApiResponse<CreationItem>>(`/creations/${creation_id}/info`);
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

  async getCreationGenerateForm(creation_id: string): Promise<ApiResponse<CreationItem>> {
    try {
      const response = await apiClient.get<ApiResponse<CreationItem>>(`/creations/${creation_id}/generate_form`);
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
  
  async submitCreationGenerate(creation_id: string, form: FormForGenerate): Promise<ApiResponse<null>> {
    try {
      const response = await apiClient.put<ApiResponse<null>>(
        `/creations/generate_form`, 
        {
          id: creation_id,
          form: form
        }
      );
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
  
  async cannelCreationGenerate(creation_id: string): Promise<ApiResponse<null>> {
    try {
      const response = await apiClient.put<ApiResponse<null>>(
        `/creations/cannel_generate`, 
        {
          id: creation_id
        }
      );
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

  async batchFinishCreation(creation_ids: string[]): Promise<ApiResponse<null>> { 
    try {
      const response = await apiClient.put<ApiResponse<null>>(
        `/creations/batch_finish`, 
        {
          ids: creation_ids
        }
      );
      if (response.status === 200) {
        console.log('ResponseData:', response.data);
        return response.data;
      } else {
        throw new Error('请求失败.');
      }
    } catch (error) {
      throw new Error(`操作失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  async batchDeleteCreation(creation_ids: string[]): Promise<ApiResponse<null>> { 
    try {
      const response = await apiClient.put<ApiResponse<null>>(
        `/creations/batch_delete`, 
        {
          ids: creation_ids
        }
      );
      if (response.status === 200) {
        console.log('ResponseData:', response.data);
        return response.data;
      } else {
        throw new Error('请求失败.');
      }
    } catch (error) {
      throw new Error(`删除失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

}

export const forgeApi = new ForgeApi();