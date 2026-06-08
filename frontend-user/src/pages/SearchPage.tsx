import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Search, FileText, Loader2 } from 'lucide-react'
import { searchDocuments } from '../api/repositories'
import type { SearchResponse } from '../types'

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const performSearch = async () => {
      if (!query.trim()) {
        setResults(null)
        return
      }

      setLoading(true)
      try {
        const data = await searchDocuments(query)
        setResults(data)
      } catch (error) {
        console.error('Search failed:', error)
      } finally {
        setLoading(false)
      }
    }

    performSearch()
  }, [query])

  return (
    <div className="max-w-4xl mx-auto">
      {/* Search Header */}
      <div className="bg-surface rounded-xl shadow-card p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Search className="w-5 h-5 text-text-muted" />
          <h1 className="text-lg font-medium text-text-primary">搜索结果</h1>
        </div>
        {query && (
          <p className="text-text-secondary">
            搜索 "<span className="text-accent font-medium">{query}</span>" 
            {results && <span className="text-text-muted ml-2">找到 {results.total} 个结果</span>}
          </p>
        )}
      </div>

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 text-text-muted animate-spin" />
        </div>
      ) : !query ? (
        <div className="bg-surface rounded-xl shadow-card p-8 text-center">
          <Search className="w-12 h-12 text-text-muted mx-auto mb-3" />
          <p className="text-text-muted">请输入搜索关键词</p>
        </div>
      ) : results && results.results.length === 0 ? (
        <div className="bg-surface rounded-xl shadow-card p-8 text-center">
          <FileText className="w-12 h-12 text-text-muted mx-auto mb-3" />
          <p className="text-text-muted">未找到相关文档</p>
        </div>
      ) : results ? (
        <div className="space-y-4">
          {results.results.map((result, index) => (
            <Link
              key={index}
              to={`/repo/${result.repository.id}/doc/${result.document.filepath}`}
              className="block bg-surface rounded-xl shadow-card p-5 hover:shadow-card-hover transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-surface-alt rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-text-muted" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-text-primary mb-1">
                    {result.document.filename}
                  </h3>
                  <p className="text-xs text-text-muted mb-2">
                    {result.repository.name} / {result.document.filepath}
                  </p>
                  {result.highlights.length > 0 && (
                    <div className="text-sm text-text-secondary">
                      {result.highlights.map((highlight, i) => (
                        <p 
                          key={i} 
                          className="line-clamp-2"
                          dangerouslySetInnerHTML={{ 
                            __html: highlight.replace(
                              new RegExp(`(${query})`, 'gi'), 
                              '<mark class="bg-accent-light text-accent px-0.5 rounded">$1</mark>'
                            ) 
                          }}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  )
}
