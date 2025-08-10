'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Calendar,
  FileText,
  Users,
  ChevronRight,
  Loader2
} from 'lucide-react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { format, parseISO } from 'date-fns'
import { pl } from 'date-fns/locale'

interface PlansOverviewProps {
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

export function PlansOverview({ organizationId }: PlansOverviewProps) {
  const router = useRouter()
  const [plans, setPlans] = useState<ContentPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  console.log('PlansOverview component loaded, orgId:', organizationId)

  useEffect(() => {
    async function fetchPlans() {
      console.log('Fetching plans for organization:', organizationId)
      setLoading(true)
      setError(null)
      
      try {
        const data = await api.contentPlans.list(organizationId)
        console.log('Plans fetched successfully:', data)
        setPlans(data || [])
      } catch (err) {
        console.error('Error fetching plans:', err)
        setError('Nie udało się pobrać planów treści')
      } finally {
        setLoading(false)
      }
    }

    if (organizationId) {
      fetchPlans()
    }
  }, [organizationId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <Card className="p-6 max-w-md">
          <p className="text-center text-red-500">{error}</p>
        </Card>
      </div>
    )
  }

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

      {plans.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {plans.map((plan) => (
            <Card 
              key={plan.id}
              className="p-6 cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => router.push(`/dashboard/organization/${organizationId}/content-workspace/plan/${plan.id}`)}
            >
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-primary" />
                    {plan.plan_period}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {format(parseISO(plan.created_at), 'dd MMM yyyy', { locale: pl })}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <FileText className="h-4 w-4" />
                      Blog
                    </div>
                    <div className="text-xl font-bold">{plan.blog_posts_quota}</div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Users className="h-4 w-4" />
                      Social
                    </div>
                    <div className="text-xl font-bold">{plan.sm_posts_quota}</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <Badge>{plan.status}</Badge>
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
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
            Stwórz pierwszy plan treści
          </p>
          <Button onClick={() => router.push(`/dashboard/organization/${organizationId}/content-plans/new`)}>
            Stwórz plan
          </Button>
        </Card>
      )}
    </div>
  )
}