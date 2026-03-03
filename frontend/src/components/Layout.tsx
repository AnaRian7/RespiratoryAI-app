import { ReactNode } from 'react'
import Header from './Header'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
        {children}
      </main>
      <footer className="bg-gray-100 border-t border-gray-200 py-6">
        <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
          <p>RespiratoryAI - AI-Powered Chest X-Ray Analysis</p>
          <p className="mt-1 text-gray-500">
            For research and educational purposes only. Not for clinical diagnosis.
          </p>
        </div>
      </footer>
    </div>
  )
}
