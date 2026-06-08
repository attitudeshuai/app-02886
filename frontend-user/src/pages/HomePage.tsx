import { BookOpen, FolderGit2, Search, Download } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="bg-surface rounded-xl shadow-card p-8 mb-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-[28px] font-medium text-text-primary mb-3">
            Git Doc Fetcher
          </h1>
          <p className="text-text-secondary max-w-lg mx-auto">
            一款简洁高效的 Git 仓库文档抓取工具，帮助您快速浏览、搜索和导出任意公开仓库的文档内容。
          </p>
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FeatureCard
          icon={<FolderGit2 className="w-5 h-5" />}
          title="仓库管理"
          description="支持添加多个 Git 仓库，自动扫描并索引文档文件"
        />
        <FeatureCard
          icon={<BookOpen className="w-5 h-5" />}
          title="文档浏览"
          description="精美的 Markdown 渲染，支持代码高亮和目录导航"
        />
        <FeatureCard
          icon={<Search className="w-5 h-5" />}
          title="全文搜索"
          description="快速搜索所有文档内容，关键词高亮显示"
        />
        <FeatureCard
          icon={<Download className="w-5 h-5" />}
          title="文档导出"
          description="支持导出为 Markdown 或 PDF，可批量打包下载"
        />
      </div>

      {/* Getting Started */}
      <div className="mt-6 bg-surface rounded-xl shadow-card p-6">
        <h2 className="text-lg font-medium text-text-primary mb-4">快速开始</h2>
        <ol className="space-y-3 text-text-secondary">
          <li className="flex gap-3">
            <span className="w-6 h-6 bg-accent/10 text-accent rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">1</span>
            <span>点击左侧边栏的 "+" 按钮添加一个 Git 仓库</span>
          </li>
          <li className="flex gap-3">
            <span className="w-6 h-6 bg-accent/10 text-accent rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">2</span>
            <span>等待仓库克隆完成，系统会自动扫描文档</span>
          </li>
          <li className="flex gap-3">
            <span className="w-6 h-6 bg-accent/10 text-accent rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">3</span>
            <span>点击仓库名称，浏览文档树并查看内容</span>
          </li>
        </ol>
      </div>
    </div>
  )
}

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="bg-surface rounded-xl shadow-card p-5 hover:shadow-card-hover transition-shadow">
      <div className="w-10 h-10 bg-surface-alt rounded-lg flex items-center justify-center text-text-muted mb-3">
        {icon}
      </div>
      <h3 className="text-sm font-medium text-text-primary mb-1">{title}</h3>
      <p className="text-sm text-text-muted">{description}</p>
    </div>
  )
}
