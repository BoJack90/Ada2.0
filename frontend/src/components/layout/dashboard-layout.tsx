'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { Navigation } from './navigation'
import { Header } from './header'

interface DashboardLayoutProps {
  children: ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Navigation Sidebar */}
      <Navigation />
      
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      <main className="ml-64 pt-16">
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="p-6"
        >
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </motion.div>
      </main>
    </div>
  )
}
