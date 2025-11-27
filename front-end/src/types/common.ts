
export interface CreationsTable {
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
  formForGenerate: FormForGenerate;
  result: ResultForGenerate[];
  del_flag: boolean;
}

export interface FormForGenerate {
  html: string;
  type: string;
  idea: string;
}

export interface ResultForGenerate {
  to: string;
  content: string;
}