'use client'

import { useContext } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { AuthContext } from '@/contexts/auth-context'
import { ContentPlansDisplay } from '@/components/content/content-plans-display'

export default function ContentDashboardPage() {
  const { user } = useContext(AuthContext)
  const organizationId = user?.active_organization_id

  if (!organizationId) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Nie wybrano organizacji</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <ContentPlansDisplay organizationId={organizationId} />
    </DashboardLayout>
  )
}