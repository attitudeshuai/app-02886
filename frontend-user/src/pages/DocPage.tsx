import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Download, Loader2, FileText, ArrowLeft, FolderOpen } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import rehypeSlug from 'rehype-slug'
import remarkGfm from 'remark-gfm'
import { getDocumentContent, exportDocument, getReadingProgress, saveReadingProgress } from '../api/repositories'
import type { DocumentContent } from '../types'
import { saveAs } from 'file-saver'
import 'highlight.js/styles/github-dark.css'

const SESSION_STORAGE_KEY = 'reader_session_id'

const generateSessionId = (): string => {
  return 'session_' + Date.now().toString(36) + '_' + Math.random().toString(36).substring(2, 10)
}

const getSessionId = (): string => {
  let sessionId = localStorage.getItem(SESSION_STORAGE_KEY)
  if (!sessionId) {
    sessionId = generateSessionId()
    localStorage.setItem(SESSION_STORAGE_KEY, sessionId)
  }
  return sessionId
}

interface TocItem {
  id: string
  text: string
  level: number
}

export default function DocPage() {
  const { repoId, '*': filepath } = useParams<{ repoId: string; '*': string }>()
  const [doc, setDoc] = useState<DocumentContent | null>(null)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [toc, setToc] = useState<TocItem[]>([])
  const [activeId, setActiveId] = useState<string>('')
  const [contentRendered, setContentRendered] = useState(false)
  const [hasRestoredProgress, setHasRestoredProgress] = useState(false)
  
  const contentRef = useRef<HTMLDivElement>(null)
  const tocRef = useRef<HTMLDivElement>(null)
  const tocItemRefs = useRef<Map<string, HTMLButtonElement>>(new Map())
  const observerRef = useRef<IntersectionObserver | null>(null)
  // true = 正在由用户点击驱动的跳转，Observer 和 TOC 自动滚动都应忽略
  const isUserClickScrolling = useRef(false)
  const scrollEndTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  // Observer 累积的可见标题集合（提升为 ref 以便清空）
  const visibleIdsRef = useRef(new Set<string>())
  // 阅读进度相关
  const sessionIdRef = useRef<string>(getSessionId())
  const saveProgressTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isRestoringProgress = useRef(false)

  // 清理
  useEffect(() => {
    return () => {
      if (scrollEndTimer.current) clearTimeout(scrollEndTimer.current)
      if (saveProgressTimer.current) clearTimeout(saveProgressTimer.current)
      observerRef.current?.disconnect()
    }
  }, [])

  // 加载文档内容
  useEffect(() => {
    const fetchDoc = async () => {
      if (!repoId || !filepath) return
      setLoading(true)
      setActiveId('')
      setToc([])
      setContentRendered(false)
      setHasRestoredProgress(false)
      isRestoringProgress.current = false
      // 滚动到顶部，等待恢复进度
      window.scrollTo({ top: 0, behavior: 'auto' })
      try {
        const data = await getDocumentContent(Number(repoId), filepath)
        setDoc(data)
      } catch (error) {
        console.error('Failed to fetch document:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDoc()
  }, [repoId, filepath])

  // 从实际 DOM 提取标题 ID（保证和 rehype-slug 生成的完全一致）
  useEffect(() => {
    if (!contentRendered || !contentRef.current) return
    const raf = requestAnimationFrame(() => {
      const els = contentRef.current?.querySelectorAll('h1[id], h2[id], h3[id]')
      if (!els || els.length === 0) return
      const items: TocItem[] = []
      els.forEach((el) => {
        const id = el.getAttribute('id')
        if (!id) return
        items.push({
          id,
          text: el.textContent || '',
          level: parseInt(el.tagName.charAt(1), 10),
        })
      })
      setToc(items)
      if (items.length > 0) setActiveId(items[0].id)
    })
    return () => cancelAnimationFrame(raf)
  }, [contentRendered])

  // 恢复阅读进度
  useEffect(() => {
    if (!contentRendered || !repoId || !filepath || hasRestoredProgress) return

    const restoreProgress = async () => {
      try {
        const progress = await getReadingProgress(
          Number(repoId),
          filepath,
          sessionIdRef.current
        )

        if (progress && progress.scroll_position > 0) {
          isRestoringProgress.current = true
          const doc = document.documentElement
          const maxScroll = doc.scrollHeight - doc.clientHeight
          const targetY = maxScroll * progress.scroll_position
          window.scrollTo({ top: targetY, behavior: 'auto' })
          
          setTimeout(() => {
            isRestoringProgress.current = false
            setHasRestoredProgress(true)
          }, 100)
        } else {
          setHasRestoredProgress(true)
        }
      } catch (error) {
        console.error('Failed to restore reading progress:', error)
        setHasRestoredProgress(true)
      }
    }

    restoreProgress()
  }, [contentRendered, repoId, filepath])

  // ========== Intersection Observer ==========
  useEffect(() => {
    if (!contentRef.current || toc.length === 0) return
    observerRef.current?.disconnect()

    const headings = contentRef.current.querySelectorAll('h1[id], h2[id], h3[id]')
    if (headings.length === 0) return

    // 按文档顺序排列的所有标题 id
    const orderedIds: string[] = []
    headings.forEach((el) => {
      const id = el.getAttribute('id')
      if (id) orderedIds.push(id)
    })

    // 清空可见标题集合
    visibleIdsRef.current.clear()

    const callback: IntersectionObserverCallback = (entries) => {
      if (isUserClickScrolling.current) return

      const visibleIds = visibleIdsRef.current

      entries.forEach((entry) => {
        const id = entry.target.getAttribute('id')
        if (!id) return
        if (entry.isIntersecting) {
          visibleIds.add(id)
        } else {
          visibleIds.delete(id)
        }
      })

      if (visibleIds.size === 0) return

      // 从文档顺序中选第一个可见的标题
      for (const id of orderedIds) {
        if (visibleIds.has(id)) {
          setActiveId(id)
          return
        }
      }
    }

    observerRef.current = new IntersectionObserver(callback, {
      root: null,
      rootMargin: '-80px 0px -65% 0px',
      threshold: 0,
    })

    headings.forEach((el) => observerRef.current?.observe(el))

    return () => observerRef.current?.disconnect()
  }, [toc])

  // ========== TOC 自动跟随（仅在非点击滚动时） ==========
  useEffect(() => {
    // 点击触发的 activeId 变化不需要自动滚动 TOC（用户已经看到了）
    if (!activeId || !tocRef.current || isUserClickScrolling.current) return

    const btn = tocItemRefs.current.get(activeId)
    if (!btn) return

    const container = tocRef.current
    const btnTop = btn.offsetTop
    const btnHeight = btn.offsetHeight
    const scrollTop = container.scrollTop
    const containerHeight = container.clientHeight

    // 只在超出可见区域时才滚动，且只滚动 TOC 容器
    if (btnTop < scrollTop + 20) {
      container.scrollTo({ top: btnTop - 20, behavior: 'smooth' })
    } else if (btnTop + btnHeight > scrollTop + containerHeight - 20) {
      container.scrollTo({
        top: btnTop + btnHeight - containerHeight + 20,
        behavior: 'smooth',
      })
    }
  }, [activeId])

  // ========== 根据当前滚动位置计算活跃标题 ==========
  const computeActiveFromScroll = useCallback(() => {
    if (!contentRef.current) return
    const headings = contentRef.current.querySelectorAll('h1[id], h2[id], h3[id]')
    if (!headings.length) return

    const headerOffset = 100
    let bestId = ''

    // 找到最后一个已经滚过顶部（或刚好在顶部）的标题
    headings.forEach((el) => {
      const rect = el.getBoundingClientRect()
      if (rect.top <= headerOffset) {
        const id = el.getAttribute('id')
        if (id) bestId = id
      }
    })

    // 如果没有滚过顶部的，取第一个
    if (!bestId) {
      const first = headings[0].getAttribute('id')
      if (first) bestId = first
    }

    if (bestId) setActiveId(bestId)
  }, [])

  // ========== 保存阅读进度 ==========
  const saveProgress = useCallback(() => {
    if (!repoId || !filepath || !hasRestoredProgress || isRestoringProgress.current) return

    const scrollTop = window.scrollY
    const doc = document.documentElement
    const maxScroll = doc.scrollHeight - doc.clientHeight
    const scrollPosition = maxScroll > 0 ? Math.min(1, Math.max(0, scrollTop / maxScroll)) : 0

    if (saveProgressTimer.current) {
      clearTimeout(saveProgressTimer.current)
    }

    saveProgressTimer.current = setTimeout(async () => {
      try {
        await saveReadingProgress(
          Number(repoId),
          filepath,
          sessionIdRef.current,
          scrollPosition
        )
      } catch (error) {
        console.error('Failed to save reading progress:', error)
      }
    }, 500)
  }, [repoId, filepath, hasRestoredProgress])

  // 监听滚动事件，保存进度
  useEffect(() => {
    if (!hasRestoredProgress) return

    const handleScroll = () => {
      if (isRestoringProgress.current) return
      saveProgress()
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [hasRestoredProgress, saveProgress])

  // ========== 点击 TOC 跳转 ==========
  const handleTocClick = useCallback((id: string) => {
    const element = document.getElementById(id)
    if (!element) return

    // 1) 锁定：禁用 Observer + 禁用 TOC 自动滚动
    isUserClickScrolling.current = true
    if (scrollEndTimer.current) clearTimeout(scrollEndTimer.current)

    // 2) 清空 Observer 累积的旧数据
    visibleIdsRef.current.clear()

    // 3) 立即高亮
    setActiveId(id)

    // 4) 仅滚动主页面
    const headerOffset = 100
    const y =
      element.getBoundingClientRect().top + window.pageYOffset - headerOffset
    window.scrollTo({ top: y, behavior: 'smooth' })

    // 5) 监听滚动结束后解锁 + 重新计算真实位置
    const unlock = () => {
      isUserClickScrolling.current = false
      // 解锁后断开重连 Observer，让它重新收集所有标题的可见状态
      if (observerRef.current && contentRef.current) {
        const headings = contentRef.current.querySelectorAll('h1[id], h2[id], h3[id]')
        observerRef.current.disconnect()
        headings.forEach((el) => observerRef.current?.observe(el))
      }
      // 同时根据当前滚动位置主动计算一次
      computeActiveFromScroll()
    }

    const onScroll = () => {
      if (scrollEndTimer.current) clearTimeout(scrollEndTimer.current)
      scrollEndTimer.current = setTimeout(() => {
        window.removeEventListener('scroll', onScroll)
        unlock()
      }, 150)
    }
    window.addEventListener('scroll', onScroll, { passive: true })

    // 兜底：最多 2 秒后一定解锁
    scrollEndTimer.current = setTimeout(() => {
      window.removeEventListener('scroll', onScroll)
      unlock()
    }, 2000)
  }, [computeActiveFromScroll])

  const handleExport = async () => {
    if (!repoId || !filepath || !doc) return
    setExporting(true)
    try {
      const blob = await exportDocument(Number(repoId), filepath)
      saveAs(blob, doc.document.filename)
    } catch (error) {
      console.error('Failed to export:', error)
    } finally {
      setExporting(false)
    }
  }

  const setTocItemRef = useCallback(
    (id: string, el: HTMLButtonElement | null) => {
      if (el) tocItemRefs.current.set(id, el)
      else tocItemRefs.current.delete(id)
    },
    []
  )

  // ========== 渲染 ==========

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 text-text-muted animate-spin" />
      </div>
    )
  }

  if (!doc) {
    return (
      <div className="bg-surface rounded-xl shadow-card p-8 text-center">
        <FileText className="w-12 h-12 text-text-muted mx-auto mb-3" />
        <p className="text-text-muted mb-4">文档不存在</p>
        <Link
          to={`/repo/${repoId}`}
          className="inline-flex items-center gap-2 text-accent hover:underline"
        >
          <ArrowLeft className="w-4 h-4" />
          返回文件列表
        </Link>
      </div>
    )
  }

  return (
    <div className="flex gap-6 min-w-0 max-w-full">
      {/* Main Content */}
      <div className="flex-1 min-w-0 overflow-hidden">
        <div className="mb-4">
          <Link
            to={`/repo/${repoId}`}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm text-text-secondary hover:text-text-primary bg-surface rounded-lg shadow-card hover:shadow-card-hover transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <FolderOpen className="w-4 h-4" />
            <span>返回文件列表</span>
          </Link>
        </div>

        <div className="bg-surface rounded-xl shadow-card overflow-hidden">
          <div className="px-8 py-4 border-b border-divider flex items-center justify-between">
            <div className="min-w-0 flex-1 mr-4">
              <h1 className="text-lg font-medium text-text-primary truncate">
                {doc.document.filename}
              </h1>
              <p className="text-sm text-text-muted mt-1 truncate">{filepath}</p>
            </div>
            <button
              onClick={handleExport}
              disabled={exporting}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-border rounded-md text-sm text-text-secondary hover:bg-surface-alt transition-colors disabled:opacity-50"
            >
              {exporting ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              下载
            </button>
          </div>

          <div ref={contentRef} className="px-10 py-8 overflow-hidden">
            <article className="markdown-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw, rehypeHighlight, rehypeSlug]}
                components={{
                  p: ({ children, ...props }) => {
                    if (!contentRendered) {
                      setTimeout(() => setContentRendered(true), 0)
                    }
                    return <p {...props}>{children}</p>
                  },
                }}
              >
                {doc.content}
              </ReactMarkdown>
            </article>
          </div>
        </div>
      </div>

      {/* TOC Sidebar */}
      {toc.length > 0 && (
        <aside className="w-[220px] flex-shrink-0 hidden xl:block">
          <div className="sticky top-20">
            <h3 className="text-xs font-medium text-text-muted uppercase tracking-wider mb-3 px-2">
              目录 ({toc.length})
            </h3>
            <div
              ref={tocRef}
              className="max-h-[calc(100vh-160px)] overflow-y-auto scrollbar-thin pr-2"
            >
              <nav className="space-y-0.5 border-l-2 border-divider">
                {toc.map((item, index) => {
                  const isActive = activeId === item.id
                  return (
                    <button
                      key={`${item.id}-${index}`}
                      ref={(el) => setTocItemRef(item.id, el)}
                      onClick={() => handleTocClick(item.id)}
                      className={`
                        block w-full text-left text-sm py-1.5 pr-2 transition-all duration-200
                        border-l-2 -ml-[2px]
                        ${
                          isActive
                            ? 'text-accent border-accent bg-accent/5 font-medium'
                            : 'text-text-secondary border-transparent hover:text-text-primary hover:border-text-muted'
                        }
                      `}
                      style={{
                        paddingLeft: `${8 + (item.level - 1) * 12}px`,
                      }}
                      title={item.text}
                    >
                      <span className="line-clamp-2">{item.text}</span>
                    </button>
                  )
                })}
              </nav>
            </div>
          </div>
        </aside>
      )}
    </div>
  )
}
