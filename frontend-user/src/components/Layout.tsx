import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div className="min-h-screen bg-background max-w-full overflow-x-hidden">
      <Header />
      <div className="flex min-w-0">
        <Sidebar />
        <main className="flex-1 min-w-0 p-6 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
