import { Link, useLocation } from 'react-router-dom'
import { Activity, History, Info } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Analyze', icon: Activity },
  { path: '/history', label: 'History', icon: History },
  { path: '/about', label: 'About', icon: Info },
]

export default function Header() {
  const location = useLocation()

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-primary-600" />
            </div>
            <span className="text-xl font-bold text-gray-900">
              Respiratory<span className="text-primary-600">AI</span>
            </span>
          </Link>

          <nav className="flex items-center gap-1">
            {navItems.map(({ path, label, icon: Icon }) => {
              const isActive = location.pathname === path
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{label}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}
