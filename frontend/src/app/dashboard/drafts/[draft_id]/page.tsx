'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  ArrowLeft,
  Save,
  CheckCircle,
  XCircle,
  MessageSquare,
  RefreshCw,
  Send,
  Linkedin,
  Facebook,
  Globe,
  Twitter,
  FileText,
  AlertCircle
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { ContentVariant, ContentStatus } from '@/types'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'

const platformIcons = {
  linkedin: Linkedin,
  facebook: Facebook,
  twitter: Twitter,
  blog: Globe,
  website: FileText,
} as const

export default function DraftDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const toast = useToast()
  const draftId = params?.draft_id ? parseInt(params.draft_id as string) : null

  const [editedVariants, setEditedVariants] = useState<Record<number, string>>({})
  const [feedbackDialog, setFeedbackDialog] = useState<{ open: boolean; variantId: number | null }>({
    open: false,
    variantId: null
  })
  const [feedbackText, setFeedbackText] = useState('')

  // Pobieranie wariantów dla draftu
  const { data: variants, isLoading } = useQuery({
    queryKey: ['content-variants', draftId],
    queryFn: async () => {
      if (!draftId) return []
      const response = await api.contentDrafts.getVariants(draftId)
      return response
    },
    enabled: !!draftId
  })

  // Mutacje
  const updateVariantMutation = useMutation({
    mutationFn: async ({ variantId, content }: { variantId: number; content: string }) => {
      return await api.contentVariants.update(variantId, { content_text: content })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-variants', draftId] })
      toast.success('Treść wariantu została zaktualizowana')
    }
  })

  const updateStatusMutation = useMutation({
    mutationFn: async ({ variantId, status }: { variantId: number; status: ContentStatus }) => {
      return await api.contentVariants.updateStatus(variantId, status)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-variants', draftId] })
      toast.success('Status wariantu został zaktualizowany')
    }
  })

  const requestRevisionMutation = useMutation({
    mutationFn: async ({ variantId, feedback }: { variantId: number; feedback: string }) => {
      return await api.contentVariants.requestRevision(variantId, feedback)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-variants', draftId] })
      toast.success('Feedback został zapisany')
      setFeedbackDialog({ open: false, variantId: null })
      setFeedbackText('')
    }
  })

  const regenerateVariantMutation = useMutation({
    mutationFn: async (variantId: number) => {
      return await api.contentVariants.regenerate(variantId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-variants', draftId] })
      toast.success('Nowa wersja wariantu jest generowana')
    }
  })

  // Grupowanie wariantów według platformy
  const variantsByPlatform = variants?.reduce((acc, variant) => {
    const platform = variant.platform || 'other'
    if (!acc[platform]) acc[platform] = []
    acc[platform].push(variant)
    return acc
  }, {} as Record<string, ContentVariant[]>) || {}

  const handleSaveChanges = (variantId: number) => {
    const content = editedVariants[variantId]
    if (content) {
      updateVariantMutation.mutate({ variantId, content })
    }
  }

  const handleStatusChange = (variantId: number, status: ContentStatus) => {
    updateStatusMutation.mutate({ variantId, status })
  }

  const handleRequestRevision = () => {
    if (feedbackDialog.variantId && feedbackText.trim()) {
      requestRevisionMutation.mutate({
        variantId: feedbackDialog.variantId,
        feedback: feedbackText
      })
    }
  }

  const canFinalizePlan = variants?.every(v => v.status === 'approved')

  const getStatusBadge = (status: ContentStatus) => {
    const statusConfig = {
      draft: { label: 'Szkic', className: 'bg-muted text-muted-foreground' },
      review: { label: 'W recenzji', className: 'bg-yellow-50 text-yellow-600' },
      approved: { label: 'Zatwierdzony', className: 'bg-green-50 text-green-600' },
      rejected: { label: 'Odrzucony', className: 'bg-destructive/10 text-destructive' }
    }
    const config = statusConfig[status] || statusConfig.draft
    return <Badge className={config.className}>{config.label}</Badge>
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (!variants || variants.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center">
          <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">
            Brak wariantów
          </h3>
          <p className="text-muted-foreground mb-4">
            Nie znaleziono wariantów dla tego draftu
          </p>
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Wróć
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-subtle p-6">
      <div className="max-w-7xl mx-auto space-y-6">
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
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  Warianty treści
                </h1>
                <p className="text-muted-foreground">
                  Draft #{draftId} - {variants[0]?.content_draft?.topic || 'Bez tematu'}
                </p>
              </div>
            </div>
            <Button
              variant="default"
              size="lg"
              disabled={!canFinalizePlan}
              onClick={() => {
                toast.success('Wszystkie warianty zostały zatwierdzone')
              }}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Zakończ i zatwierdź harmonogram
            </Button>
          </div>
        </motion.div>

        {/* Tabs dla platform */}
        <Tabs defaultValue={Object.keys(variantsByPlatform)[0]} className="space-y-4">
          <TabsList className="grid w-full grid-cols-auto gap-2">
            {Object.keys(variantsByPlatform).map((platform) => {
              const Icon = platformIcons[platform as keyof typeof platformIcons] || FileText
              return (
                <TabsTrigger key={platform} value={platform} className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  {platform.charAt(0).toUpperCase() + platform.slice(1)}
                </TabsTrigger>
              )
            })}
          </TabsList>

          {Object.entries(variantsByPlatform).map(([platform, platformVariants]) => (
            <TabsContent key={platform} value={platform} className="space-y-4">
              {platformVariants.map((variant) => (
                <motion.div
                  key={variant.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-foreground">
                          Wariant #{variant.id}
                        </h3>
                        {getStatusBadge(variant.status)}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => regenerateVariantMutation.mutate(variant.id)}
                          disabled={regenerateVariantMutation.isPending}
                        >
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Wygeneruj nową wersję
                        </Button>
                      </div>
                    </div>

                    {/* Edytor treści */}
                    <div className="space-y-4">
                      <Textarea
                        value={editedVariants[variant.id] || variant.content_text}
                        onChange={(e) => setEditedVariants({
                          ...editedVariants,
                          [variant.id]: e.target.value
                        })}
                        className="min-h-[200px] font-mono text-sm"
                        placeholder="Treść wariantu..."
                      />

                      {/* Przyciski akcji */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => handleSaveChanges(variant.id)}
                            disabled={!editedVariants[variant.id] || updateVariantMutation.isPending}
                          >
                            <Save className="h-4 w-4 mr-2" />
                            Zapisz zmiany
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setFeedbackDialog({ open: true, variantId: variant.id })}
                          >
                            <MessageSquare className="h-4 w-4 mr-2" />
                            Poproś o poprawki
                          </Button>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleStatusChange(variant.id, 'rejected')}
                            disabled={variant.status === 'rejected'}
                          >
                            <XCircle className="h-4 w-4 mr-2" />
                            Odrzuć
                          </Button>
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => handleStatusChange(variant.id, 'approved')}
                            disabled={variant.status === 'approved'}
                          >
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Akceptuj
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </TabsContent>
          ))}
        </Tabs>

        {/* Dialog feedbacku */}
        <Dialog open={feedbackDialog.open} onOpenChange={(open) => 
          setFeedbackDialog({ ...feedbackDialog, open })
        }>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Poproś o poprawki</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <Textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="Opisz jakie zmiany są potrzebne..."
                className="min-h-[150px]"
              />
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setFeedbackDialog({ open: false, variantId: null })
                  setFeedbackText('')
                }}
              >
                Anuluj
              </Button>
              <Button
                onClick={handleRequestRevision}
                disabled={!feedbackText.trim() || requestRevisionMutation.isPending}
              >
                <Send className="h-4 w-4 mr-2" />
                Wyślij feedback
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}