'use client'

import { useContext } from 'react'
import { useParams } from 'next/navigation'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { AuthContext } from '@/contexts/auth-context'
import { ContentPlanVisualization } from '@/components/content/content-plan-visualization'

export default function ContentPlanViewPage() {
  const { user } = useContext(AuthContext)
  const params = useParams()
  const planId = parseInt(params.plan_id as string)
  const organizationId = user?.active_organization_id

  if (!organizationId || !planId) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Nieprawidłowe parametry</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <ContentPlanVisualization 
        planId={planId} 
        organizationId={organizationId} 
      />
    </DashboardLayout>
  )
}