'use client'

import { usePathname } from 'next/navigation'
import { ReactNode } from 'react'
import { DashboardProvider } from '@/contexts/dashboard-context'
import { DashboardLayout } from './dashboard-layout'

interface LayoutWrapperProps {
  children: ReactNode
}

export function LayoutWrapper({ children }: LayoutWrapperProps) {
  const pathname = usePathname()
  
  // Sprawdź czy to strona auth (login/register)
  const isAuthPage = pathname?.startsWith('/auth')
  
  if (isAuthPage) {
    // Dla stron auth - zwróć samo children bez dashboardu
    return <>{children}</>
  }
  
  // Dla pozostałych stron - użyj pełnego layoutu z dashboardem
  return (
    <DashboardProvider>
      <DashboardLayout>
        {children}
      </DashboardLayout>
    </DashboardProvider>
  )
}
