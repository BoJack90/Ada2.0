'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  ArrowLeft,
  FileText,
  Calendar,
  CheckCircle,
  Clock,
  AlertCircle,
  Sparkles,
  RefreshCw,
  Send,
  Brain,
  BarChart3,
  Search
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { ContentCalendar } from '@/components/content/content-calendar'
import { TopicApprovalInterface } from '@/components/content/topic-approval-interface'
import { ContentWorkspace } from '@/components/content/content-workspace'
import { ContentVisualizationV2 } from '@/components/content/content-visualization-v2'
import { PlanStatusOverview } from '@/components/content/plan-status-overview'
import { BriefManager } from '@/components/content-plans/brief-manager'
import { CorrelationConfig } from '@/components/content-plans/correlation-config'
import { VariantGenerationControl } from '@/components/content-plans/variant-generation-control'
import { AutoGenerateTopics } from '@/components/content-plans/auto-generate-topics'
import { GenerationInsights } from '@/components/content-plans/generation-insights'
import { ResearchTool } from '@/components/tools/research-tool'
import { Badge } from '@/components/ui/badge'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { useToast } from '@/hooks/use-toast'
import '@/styles/calendar.css'

export default function ContentPlanDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { success: toastSuccess } = useToast()
  const organizationId = params?.id ? parseInt(params.id as string) : null
  const planId = params?.planId ? parseInt(params.planId as string) : null
  
  const [activeTab, setActiveTab] = useState<'overview' | 'research' | 'insights'>('overview')

  // Pobieranie szczegółów planu
  const { data: plan, isLoading: planLoading } = useQuery({
    queryKey: ['content-plan', planId],
    queryFn: async () => {
      if (!planId) return null
      return await api.contentPlans.get(planId)
    },
    enabled: !!planId
  })

  // Pobieranie harmonogramu dla planów ze statusem 'complete'
  const { data: scheduledPosts, isLoading: scheduleLoading } = useQuery({
    queryKey: ['content-plan-schedule', planId],
    queryFn: async () => {
      if (!planId) return []
      return await api.contentPlans.getSchedule(planId)
    },
    enabled: !!planId && plan?.status === 'complete'
  })

  // Pobieranie tematów sugerowanych
  const { data: suggestedTopics } = useQuery({
    queryKey: ['suggested-topics', planId],
    queryFn: async () => {
      if (!planId) return []
      return await api.contentPlans.getSuggestedTopics(planId)
    },
    enabled: !!planId
  })

  // Mutacja do anulowania publikacji
  const cancelPostMutation = useMutation({
    mutationFn: async (postId: number) => {
      // Tu będzie wywołanie API do anulowania publikacji
      console.log('Cancelling post:', postId)
      // return await api.scheduledPosts.cancel(postId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-plan-schedule', planId] })
      toastSuccess('Post został usunięty z harmonogramu')
    }
  })

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { label: 'Szkic', className: 'bg-muted text-muted-foreground', icon: Clock },
      in_progress: { label: 'W trakcie', className: 'bg-yellow-50 text-yellow-600', icon: RefreshCw },
      complete: { label: 'Ukończony', className: 'bg-green-50 text-green-600', icon: CheckCircle },
      error: { label: 'Błąd', className: 'bg-destructive/10 text-destructive', icon: AlertCircle }
    }
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft
    const Icon = config.icon
    
    return (
      <Badge className={`${config.className} flex items-center gap-1`}>
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    )
  }

  if (planLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (!plan) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center">
          <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">
            Plan nie został znaleziony
          </h3>
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Wróć
          </Button>
        </Card>
      </div>
    )
  }

  // Renderowanie interfejsu w zależności od statusu planu (maszyna stanów)
  const renderPlanInterface = () => {
    switch (plan.status) {
      case 'new':
        // Show auto-generation if plan has advanced generation method
        if (plan.meta_data?.generation_method === 'deep_reasoning') {
          return <AutoGenerateTopics planId={planId!} planMetadata={plan.meta_data} />
        }
        return <PlanStatusOverview status={plan.status} />
        
      case 'generating_topics':
        return (
          <div className="space-y-6">
            <PlanStatusOverview status={plan.status} />
            {plan.meta_data?.generation_method === 'deep_reasoning' && (
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Brain className="w-5 h-5 text-purple-500" />
                  <h3 className="text-lg font-semibold">Deep Reasoning w toku</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  System przeprowadza zaawansowaną analizę z wykorzystaniem zewnętrznych źródeł.
                  Proces może potrwać 2-5 minut.
                </p>
              </Card>
            )}
          </div>
        )
      
      case 'pending_blog_topic_approval':
        return <TopicApprovalInterface plan={plan} />
      
      case 'generating_sm_topics':
      case 'pending_draft_approval':
      case 'generating_drafts':
      case 'draft':
      case 'review':
      case 'pending_final_scheduling':
        // Przygotuj listę zatwierdzonych tematów SM bez wariantów
        const approvedSmTopics = (suggestedTopics || [])
          .filter(topic => 
            topic.category === 'social_media' && 
            topic.status === 'approved'
          )
          .map(topic => ({
            id: topic.id,
            title: topic.title,
            hasVariants: false // TODO: Check if topic has content drafts
          }))
        
        return (
          <div className="space-y-6">
            {approvedSmTopics.length > 0 && (
              <VariantGenerationControl
                contentPlanId={planId!}
                approvedSmTopics={approvedSmTopics}
              />
            )}
            <ContentVisualizationV2 
              planId={planId!} 
              organizationId={organizationId!} 
            />
          </div>
        )
      
      case 'complete':
        return (
          <>
            {scheduleLoading ? (
              <Card className="p-8 text-center">
                <LoadingSpinner size="large" />
                <p className="mt-4 text-muted-foreground">Ładowanie harmonogramu...</p>
              </Card>
            ) : scheduledPosts && scheduledPosts.length > 0 ? (
              <ContentCalendar 
                scheduledPosts={scheduledPosts}
                onCancelPost={(postId) => cancelPostMutation.mutate(postId)}
              />
            ) : (
              <Card className="p-8 text-center">
                <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Brak zaplanowanych publikacji
                </h3>
                <p className="text-muted-foreground">
                  Harmonogram publikacji pojawi się tutaj po zatwierdzeniu treści
                </p>
              </Card>
            )}
          </>
        )
      
      default:
        return <PlanStatusOverview status={plan.status} />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="card-base p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.back()}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Powrót
              </Button>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-foreground">
                    Plan treści: {plan.plan_period}
                  </h1>
                  <p className="text-muted-foreground">
                    Utworzony: {format(new Date(plan.created_at), 'dd MMMM yyyy', { locale: pl })}
                  </p>
                </div>
              </div>
            </div>
            {getStatusBadge(plan.status)}
          </div>
        </motion.div>

        {/* Informacje o planie */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground">Szczegóły planu</h2>
              {plan.meta_data?.generation_method === 'deep_reasoning' && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Brain className="w-3 h-3" />
                  Deep Reasoning AI
                </Badge>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Posty blogowe</p>
                <p className="text-xl font-semibold text-foreground">{plan.blog_posts_quota}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Posty social media</p>
                <p className="text-xl font-semibold text-foreground">{plan.sm_posts_quota}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Tryb planowania</p>
                <p className="text-xl font-semibold text-foreground capitalize">
                  {plan.scheduling_mode === 'auto' ? 'Automatyczny' : 
                   plan.scheduling_mode === 'with_guidelines' ? 'Z wytycznymi' : 'Wizualny'}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Briefy i korelacja - pokazuj tylko dla statusów przed finalizacją */}
        {['new', 'generating_topics', 'pending_blog_topic_approval'].includes(plan.status) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 }}
            >
              <BriefManager 
                contentPlanId={planId!} 
                isReadOnly={plan.status !== 'new'}
              />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <CorrelationConfig
                contentPlanId={planId!}
                blogPostsQuota={plan.blog_posts_quota}
                smPostsQuota={plan.sm_posts_quota}
                isReadOnly={plan.status !== 'new'}
              />
            </motion.div>
          </div>
        )}

        {/* Tabs for different views */}
        {['pending_blog_topic_approval', 'generating_sm_topics', 'pending_draft_approval', 'complete'].includes(plan.status) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="p-1">
              <div className="flex space-x-1">
                <Button
                  variant={activeTab === 'overview' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('overview')}
                  className="flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  Przegląd
                </Button>
                <Button
                  variant={activeTab === 'insights' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('insights')}
                  className="flex items-center gap-2"
                >
                  <BarChart3 className="w-4 h-4" />
                  Insights
                  {plan.meta_data?.generation_method === 'deep_reasoning' && (
                    <Badge variant="secondary" className="ml-1 text-xs">
                      <Brain className="w-3 h-3 mr-1" />
                      AI
                    </Badge>
                  )}
                </Button>
                <Button
                  variant={activeTab === 'research' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('research')}
                  className="flex items-center gap-2"
                >
                  <Search className="w-4 h-4" />
                  Research
                </Button>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Renderowanie interfejsu w zależności od statusu */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
        >
          {activeTab === 'overview' && renderPlanInterface()}
          {activeTab === 'insights' && planId && (
            <GenerationInsights planId={planId} />
          )}
          {activeTab === 'research' && (
            <ResearchTool 
              organizationId={organizationId || undefined}
              industry={plan.organization?.industry}
            />
          )}
        </motion.div>
      </div>
    </div>
  )
}