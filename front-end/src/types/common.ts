
export interface CreationData {
  items: CreationItem[];
  total: number;
  page: number;
  size: number;
}

export interface CreationItem {
  _id: string;
  source: string;
  top_id: string;
  title: string;
  cover: string;
  desc: string;
  author: string | null;
  timestamp: string;
  hot: number | null;
  url: string;
  mobileUrl: string;
  create_time: string;
  status: number;
  del_flag: boolean;
}