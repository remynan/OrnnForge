
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface ApiError {
  code: number;
  message: string;
  details?: any;
}