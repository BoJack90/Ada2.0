'use client'

import { useOrganizationStore } from '@/stores'
import { DashboardContent } from '@/components/layout/dashboard-content'
import { OrganizationDashboard } from '@/components/dashboard/organization-dashboard'

export default function DashboardPage() {
  const { currentOrganization } = useOrganizationStore()

  // Jeśli organizacja jest wybrana, pokaż dashboard organizacji
  if (currentOrganization) {
    return <OrganizationDashboard />
  }

  // Jeśli nie ma wybranej organizacji, pokaż globalne dashboard
  return <DashboardContent />
} 