import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { forgeApi } from '@/api';
import { CreationItem } from '@/types/common';

export const useForgeStore = defineStore('forge', () => {
  // 状态
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentPage = ref(1);
  const pageSize = ref(10);
  const totalCreations = ref(0);
  const showSource = ref('');
  const showCreationStatus = ref(0);
  const creations = ref([] as CreationItem[]);

  // Getter
  const totalPages = computed(() => Math.ceil(totalCreations.value / pageSize.value));

  // Actions
  const fetchCreations = async() => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await forgeApi.getCreations(showCreationStatus.value, showSource.value, currentPage.value, pageSize.value);
      
      if (response.code === 200) {
        console.log('ResponseData:', response.data);
        creations.value = response.data.items;
        totalCreations.value = response.data.total;
        currentPage.value = response.data.page;
        pageSize.value = response.data.size;
      } else {
        throw new Error(response.message);
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取视频列表失败';
      console.error('Failed to fetch videos:', err);
    } finally {
      loading.value = false;
    }
  };

  return {
    // State
    loading,
    error,
    currentPage,
    pageSize,
    totalCreations,
    showSource,
    showCreationStatus,
    creations,
    
    // Getters
    totalPages,
    
    // Actions
    fetchCreations,
  };
});
