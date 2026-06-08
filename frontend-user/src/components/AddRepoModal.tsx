import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'

interface AddRepoModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (url: string) => Promise<void>
}

export default function AddRepoModal({ isOpen, onClose, onSubmit }: AddRepoModalProps) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!url.trim()) {
      setError('请输入仓库地址')
      return
    }

    // Basic URL validation
    if (!url.match(/^https?:\/\/.+\/.+/)) {
      setError('请输入有效的 Git 仓库地址')
      return
    }

    setLoading(true)
    try {
      await onSubmit(url)
      setUrl('')
    } catch (err) {
      setError('添加仓库失败，请检查地址是否正确')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-md bg-surface rounded-xl shadow-xl mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-divider">
          <h2 className="text-lg font-medium text-text-primary">添加 Git 仓库</h2>
          <button
            onClick={onClose}
            className="p-1 text-text-muted hover:text-text-primary rounded-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-text-secondary mb-2">
              仓库地址
            </label>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="w-full h-11 px-4 bg-surface border border-border rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/10 transition-all"
              disabled={loading}
            />
            {error && (
              <p className="mt-2 text-sm text-error">{error}</p>
            )}
          </div>

          <p className="text-xs text-text-muted mb-6">
            支持 GitHub、GitLab、Gitee 等公开仓库
          </p>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 h-10 px-4 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-surface-alt transition-colors"
              disabled={loading}
            >
              取消
            </button>
            <button
              type="submit"
              className="flex-1 h-10 px-4 bg-primary rounded-lg text-sm font-medium text-white hover:bg-primary-light transition-colors flex items-center justify-center gap-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  添加中...
                </>
              ) : (
                '添加仓库'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
