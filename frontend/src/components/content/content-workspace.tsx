'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  FileEdit, 
  Plus, 
  Calendar,
  Filter,
  Search,
  ChevronRight,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Loader2,
  FileText,
  MessageSquare
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ContentPlan, ContentStatus } from '@/types'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'

interface ContentWorkspaceProps {
  plan: ContentPlan
}

export function ContentWorkspace({ plan }: ContentWorkspaceProps) {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<ContentStatus | 'all'>('all')

  // Pobieranie draftów dla tego planu
  const { data: drafts, isLoading } = useQuery({
    queryKey: ['content-drafts', plan.id],
    queryFn: async () => {
      const result = await api.contentPlans.getDrafts(plan.id)
      console.log('Drafts from API:', result)
      return result
    },
    enabled: !!plan.id
  })

  // Filtrowanie draftów
  console.log('Drafts before filtering:', drafts)
  const filteredDrafts = drafts?.filter(draft => {
    if (!draft) return false
    console.log('Processing draft:', draft)
    
    // Bezpieczne pobieranie topic
    let topic = ''
    try {
      topic = draft.suggested_topic?.title || draft.topic || ''
    } catch (e) {
      console.error('Error getting topic:', e, draft)
      topic = ''
    }
    
    const searchLower = searchQuery?.toLowerCase() || ''
    const topicLower = topic?.toLowerCase() || ''
    const matchesSearch = topicLower.includes(searchLower)
    const matchesStatus = statusFilter === 'all' || draft.status === statusFilter
    return matchesSearch && matchesStatus
  }) || []

  const getStatusIcon = (status: ContentStatus) => {
    switch (status) {
      case 'draft':
        return <Clock className="h-4 w-4" />
      case 'review':
        return <AlertCircle className="h-4 w-4" />
      case 'approved':
        return <CheckCircle className="h-4 w-4" />
      case 'rejected':
        return <XCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: ContentStatus) => {
    switch (status) {
      case 'draft':
        return 'text-muted-foreground bg-muted'
      case 'review':
        return 'text-yellow-600 bg-yellow-50'
      case 'approved':
        return 'text-green-600 bg-green-50'
      case 'rejected':
        return 'text-destructive bg-destructive/10'
      default:
        return 'text-muted-foreground bg-muted'
    }
  }

  const handleDraftClick = (draftId: number) => {
    router.push(`/dashboard/drafts/${draftId}`)
  }

  const getPlanStatusMessage = () => {
    switch (plan.status) {
      case 'generating_sm_topics':
        return {
          icon: <Loader2 className="h-6 w-6 animate-spin" />,
          title: 'Generowanie postów social media',
          description: 'Trwa generowanie propozycji postów dla różnych platform społecznościowych',
          showProgress: true
        }
      case 'generating_drafts':
        return {
          icon: <Loader2 className="h-6 w-6 animate-spin" />,
          title: 'Generowanie treści',
          description: 'Trwa generowanie wariantów treści dla zatwierdzonych tematów',
          showProgress: true
        }
      case 'pending_draft_approval':
        return {
          icon: <FileEdit className="h-6 w-6" />,
          title: 'Treści gotowe do recenzji',
          description: 'Przejrzyj i zatwierdź wygenerowane warianty treści',
          showProgress: false
        }
      default:
        return {
          icon: <FileText className="h-6 w-6" />,
          title: 'Zarządzanie treściami',
          description: 'Przeglądaj i edytuj treści w tym planie',
          showProgress: false
        }
    }
  }

  const statusMessage = getPlanStatusMessage()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header z informacjami o statusie */}
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-lg ${statusMessage.showProgress ? 'bg-primary/10 text-primary' : 'bg-primary/10 text-primary'}`}>
            {statusMessage.icon}
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-foreground mb-2">
              {statusMessage.title}
            </h2>
            <p className="text-muted-foreground mb-4">
              {statusMessage.description}
            </p>
            {statusMessage.showProgress && (
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Filtry - tylko jeśli są drafty */}
      {drafts && drafts.length > 0 && (
        <Card className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Szukaj po temacie..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <div className="flex gap-2">
              {(['all', 'draft', 'review', 'approved', 'rejected'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    statusFilter === status
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground hover:bg-accent'
                  }`}
                >
                  {status === 'all' ? 'Wszystkie' : 
                   status === 'draft' ? 'Szkice' :
                   status === 'review' ? 'W recenzji' :
                   status === 'approved' ? 'Zatwierdzone' : 'Odrzucone'}
                </button>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Lista draftów */}
      <div className="grid gap-4">
        {filteredDrafts.length === 0 ? (
          <Card className="p-8 text-center">
            <FileEdit className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              {drafts && drafts.length > 0 
                ? 'Brak treści spełniających kryteria'
                : 'Brak treści w tym planie'}
            </h3>
            <p className="text-muted-foreground">
              {drafts && drafts.length > 0
                ? 'Spróbuj zmienić kryteria wyszukiwania'
                : statusMessage.showProgress 
                  ? 'Treści pojawią się tutaj po zakończeniu generowania'
                  : 'Treści pojawią się tutaj po zatwierdzeniu tematów'}
            </p>
          </Card>
        ) : (
          filteredDrafts.map((draft, index) => (
            <motion.div
              key={draft.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card 
                className="p-6 hover-lift cursor-pointer"
                onClick={() => handleDraftClick(draft.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start gap-4">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        <FileEdit className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-foreground mb-2">
                          {draft.suggested_topic?.title || draft.topic || 'Bez tytułu'}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            <span>
                              {draft.scheduled_for 
                                ? format(new Date(draft.scheduled_for), 'dd MMM yyyy', { locale: pl })
                                : 'Nie zaplanowano'}
                            </span>
                          </div>
                          <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${getStatusColor(draft.status)}`}>
                            {getStatusIcon(draft.status)}
                            <span className="text-xs font-medium">
                              {draft.status === 'draft' ? 'Szkic' :
                               draft.status === 'review' ? 'W recenzji' :
                               draft.status === 'approved' ? 'Zatwierdzony' : 'Odrzucony'}
                            </span>
                          </div>
                        </div>
                        {(draft.suggested_topic?.category || draft.content_type) && (
                          <div className="mt-2">
                            <span className="text-xs text-muted-foreground">Kategoria: </span>
                            <span className="text-sm font-medium text-foreground">
                              {draft.suggested_topic?.category || draft.content_type}
                            </span>
                          </div>
                        )}
                        {/* Liczba wariantów */}
                        {draft.variants_count && draft.variants_count > 0 && (
                          <div className="mt-3 flex items-center gap-2">
                            <MessageSquare className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm text-muted-foreground">
                              {draft.variants_count} {draft.variants_count === 1 ? 'wariant' : 'wariantów'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                </div>
              </Card>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}