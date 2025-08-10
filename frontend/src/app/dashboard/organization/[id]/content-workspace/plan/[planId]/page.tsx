'use client'

import { useParams, useRouter } from 'next/navigation'
import { ContentVisualizationV2 } from '@/components/content/content-visualization-v2'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

export default function ContentPlanVisualizationPage() {
  const params = useParams()
  const router = useRouter()
  const organizationId = parseInt(params.id as string)
  const planId = parseInt(params.planId as string)

  if (!organizationId || !planId) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Nieprawidłowe parametry</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push(`/dashboard/organization/${organizationId}/content-workspace`)}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Powrót do pulpitu
        </Button>
      </div>
      
      <ContentVisualizationV2 
        planId={planId} 
        organizationId={organizationId} 
      />
    </div>
  )
}