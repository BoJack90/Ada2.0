'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore, useOrganizationStore } from '@/stores'
import { useDashboard, DashboardView } from '@/contexts/dashboard-context'
import { 
  BarChart3, 
  Users, 
  CheckSquare,
  Activity,
  Calendar,
  FileText,
  FileEdit,
  NotebookPen,
  FolderOpen,
  Settings, 
  LogOut,
  Building2,
  Sparkles,
  ChevronDown,
  Home
} from 'lucide-react'

interface NavigationItem {
  label: string
  icon: React.ComponentType<any>
  view?: DashboardView
  href?: string
  contextual?: boolean // Oznacza czy link wymaga wybranej organizacji
  route?: string // Scieżka dla kontekstowych linków
  badge?: string
  color?: string
  isNew?: boolean
}

// Globalne elementy nawigacji (dostępne zawsze)
const globalNavigationItems: NavigationItem[] = [
  {
    label: 'Dashboard',
    icon: Home,
    href: '/dashboard',
    color: 'blue'
  },
  {
    label: 'Organizacje',
    icon: Building2,
    href: '/dashboard/organizations',
    color: 'purple'
  },
  {
    label: 'Ustawienia',
    icon: Settings,
    href: '/settings',
    color: 'gray'
  }
]

// Kontekstowe elementy nawigacji (wymagają wybranej organizacji)
const contextualNavigationItems: NavigationItem[] = [
  {
    label: 'Plany Treści',
    icon: NotebookPen,
    contextual: true,
    route: 'content-plans',
    color: 'emerald',
    badge: 'New',
    isNew: true
  },
  {
    label: 'Pulpit Treści',
    icon: FileEdit,
    contextual: true,
    route: 'content-workspace',
    color: 'orange',
    isNew: true
  },
  {
    label: 'Zadania',
    icon: CheckSquare,
    contextual: true,
    route: 'tasks',
    color: 'red'
  },
  {
    label: 'Status API',
    icon: Activity,
    contextual: true,
    route: 'api-status',
    color: 'yellow'
  },
  {
    label: 'Kalendarz',
    icon: Calendar,
    contextual: true,
    route: 'calendar',
    color: 'indigo'
  },
  {
    label: 'Dokumenty',
    icon: FolderOpen,
    contextual: true,
    route: 'documents',
    color: 'teal'
  },
  {
    label: 'Ustawienia',
    icon: Settings,
    contextual: true,
    route: 'settings'
  }
]

export function Navigation() {
  const { logout } = useAuthStore()
  const { currentOrganization, setCurrentOrganization } = useOrganizationStore()
  const router = useRouter()
  const pathname = typeof window !== 'undefined' ? window.location.pathname : ''

  const handleGlobalNavigationClick = (item: NavigationItem) => {
    if (item.href) {
      // Jeśli to link do Dashboard, wyczyść aktywną organizację
      if (item.href === '/dashboard') {
        setCurrentOrganization(null)
      }
      router.push(item.href)
    }
  }

  const handleContextualNavigationClick = (item: NavigationItem) => {
    if (!currentOrganization || !item.route) return
    
    const href = `/dashboard/organization/${currentOrganization.id}/${item.route}`
    router.push(href)
  }

  const handleLogout = () => {
    logout()
  }

  const getColorClasses = (color?: string) => {
    const colors = {
      blue: 'text-primary bg-primary/10',
      purple: 'text-purple-600 bg-purple-50',
      emerald: 'text-emerald-600 bg-emerald-50',
      orange: 'text-orange-600 bg-orange-50',
      red: 'text-destructive bg-destructive/10',
      yellow: 'text-yellow-600 bg-yellow-50',
      indigo: 'text-indigo-600 bg-indigo-50',
      teal: 'text-teal-600 bg-teal-50'
    }
    return colors[color as keyof typeof colors] || 'text-muted-foreground bg-muted'
  }

  const getActiveColorClasses = (color?: string) => {
    return 'text-primary-foreground bg-primary shadow-soft-md'
  }

  return (
    <motion.nav 
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="fixed left-0 top-0 h-full w-64 bg-card shadow-soft-lg border-r border-border z-50 overflow-y-auto"
    >
      {/* Brand Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className="px-6 py-6 border-b border-border"
      >
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
            <span className="text-sm font-bold text-primary">A</span>
          </div>
          Ada 2.0
        </h1>
        <p className="text-muted-foreground text-sm mt-1">Platforma zarządzania treścią</p>
      </motion.div>

      {/* Navigation Content */}
      <div className="p-4 space-y-6">
        {/* Global Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
        >
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-2">
            Nawigacja główna
          </h3>
          <div className="space-y-1">
            {globalNavigationItems.map((item, index) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <motion.button
                  key={item.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index + 0.3, duration: 0.3 }}
                  whileHover={{ scale: 1.02, x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleGlobalNavigationClick(item)}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2.5 rounded-md font-medium transition-all duration-200
                    ${isActive 
                      ? getActiveColorClasses(item.color)
                      : 'text-foreground hover:' + getColorClasses(item.color) + ' hover:shadow-soft'
                    }
                  `}
                >
                  <Icon size={18} className={isActive ? 'text-white' : ''} />
                  <span className="flex-1 text-left">{item.label}</span>
                  {item.isNew && (
                    <span className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs px-2 py-0.5 rounded-full font-semibold">
                      Nowe
                    </span>
                  )}
                </motion.button>
              )
            })}
          </div>
        </motion.div>

        {/* Organization Context */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.3 }}
        >
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-2">
            Kontekst organizacji
          </h3>
          
          {/* Organization Selector */}
          <div className="mb-4 p-3 bg-muted/50 rounded-lg border border-border">
            {currentOrganization ? (
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <span className="text-primary-foreground text-sm font-bold">
                    {currentOrganization.name.charAt(0)}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {currentOrganization.name}
                  </p>
                  <p className="text-xs text-muted-foreground">Aktywna organizacja</p>
                </div>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Brak organizacji</p>
                <p className="text-xs text-muted-foreground">Wybierz organizację</p>
              </div>
            )}
          </div>

          {/* Contextual Navigation */}
          <div className="space-y-1">
            {contextualNavigationItems.map((item, index) => {
              const Icon = item.icon
              const isDisabled = !currentOrganization
              const href = currentOrganization ? `/dashboard/organization/${currentOrganization.id}/${item.route}` : '#'
              const isActive = pathname === href
              
              return (
                <motion.button
                  key={item.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index + 0.5, duration: 0.3 }}
                  whileHover={!isDisabled ? { scale: 1.02, x: 4 } : {}}
                  whileTap={!isDisabled ? { scale: 0.98 } : {}}
                  onClick={() => handleContextualNavigationClick(item)}
                  disabled={isDisabled}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2.5 rounded-md font-medium transition-all duration-200
                    ${isDisabled 
                      ? 'text-muted-foreground/50 cursor-not-allowed opacity-50'
                      : isActive 
                        ? getActiveColorClasses(item.color)
                        : 'text-foreground hover:' + getColorClasses(item.color) + ' hover:shadow-soft'
                    }
                  `}
                  title={isDisabled ? 'Wybierz organizację aby uzyskać dostęp' : ''}
                >
                  <Icon size={18} className={isActive && !isDisabled ? 'text-white' : ''} />
                  <span className="flex-1 text-left">{item.label}</span>
                  {item.isNew && !isDisabled && (
                    <span className="bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full font-semibold">
                      Nowe
                    </span>
                  )}
                </motion.button>
              )
            })}
          </div>
        </motion.div>

        {/* Account Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.3 }}
          className="border-t border-border pt-4"
        >
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-2">
            Konto
          </h3>
          <div className="space-y-1">
            {/* Settings */}
            <motion.button
              whileHover={{ scale: 1.02, x: 4 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md font-medium transition-all duration-200 text-foreground hover:bg-muted hover:shadow-soft"
            >
              <Settings size={18} />
              <span className="flex-1 text-left">Ustawienia</span>
            </motion.button>

            {/* Logout */}
            <motion.button
              whileHover={{ scale: 1.02, x: 4 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md font-medium transition-all duration-200 text-destructive hover:text-destructive-foreground hover:bg-destructive hover:shadow-soft-md"
            >
              <LogOut size={18} />
              <span className="flex-1 text-left">Wyloguj się</span>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </motion.nav>
  )
}