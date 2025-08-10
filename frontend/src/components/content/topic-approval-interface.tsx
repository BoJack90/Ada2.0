'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  CheckCircle,
  XCircle,
  FileText,
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  ChevronRight,
  Loader2,
  Star,
  Target,
  Brain,
  Tag
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { ContentPlan, SuggestedTopic } from '@/types'

interface TopicApprovalInterfaceProps {
  plan: ContentPlan
}

export function TopicApprovalInterface({ plan }: TopicApprovalInterfaceProps) {
  const queryClient = useQueryClient()
  const toast = useToast()
  const [feedbackNotes, setFeedbackNotes] = useState<Record<number, string>>({})

  // Pobieranie sugerowanych tematów
  const { data: topics, isLoading } = useQuery({
    queryKey: ['suggested-topics', plan.id],
    queryFn: async () => {
      return await api.contentPlans.getSuggestedTopics(plan.id)
    },
    enabled: !!plan.id
  })

  // Mutacja do aktualizacji statusu tematu
  const updateTopicStatusMutation = useMutation({
    mutationFn: async ({ topicId, status }: { topicId: number; status: string }) => {
      return await api.contentPlans.updateTopicStatus(topicId, { status })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suggested-topics', plan.id] })
      queryClient.invalidateQueries({ queryKey: ['content-plan', plan.id] })
      toast.success('Status tematu został zaktualizowany')
    }
  })

  // Mutacja do wyzwalania generowania postów SM
  const triggerSmGenerationMutation = useMutation({
    mutationFn: async () => {
      return await api.contentPlans.triggerSmGeneration(plan.id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-plan', plan.id] })
      toast.success('Rozpoczęto generowanie postów social media')
    }
  })

  const handleApprove = (topicId: number) => {
    updateTopicStatusMutation.mutate({ topicId, status: 'approved' })
  }

  const handleReject = (topicId: number) => {
    updateTopicStatusMutation.mutate({ topicId, status: 'rejected' })
  }

  const handleProceedToNextStep = () => {
    triggerSmGenerationMutation.mutate()
  }

  // Grupowanie tematów według statusu
  const groupedTopics = topics?.reduce((acc, topic) => {
    const status = topic.status || 'suggested'
    if (!acc[status]) acc[status] = []
    acc[status].push(topic)
    return acc
  }, {} as Record<string, SuggestedTopic[]>) || {}

  const approvedCount = groupedTopics['approved']?.length || 0
  const totalCount = topics?.length || 0
  const canProceed = approvedCount > 0

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      suggested: { label: 'Sugerowany', className: 'bg-blue-50 text-blue-600' },
      approved: { label: 'Zatwierdzony', className: 'bg-green-50 text-green-600' },
      rejected: { label: 'Odrzucony', className: 'bg-destructive/10 text-destructive' }
    }
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.suggested
    return <Badge className={config.className}>{config.label}</Badge>
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header z instrukcjami */}
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-foreground mb-2">
              Akceptacja tematów blogowych
            </h2>
            <p className="text-muted-foreground mb-4">
              Przejrzyj i zaakceptuj tematy blogowe zaproponowane przez AI. 
              Możesz zatwierdzić, odrzucić lub dodać komentarze do każdego tematu.
            </p>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-foreground">{approvedCount} zatwierdzonych</span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="h-4 w-4 text-destructive" />
                <span className="text-foreground">{groupedTopics['rejected']?.length || 0} odrzuconych</span>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-blue-600" />
                <span className="text-foreground">{totalCount} łącznie</span>
              </div>
            </div>
          </div>
          <Button
            onClick={handleProceedToNextStep}
            disabled={!canProceed || triggerSmGenerationMutation.isPending}
            size="lg"
          >
            {triggerSmGenerationMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generowanie...
              </>
            ) : (
              <>
                Przejdź dalej
                <ChevronRight className="h-4 w-4 ml-2" />
              </>
            )}
          </Button>
        </div>
      </Card>

      {/* Lista tematów */}
      <div className="space-y-4">
        {topics && topics.length > 0 ? (
          topics.map((topic, index) => (
            <motion.div
              key={topic.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        <FileText className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-foreground mb-1">
                          {topic.title}
                        </h3>
                        <div className="flex items-center gap-2 flex-wrap">
                          {topic.category && (
                            <Badge variant="outline">
                              {topic.category}
                            </Badge>
                          )}
                          {/* Show meta_data for deep reasoning topics */}
                          {topic.meta_data?.priority_score && (
                            <Badge variant="secondary" className="flex items-center gap-1">
                              <Star className="w-3 h-3" />
                              Priorytet: {topic.meta_data.priority_score}/10
                            </Badge>
                          )}
                          {topic.meta_data?.pillar && (
                            <Badge variant="outline" className="flex items-center gap-1">
                              <Tag className="w-3 h-3" />
                              {topic.meta_data.pillar}
                            </Badge>
                          )}
                          {topic.meta_data?.reasoning_steps && (
                            <Badge variant="secondary" className="flex items-center gap-1 bg-purple-100 text-purple-700">
                              <Brain className="w-3 h-3" />
                              Deep Reasoning
                            </Badge>
                          )}
                        </div>
                      </div>
                      {getStatusBadge(topic.status)}
                    </div>
                    
                    {topic.description && (
                      <p className="text-muted-foreground mb-4">
                        {topic.description}
                      </p>
                    )}

                    {/* Pole na feedback */}
                    {topic.status === 'suggested' && (
                      <div className="mt-4">
                        <Textarea
                          placeholder="Dodaj komentarz lub sugestie..."
                          value={feedbackNotes[topic.id] || ''}
                          onChange={(e) => setFeedbackNotes({
                            ...feedbackNotes,
                            [topic.id]: e.target.value
                          })}
                          className="min-h-[80px] text-sm"
                        />
                      </div>
                    )}
                  </div>
                </div>

                {/* Przyciski akcji */}
                {topic.status === 'suggested' && (
                  <div className="flex items-center justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleReject(topic.id)}
                      disabled={updateTopicStatusMutation.isPending}
                    >
                      <ThumbsDown className="h-4 w-4 mr-2" />
                      Odrzuć
                    </Button>
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => handleApprove(topic.id)}
                      disabled={updateTopicStatusMutation.isPending}
                    >
                      <ThumbsUp className="h-4 w-4 mr-2" />
                      Zatwierdź
                    </Button>
                  </div>
                )}
              </Card>
            </motion.div>
          ))
        ) : (
          <Card className="p-8 text-center">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              Brak sugerowanych tematów
            </h3>
            <p className="text-muted-foreground">
              Tematy pojawią się tutaj po wygenerowaniu
            </p>
          </Card>
        )}
      </div>
    </div>
  )
}