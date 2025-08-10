'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  Calendar,
  FileText,
  Users,
  Clock,
  CheckCircle,
  AlertCircle,
  ChevronRight,
  Eye,
  TrendingUp,
  Layers
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { format, parseISO } from 'date-fns'
import { pl } from 'date-fns/locale'

interface ContentPlansDisplayProps {
  organizationId: number
}

interface ContentPlan {
  id: number
  plan_period: string
  status: string
  blog_posts_quota: number
  sm_posts_quota: number
  created_at: string
  updated_at: string
}

export function ContentPlansDisplay({ organizationId }: ContentPlansDisplayProps) {
  const router = useRouter()
  
  console.log('ContentPlansDisplay mounted with org:', organizationId)

  // Fetch content plans using the correct endpoint
  const { data: plans, isLoading, error } = useQuery<ContentPlan[]>({
    queryKey: ['content-plans-v2', organizationId],
    queryFn: async () => {
      console.log('Fetching content plans using api.contentPlans.list...')
      const data = await api.contentPlans.list(organizationId)
      console.log('Content plans fetched:', data)
      return data || []
    }
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <Card className="p-6 max-w-md">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-center text-muted-foreground">
            Błąd podczas ładowania planów treści
          </p>
        </Card>
      </div>
    )
  }

  console.log('Plans loaded:', plans)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Plany treści</h2>
        <Button
          onClick={() => router.push(`/dashboard/organization/${organizationId}/content-plans/new`)}
        >
          <Calendar className="h-4 w-4 mr-2" />
          Nowy plan
        </Button>
      </div>

      {plans && plans.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {plans.map((plan) => (
            <Card 
              key={plan.id}
              className="p-6 cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => router.push(`/dashboard/organization/${organizationId}/content-plans/${plan.id}`)}
            >
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                      <Calendar className="h-5 w-5 text-primary" />
                      {plan.plan_period}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      Utworzono: {format(parseISO(plan.created_at), 'dd MMM yyyy', { locale: pl })}
                    </p>
                  </div>
                  <Badge>{plan.status}</Badge>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                      <FileText className="h-4 w-4" />
                      Blog
                    </div>
                    <div className="text-xl font-bold">{plan.blog_posts_quota}</div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                      <Users className="h-4 w-4" />
                      Social
                    </div>
                    <div className="text-xl font-bold">{plan.sm_posts_quota}</div>
                  </div>
                </div>

                <div className="flex items-center justify-end text-primary">
                  <Eye className="h-4 w-4 mr-1" />
                  <span className="text-sm">Zobacz</span>
                  <ChevronRight className="h-4 w-4" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Brak planów treści</h3>
          <p className="text-muted-foreground mb-6">
            Stwórz pierwszy plan treści, aby rozpocząć generowanie
          </p>
          <Button onClick={() => router.push(`/dashboard/organization/${organizationId}/content-plans/new`)}>
            Stwórz plan treści
          </Button>
        </Card>
      )}
    </div>
  )
}