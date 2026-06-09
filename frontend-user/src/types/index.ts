// Repository types
export interface Repository {
  id: number
  name: string
  url: string
  description: string | null
  local_path: string
  branch: string
  status: 'pending' | 'cloning' | 'ready' | 'error'
  error_message: string | null
  doc_count: number
  created_at: string
  updated_at: string
}

export interface CreateRepositoryRequest {
  url: string
  branch?: string
}

// Document types
export interface Document {
  id: number
  repository_id: number
  filename: string
  filepath: string
  extension: string
  title: string | null
  size: number
  is_indexed: boolean
  created_at: string
  updated_at: string
}

export interface DocumentContent {
  document: Document
  content: string
}

// File tree types
export interface TreeNode {
  name: string
  path: string
  type: 'file' | 'directory'
  extension?: string
  children?: TreeNode[]
}

// Search types
export interface SearchResult {
  document: Document
  repository: Repository
  highlights: string[]
  score: number
}

export interface SearchResponse {
  query: string
  total: number
  results: SearchResult[]
}

// Reading progress types
export interface ReadingProgress {
  id: number
  session_id: string
  repository_id: number
  filepath: string
  scroll_position: number
  last_read_at: string
}

// API response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface ApiError {
  detail: string
}
