'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'

export default function DashboardOrganizationSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const organizationId = params?.id as string

  useEffect(() => {
    // Przekierowanie do właściwej strony settings
    if (organizationId) {
      router.replace(`/organizations/${organizationId}/settings`)
    }
  }, [organizationId, router])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-lg font-medium text-gray-900">Przekierowywanie...</h2>
      </div>
    </div>
  )
}