import apiClient from './client'
import type { Repository, CreateRepositoryRequest, TreeNode, DocumentContent, SearchResponse } from '../types'

// Repository APIs
export const getRepositories = async (): Promise<Repository[]> => {
  const response = await apiClient.get('/repositories')
  return response.data
}

export const getRepository = async (id: number): Promise<Repository> => {
  const response = await apiClient.get(`/repositories/${id}`)
  return response.data
}

export const createRepository = async (data: CreateRepositoryRequest): Promise<Repository> => {
  const response = await apiClient.post('/repositories', data)
  return response.data
}

export const deleteRepository = async (id: number): Promise<void> => {
  await apiClient.delete(`/repositories/${id}`)
}

export const refreshRepository = async (id: number): Promise<Repository> => {
  const response = await apiClient.post(`/repositories/${id}/refresh`)
  return response.data
}

// Document APIs
export const getDocumentTree = async (repoId: number): Promise<TreeNode[]> => {
  const response = await apiClient.get(`/repositories/${repoId}/tree`)
  return response.data
}

export const getDocumentContent = async (repoId: number, filepath: string): Promise<DocumentContent> => {
  const response = await apiClient.get(`/repositories/${repoId}/documents`, {
    params: { filepath }
  })
  return response.data
}

// Search API
export const searchDocuments = async (query: string, repoId?: number): Promise<SearchResponse> => {
  const response = await apiClient.get('/search', {
    params: { q: query, repo_id: repoId }
  })
  return response.data
}

// Export APIs
export const exportDocument = async (repoId: number, filepath: string): Promise<Blob> => {
  const response = await apiClient.get(`/repositories/${repoId}/export`, {
    params: { filepath },
    responseType: 'blob'
  })
  return response.data
}

export const exportRepository = async (repoId: number): Promise<Blob> => {
  const response = await apiClient.get(`/repositories/${repoId}/export-all`, {
    responseType: 'blob'
  })
  return response.data
}
