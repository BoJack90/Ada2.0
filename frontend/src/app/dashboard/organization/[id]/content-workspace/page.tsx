'use client'

import { useParams } from 'next/navigation'
import { PlansOverview } from '@/components/workspace/plans-overview'

export default function ContentWorkspacePage() {
  const params = useParams()
  const organizationId = parseInt(params.id as string)
  
  console.log('ContentWorkspacePage rendered, params:', params)

  if (!organizationId || isNaN(organizationId)) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Nieprawidłowe parametry organizacji</p>
      </div>
    )
  }

  return <PlansOverview organizationId={organizationId} />
}