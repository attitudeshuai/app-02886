import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { FolderGit2, Plus, RefreshCw, Trash2, Loader2 } from 'lucide-react'
import { getRepositories, createRepository, deleteRepository, refreshRepository } from '../api/repositories'
import type { Repository } from '../types'
import AddRepoModal from './AddRepoModal'

export default function Sidebar() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const { repoId } = useParams()

  const fetchRepos = async () => {
    try {
      const data = await getRepositories()
      setRepos(data)
    } catch (error) {
      console.error('Failed to fetch repositories:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRepos()
  }, [])

  const handleAddRepo = async (url: string) => {
    try {
      await createRepository({ url })
      await fetchRepos()
      setShowAddModal(false)
    } catch (error) {
      console.error('Failed to add repository:', error)
      throw error
    }
  }

  const handleDeleteRepo = async (id: number, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (confirm('确定要删除这个仓库吗？')) {
      try {
        await deleteRepository(id)
        await fetchRepos()
      } catch (error) {
        console.error('Failed to delete repository:', error)
      }
    }
  }

  const handleRefreshRepo = async (id: number, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    try {
      await refreshRepository(id)
      await fetchRepos()
    } catch (error) {
      console.error('Failed to refresh repository:', error)
    }
  }

  return (
    <>
      <aside className="w-[280px] bg-surface border-r border-border h-[calc(100vh-56px)] sticky top-14 overflow-y-auto hidden lg:block">
        {/* Header */}
        <div className="p-4 border-b border-divider">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-text-muted uppercase tracking-wider">仓库列表</span>
            <button
              onClick={() => setShowAddModal(true)}
              className="p-1.5 text-text-secondary hover:text-accent hover:bg-accent-light rounded-md transition-colors"
              title="添加仓库"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Repository list */}
        <div className="py-2">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-5 h-5 text-text-muted animate-spin" />
            </div>
          ) : repos.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <FolderGit2 className="w-10 h-10 text-text-muted mx-auto mb-3" />
              <p className="text-sm text-text-muted">暂无仓库</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="mt-3 text-sm text-accent hover:underline"
              >
                添加第一个仓库
              </button>
            </div>
          ) : (
            repos.map((repo) => (
              <Link
                key={repo.id}
                to={`/repo/${repo.id}`}
                className={`group flex items-center gap-3 px-4 py-3 hover:bg-background transition-colors ${
                  Number(repoId) === repo.id ? 'bg-accent-light border-l-[3px] border-accent' : ''
                }`}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  Number(repoId) === repo.id ? 'bg-accent/10' : 'bg-surface-alt'
                }`}>
                  <FolderGit2 className={`w-5 h-5 ${
                    Number(repoId) === repo.id ? 'text-accent' : 'text-text-muted'
                  }`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-text-primary truncate">{repo.name}</div>
                  <div className="text-xs text-text-muted truncate">
                    {repo.status === 'ready' ? `${repo.doc_count} 个文档` : getStatusText(repo.status)}
                  </div>
                </div>
                {/* Actions */}
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => handleRefreshRepo(repo.id, e)}
                    className="p-1 text-text-muted hover:text-accent rounded"
                    title="刷新"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => handleDeleteRepo(repo.id, e)}
                    className="p-1 text-text-muted hover:text-error rounded"
                    title="删除"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </Link>
            ))
          )}
        </div>
      </aside>

      {/* Add Repository Modal */}
      <AddRepoModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddRepo}
      />
    </>
  )
}

function getStatusText(status: string): string {
  switch (status) {
    case 'pending': return '等待中...'
    case 'cloning': return '克隆中...'
    case 'error': return '错误'
    default: return status
  }
}
