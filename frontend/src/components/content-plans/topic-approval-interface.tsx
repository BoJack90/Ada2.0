'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, XCircle, Clock, AlertCircle, Check, X, Loader2 } from 'lucide-react'

import { api } from '@/lib/api'
import { ContentPlan, SuggestedTopic } from '@/types'
import { Card } from '@/components/ui/cards'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

interface TopicApprovalInterfaceProps {
  contentPlan: ContentPlan
}

interface TopicWithLocalStatus extends SuggestedTopic {
  localStatus?: 'approved' | 'rejected' | 'suggested' | null
  isUpdating?: boolean
}

export function TopicApprovalInterface({ contentPlan }: TopicApprovalInterfaceProps) {
  const queryClient = useQueryClient()
  const [topics, setTopics] = useState<TopicWithLocalStatus[]>([])
  const [approvedCount, setApprovedCount] = useState(0)

  // Debug logging
  console.log('[TopicApprovalInterface] Content Plan:', contentPlan)
  console.log('[TopicApprovalInterface] Content Plan ID:', contentPlan.id)

  // Fetch suggested topics
  const { data: suggestedTopics, isLoading, error } = useQuery({
    queryKey: ['suggestedTopics', contentPlan.id],
    queryFn: async () => {
      console.log('[TopicApprovalInterface] Fetching topics for plan ID:', contentPlan.id)
      const result = await api.contentPlans.getSuggestedTopics(contentPlan.id)
      console.log('[TopicApprovalInterface] Fetched topics:', result)
      return result
    },
    enabled: !!contentPlan.id,
    retry: 3,
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Update local state when data changes
  useEffect(() => {
    console.log('[TopicApprovalInterface] Suggested topics updated:', suggestedTopics)
    if (suggestedTopics && Array.isArray(suggestedTopics)) {
      const processedTopics = suggestedTopics.map(topic => ({
        ...topic,
        localStatus: topic.status === 'suggested' ? null : topic.status as 'approved' | 'rejected',
        isUpdating: false
      }))
      console.log('[TopicApprovalInterface] Processed topics:', processedTopics)
      setTopics(processedTopics)
    } else if (suggestedTopics === null || suggestedTopics === undefined) {
      console.log('[TopicApprovalInterface] No topics data received')
      setTopics([])
    }
  }, [suggestedTopics])

  // Count approved topics
  useEffect(() => {
    const count = topics.filter(topic => {
      const currentStatus = topic.localStatus !== null ? topic.localStatus : topic.status
      return currentStatus === 'approved'
    }).length
    console.log('[TopicApprovalInterface] Approved count:', count, 'Required:', contentPlan.blog_posts_quota)
    setApprovedCount(count)
  }, [topics, contentPlan.blog_posts_quota])

  // Mutation for updating topic status
  const updateTopicMutation = useMutation({
    mutationFn: ({ topicId, status }: { topicId: number; status: 'approved' | 'rejected' | 'suggested' }) => {
      console.log('[TopicApprovalInterface] Updating topic status:', { topicId, status })
      return api.contentPlans.updateTopicStatus(topicId, { status })
    },
    onSuccess: (updatedTopic) => {
      console.log('[TopicApprovalInterface] Topic status updated successfully:', updatedTopic)
      // Update local state
      setTopics(prev => prev.map(topic => 
        topic.id === updatedTopic.id 
          ? { ...updatedTopic, localStatus: updatedTopic.status === 'suggested' ? null : updatedTopic.status as 'approved' | 'rejected', isUpdating: false }
          : topic
      ))
      // Update cache
      queryClient.invalidateQueries({ queryKey: ['suggestedTopics', contentPlan.id] })
    },
    onError: (error, variables) => {
      console.error('[TopicApprovalInterface] Error updating topic status:', error, variables)
      // Reset updating state on error
      setTopics(prev => prev.map(topic => 
        topic.id === variables.topicId 
          ? { ...topic, isUpdating: false }
          : topic
      ))
    }
  })

  // Mutation for triggering SM generation
  const triggerSmMutation = useMutation({
    mutationFn: () => {
      console.log('[TopicApprovalInterface] Triggering SM generation for plan:', contentPlan.id)
      return api.contentPlans.triggerSmGeneration(contentPlan.id)
    },
    onSuccess: (result) => {
      console.log('[TopicApprovalInterface] SM generation triggered successfully:', result)
      // Invalidate and refetch content plan to update status
      queryClient.invalidateQueries({ queryKey: ['contentPlan', contentPlan.id] })
      queryClient.invalidateQueries({ queryKey: ['contentPlans'] })
    },
    onError: (error) => {
      console.error('[TopicApprovalInterface] Error triggering SM generation:', error)
    }
  })

  const handleTopicAction = (topicId: number, action: 'approve' | 'reject' | 'undo') => {
    const status = action === 'approve' ? 'approved' : action === 'reject' ? 'rejected' : 'suggested'
    
    console.log('[TopicApprovalInterface] Handling topic action:', { topicId, action, status })
    
    // Update local state to show immediate feedback
    setTopics(prev => {
      const updated = prev.map(topic => 
        topic.id === topicId 
          ? { ...topic, localStatus: status === 'suggested' ? null : status as 'approved' | 'rejected', isUpdating: true }
          : topic
      )
      console.log('[TopicApprovalInterface] Updated local topics state:', updated)
      return updated
    })
    
    // Execute mutation
    updateTopicMutation.mutate({ topicId, status })
  }

  const handleFinalize = () => {
    console.log('[TopicApprovalInterface] Finalizing topic selection...')
    console.log('[TopicApprovalInterface] Approved topics count:', approvedCount)
    console.log('[TopicApprovalInterface] Required quota:', contentPlan.blog_posts_quota)
    console.log('[TopicApprovalInterface] Is enabled:', isFinalizationEnabled)
    
    if (!isFinalizationEnabled) {
      console.warn('[TopicApprovalInterface] Finalization not enabled, aborting')
      return
    }
    
    triggerSmMutation.mutate()
  }

  const getTopicDisplayStatus = (topic: TopicWithLocalStatus): string => {
    // Jeśli mamy lokalny status (optymistyczna aktualizacja), użyj go
    // W przeciwnym razie użyj statusu z serwera
    if (topic.localStatus !== null && topic.localStatus !== undefined) {
      return topic.localStatus
    }
    return topic.status || 'suggested'
  }

  const getTopicStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'suggested':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getTopicStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'rejected':
        return <XCircle className="w-4 h-4 text-red-600" />
      case 'suggested':
        return <Clock className="w-4 h-4 text-yellow-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-600" />
    }
  }

  const isFinalizationEnabled = approvedCount >= contentPlan.blog_posts_quota

  console.log('[TopicApprovalInterface] Finalization enabled:', isFinalizationEnabled, 'Approved:', approvedCount, 'Required:', contentPlan.blog_posts_quota)

  if (isLoading) {
    return (
      <Card className="p-8 text-center">
        <LoadingSpinner size="large" />
        <p className="text-gray-600 mt-4">Ładowanie propozycji tematów dla planu {contentPlan.id}...</p>
      </Card>
    )
  }

  if (error) {
    console.error('[TopicApprovalInterface] Error loading topics:', error)
    return (
      <Card className="p-8 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Błąd podczas ładowania tematów
        </h3>
        <p className="text-gray-600 mb-4">
          Nie udało się załadować propozycji tematów dla planu {contentPlan.plan_period}.
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Błąd: {error instanceof Error ? error.message : 'Nieznany błąd'}
        </p>
        <button
          onClick={() => queryClient.invalidateQueries({ queryKey: ['suggestedTopics', contentPlan.id] })}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Spróbuj ponownie
        </button>
      </Card>
    )
  }

  if (!topics || topics.length === 0) {
    console.log('[TopicApprovalInterface] No topics available')
    return (
      <Card className="p-8 text-center">
        <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Brak tematów do zatwierdzenia
        </h3>
        <p className="text-gray-600 mb-4">
          Nie znaleziono propozycji tematów dla tego planu treści.
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Plan: {contentPlan.plan_period} (ID: {contentPlan.id})
        </p>
        <div className="space-y-2">
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['suggestedTopics', contentPlan.id] })}
            className="block mx-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Odśwież listę tematów
          </button>
          <p className="text-xs text-gray-400">
            Upewnij się, że proces generowania tematów został zakończony pomyślnie.
          </p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with progress */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Akceptacja Tematów Blogowych
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Zatwierdź tematy, które chcesz wykorzystać do generowania treści
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">
              {approvedCount}/{contentPlan.blog_posts_quota}
            </div>
            <div className="text-sm text-gray-600">
              zatwierdzonych tematów
            </div>
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Postęp akceptacji</span>
            <span>{Math.round((approvedCount / contentPlan.blog_posts_quota) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min((approvedCount / contentPlan.blog_posts_quota) * 100, 100)}%` }}
            />
          </div>
        </div>
      </Card>

      {/* Topics list */}
      <div className="space-y-4">
        <AnimatePresence>
          {topics.map((topic, index) => {
            const displayStatus = getTopicDisplayStatus(topic)
            const statusColor = getTopicStatusColor(displayStatus)
            const statusIcon = getTopicStatusIcon(displayStatus)
            
            return (
              <motion.div
                key={topic.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                <Card className={`p-6 transition-all duration-300 ${
                  displayStatus === 'approved' ? 'ring-2 ring-green-200 bg-green-50' : 
                  displayStatus === 'rejected' ? 'ring-2 ring-red-200 bg-red-50' : 
                  'hover:shadow-md'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-medium text-gray-900">
                          {topic.title}
                        </h3>
                        <Badge className={`${statusColor} flex items-center gap-1`}>
                          {statusIcon}
                          {displayStatus === 'approved' ? 'Zatwierdzony' : 
                           displayStatus === 'rejected' ? 'Odrzucony' : 
                           displayStatus === 'suggested' ? 'Oczekuje' : 
                           'Nieznany'}
                        </Badge>
                      </div>
                      <p className="text-gray-600 text-sm leading-relaxed">
                        {topic.description}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      {displayStatus === 'suggested' && (
                        <>
                          <button
                            onClick={() => handleTopicAction(topic.id, 'approve')}
                            disabled={topic.isUpdating}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {topic.isUpdating ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Check className="w-4 h-4" />
                            )}
                            Akceptuj
                          </button>
                          <button
                            onClick={() => handleTopicAction(topic.id, 'reject')}
                            disabled={topic.isUpdating}
                            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {topic.isUpdating ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <X className="w-4 h-4" />
                            )}
                            Odrzuć
                          </button>
                        </>
                      )}
                      {(displayStatus === 'approved' || displayStatus === 'rejected') && (
                        <button
                          onClick={() => handleTopicAction(topic.id, 'undo')}
                          disabled={topic.isUpdating}
                          className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {topic.isUpdating ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <X className="w-4 h-4" />
                          )}
                          Cofnij
                        </button>
                      )}
                    </div>
                  </div>
                </Card>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* Finalization button */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Finalizacja wyboru tematów
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {isFinalizationEnabled ? 
                'Możesz teraz uruchomić generowanie treści social media.' : 
                `Zatwierdź co najmniej ${contentPlan.blog_posts_quota} tematów aby kontynuować (obecnie: ${approvedCount}).`
              }
            </p>
            {/* Debug info */}
            <div className="mt-2 text-xs text-gray-400">
              Plan ID: {contentPlan.id} | Status: {contentPlan.status} | Quota: {contentPlan.blog_posts_quota} | Zatwierdzone: {approvedCount}
            </div>
          </div>
          <div className="text-right">
            <div className="mb-2 text-sm text-gray-600">
              Postęp: {approvedCount} / {contentPlan.blog_posts_quota}
            </div>
            <button
              onClick={handleFinalize}
              disabled={!isFinalizationEnabled || triggerSmMutation.isPending}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                isFinalizationEnabled 
                  ? 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
              title={!isFinalizationEnabled ? `Zatwierdź jeszcze ${contentPlan.blog_posts_quota - approvedCount} tematów` : 'Uruchom generowanie treści SM'}
            >
              {triggerSmMutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Uruchamianie...
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Zatwierdź Wybrane Tematy i Generuj Treści SM
                </>
              )}
            </button>
            {triggerSmMutation.error && (
              <p className="text-sm text-red-600 mt-2">
                Błąd: {triggerSmMutation.error instanceof Error ? triggerSmMutation.error.message : 'Nieznany błąd'}
              </p>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
} 