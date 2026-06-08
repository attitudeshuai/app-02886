import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FileText, Folder, ChevronRight, Download, Loader2, RefreshCw } from 'lucide-react'
import { getRepository, getDocumentTree, exportRepository } from '../api/repositories'
import type { Repository, TreeNode } from '../types'
import { saveAs } from 'file-saver'

export default function RepoPage() {
  const { repoId } = useParams<{ repoId: string }>()
  const [repo, setRepo] = useState<Repository | null>(null)
  const [tree, setTree] = useState<TreeNode[]>([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  const fetchData = useCallback(async () => {
    if (!repoId) return
    setLoading(true)
    try {
      const repoData = await getRepository(Number(repoId))
      setRepo(repoData)
      
      // 只有当仓库状态为 ready 时才获取文档树
      if (repoData.status === 'ready') {
        const treeData = await getDocumentTree(Number(repoId))
        setTree(treeData)
      } else {
        setTree([])
      }
    } catch (error) {
      console.error('Failed to fetch repository:', error)
    } finally {
      setLoading(false)
    }
  }, [repoId])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // 自动轮询：当仓库正在克隆时，每 3 秒刷新一次状态
  useEffect(() => {
    if (!repo || (repo.status !== 'pending' && repo.status !== 'cloning')) {
      return
    }

    const interval = setInterval(() => {
      fetchData()
    }, 3000)

    return () => clearInterval(interval)
  }, [repo, fetchData])

  const handleExportAll = async () => {
    if (!repo) return
    setExporting(true)
    try {
      const blob = await exportRepository(repo.id)
      saveAs(blob, `${repo.name}-docs.zip`)
    } catch (error) {
      console.error('Failed to export:', error)
    } finally {
      setExporting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 text-text-muted animate-spin" />
      </div>
    )
  }

  if (!repo) {
    return (
      <div className="bg-surface rounded-xl shadow-card p-8 text-center">
        <p className="text-text-muted">仓库不存在</p>
      </div>
    )
  }

  // 仓库正在克隆或等待中
  if (repo.status === 'pending' || repo.status === 'cloning') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-surface rounded-xl shadow-card p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <RefreshCw className="w-8 h-8 text-accent animate-spin" />
            </div>
            <h2 className="text-xl font-medium text-text-primary mb-2">{repo.name}</h2>
            <p className="text-text-muted mb-4">{repo.url}</p>
            
            {/* 进度条 */}
            <div className="max-w-xs mx-auto mb-4">
              <div className="h-2 bg-surface-alt rounded-full overflow-hidden">
                <div className="h-full bg-accent rounded-full animate-pulse" style={{ width: '60%' }} />
              </div>
            </div>
            
            <p className="text-sm text-text-secondary">
              {repo.status === 'pending' ? '等待克隆...' : '正在克隆仓库，请稍候...'}
            </p>
            <p className="text-xs text-text-muted mt-2">
              页面将自动刷新
            </p>
          </div>
        </div>
      </div>
    )
  }

  // 仓库克隆失败
  if (repo.status === 'error') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-surface rounded-xl shadow-card p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">⚠️</span>
            </div>
            <h2 className="text-xl font-medium text-text-primary mb-2">{repo.name}</h2>
            <p className="text-error mb-4">克隆失败</p>
            <p className="text-sm text-text-muted">{repo.error_message}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-surface rounded-xl shadow-card p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-medium text-text-primary mb-2">{repo.name}</h1>
            <p className="text-sm text-text-muted mb-3">{repo.url}</p>
            <div className="flex items-center gap-4 text-sm text-text-secondary">
              <span>{repo.doc_count} 个文档</span>
              <span>分支: {repo.branch}</span>
            </div>
          </div>
          <button
            onClick={handleExportAll}
            disabled={exporting}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-light transition-colors disabled:opacity-50"
          >
            {exporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            导出全部
          </button>
        </div>
      </div>

      {/* Document Tree */}
      <div className="bg-surface rounded-xl shadow-card">
        <div className="px-6 py-4 border-b border-divider">
          <h2 className="text-sm font-medium text-text-primary">文档列表</h2>
        </div>
        <div className="py-2">
          {tree.length === 0 ? (
            <p className="px-6 py-8 text-center text-text-muted">暂无文档</p>
          ) : (
            <TreeView nodes={tree} repoId={Number(repoId)} />
          )}
        </div>
      </div>
    </div>
  )
}

interface TreeViewProps {
  nodes: TreeNode[]
  repoId: number
}

function TreeView({ nodes, repoId }: TreeViewProps) {
  return (
    <div>
      {nodes.map((node) => (
        <TreeNodeItem key={node.path} node={node} repoId={repoId} depth={0} />
      ))}
    </div>
  )
}

interface TreeNodeItemProps {
  node: TreeNode
  repoId: number
  depth: number
}

function TreeNodeItem({ node, repoId, depth }: TreeNodeItemProps) {
  const [expanded, setExpanded] = useState(depth < 1)

  if (node.type === 'directory') {
    return (
      <div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center gap-3 px-6 py-2.5 hover:bg-background transition-colors text-left"
          style={{ paddingLeft: `${24 + depth * 16}px` }}
        >
          <ChevronRight 
            className={`w-4 h-4 text-text-muted transition-transform ${expanded ? 'rotate-90' : ''}`} 
          />
          <Folder className="w-5 h-5 text-accent" />
          <span className="text-sm text-text-primary">{node.name}</span>
        </button>
        {expanded && node.children && (
          <div>
            {node.children.map((child) => (
              <TreeNodeItem key={child.path} node={child} repoId={repoId} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <Link
      to={`/repo/${repoId}/doc/${node.path}`}
      className="flex items-center gap-3 px-6 py-2.5 hover:bg-background transition-colors"
      style={{ paddingLeft: `${44 + depth * 16}px` }}
    >
      <FileText className="w-5 h-5 text-text-muted" />
      <span className="text-sm text-text-secondary hover:text-accent">{node.name}</span>
    </Link>
  )
}
