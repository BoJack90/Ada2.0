'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

export type DashboardView = 
  | 'analytics' 
  | 'organizations' 
  | 'tasks' 
  | 'api-status'
  | 'calendar'
  | 'documents'
  | 'content-plans'

interface DashboardContextType {
  activeView: DashboardView
  setActiveView: (view: DashboardView) => void
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined)

interface DashboardProviderProps {
  children: ReactNode
}

export function DashboardProvider({ children }: DashboardProviderProps) {
  const [activeView, setActiveView] = useState<DashboardView>('analytics')

  return (
    <DashboardContext.Provider value={{ activeView, setActiveView }}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider')
  }
  return context
}
