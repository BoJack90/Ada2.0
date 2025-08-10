'use client'

import { motion } from 'framer-motion'
import { useDashboard } from '@/contexts/dashboard-context'
import { AnalyticsDashboard } from '@/components/dashboard/analytics-dashboard'
import { TaskManager } from '@/components/dashboard/task-manager'
import { OrganizationList } from '@/components/organization/organization-list'
import { ApiStatus } from '@/components/dashboard/api-status'
import { CalendarView } from '@/components/dashboard/calendar-view'
import { DocumentViewer } from '@/components/dashboard/document-viewer'

export function DashboardContent() {
  const { activeView } = useDashboard()

  console.log('[DashboardContent] activeView:', activeView)

  const renderContent = () => {
    console.log('[DashboardContent] Rendering content for view:', activeView)
    switch (activeView) {
      case 'analytics':
        return <AnalyticsDashboard />
      case 'organizations':
        console.log('[DashboardContent] Rendering OrganizationList')
        return <OrganizationList />
      case 'tasks':
        return <TaskManager expanded={true} />
      case 'api-status':
        return <ApiStatus />
      case 'calendar':
        return <CalendarView />
      case 'documents':
        return <DocumentViewer />
      default:
        return <AnalyticsDashboard />
    }
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="dashboard-content"
    >
      {renderContent()}
    </motion.div>
  )
}
