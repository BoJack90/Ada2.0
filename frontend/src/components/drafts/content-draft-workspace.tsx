'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog'
import { 
  CheckCircle, 
  XCircle, 
  MessageCircle, 
  RefreshCw, 
  Loader2, 
  Edit3, 
  Save,
  Calendar,
  CheckCircle2
} from 'lucide-react'
import { api } from '@/lib/api'
import { ContentDraft, ContentVariant } from '@/types'

interface ContentDraftWorkspaceProps {
  draft: ContentDraft
  variants: ContentVariant[]
  isLoading?: boolean
}

export function ContentDraftWorkspace({ draft, variants, isLoading }: ContentDraftWorkspaceProps) {
  const [editingVariants, setEditingVariants] = useState<Record<number, string>>({})
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackVariantId, setFeedbackVariantId] = useState<number | null>(null)
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false)
  const queryClient = useQueryClient()

  // Mutacje
  const updateStatusMutation = useMutation({
    mutationFn: ({ variantId, status }: { variantId: number, status: 'pending_approval' | 'approved' | 'rejected' | 'needs_revision' }) =>
      api.contentVariants.updateStatus(variantId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentVariants', draft.id] })
    },
    onError: (error) => {
      console.error('Error updating status:', error)
    },
  })

  const updateContentMutation = useMutation({
    mutationFn: ({ variantId, content_text }: { variantId: number, content_text: string }) =>
      api.contentVariants.updateContent(variantId, { content_text }),
    onSuccess: (updatedVariant) => {
      queryClient.invalidateQueries({ queryKey: ['contentVariants', draft.id] })
      setEditingVariants(prev => {
        const { [updatedVariant.id]: _, ...rest } = prev
        return rest
      })
    },
    onError: (error) => {
      console.error('Error updating content:', error)
    },
  })

  const requestRevisionMutation = useMutation({
    mutationFn: ({ variantId, feedback }: { variantId: number, feedback: string }) =>
      api.contentVariants.requestRevision(variantId, { feedback }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentVariants', draft.id] })
      setShowFeedbackDialog(false)
      setFeedbackText('')
      setFeedbackVariantId(null)
    },
    onError: (error) => {
      console.error('Error requesting revision:', error)
    },
  })

  const regenerateVariantMutation = useMutation({
    mutationFn: (variantId: number) =>
      api.contentVariants.regenerate(variantId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentVariants', draft.id] })
    },
    onError: (error) => {
      console.error('Error regenerating variant:', error)
    },
  })

  const finalizeDraftMutation = useMutation({
    mutationFn: () =>
      api.contentDrafts.updateStatus(draft.id, { status: 'approved' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentDraft', draft.id] })
      queryClient.invalidateQueries({ queryKey: ['contentVariants', draft.id] })
    },
    onError: (error) => {
      console.error('Error finalizing draft:', error)
    },
  })

  // Handler functions
  const handleApprove = (variant: ContentVariant) => {
    updateStatusMutation.mutate({ variantId: variant.id, status: 'approved' })
  }

  const handleReject = (variant: ContentVariant) => {
    updateStatusMutation.mutate({ variantId: variant.id, status: 'rejected' })
  }

  const handleRequestRevision = (variant: ContentVariant) => {
    setFeedbackVariantId(variant.id)
    setShowFeedbackDialog(true)
  }

  const handleSubmitFeedback = () => {
    if (feedbackVariantId && feedbackText.trim()) {
      requestRevisionMutation.mutate({
        variantId: feedbackVariantId,
        feedback: feedbackText.trim(),
      })
    }
  }

  const handleRegenerateVariant = (variant: ContentVariant) => {
    regenerateVariantMutation.mutate(variant.id)
  }

  const handleFinalizeDraft = () => {
    finalizeDraftMutation.mutate()
  }

  const handleStartEditing = (variant: ContentVariant) => {
    setEditingVariants(prev => ({
      ...prev,
      [variant.id]: variant.content_text
    }))
  }

  const handleSaveEdit = (variantId: number) => {
    const newContent = editingVariants[variantId]
    if (newContent && newContent.trim()) {
      updateContentMutation.mutate({
        variantId,
        content_text: newContent.trim()
      })
    }
  }

  const handleCancelEdit = (variantId: number) => {
    setEditingVariants(prev => {
      const { [variantId]: _, ...rest } = prev
      return rest
    })
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="complete" className="bg-green-100 text-green-800">Zaakceptowany</Badge>
      case 'rejected':
        return <Badge variant="error">Odrzucony</Badge>
      case 'needs_revision':
        return <Badge variant="generating_topics" className="bg-yellow-100 text-yellow-800">Wymaga rewizji</Badge>
      case 'pending_approval':
      default:
        return <Badge variant="default">Oczekuje zatwierdzenia</Badge>
    }
  }

  const getPlatformName = (platform: string) => {
    const platforms = {
      linkedin: 'LinkedIn',
      facebook: 'Facebook',
      instagram: 'Instagram',
      wordpress: 'WordPress',
      blog: 'Blog',
    }
    return platforms[platform as keyof typeof platforms] || platform
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  // Grupuj warianty według platform
  const variantsByPlatform = variants.reduce((acc, variant) => {
    if (!acc[variant.platform_name]) {
      acc[variant.platform_name] = []
    }
    acc[variant.platform_name].push(variant)
    return acc
  }, {} as Record<string, ContentVariant[]>)

  // Sprawdź czy wszystkie warianty są zatwierdzone
  const allVariantsApproved = variants.length > 0 && variants.every(v => v.status === 'approved')

  return (
    <div className="space-y-6">
      {/* Informacje o draft */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Pulpit Roboczy Treści</span>
            <Badge variant="default">Draft #{draft.id}</Badge>
          </CardTitle>
          <CardDescription>
            {draft.suggested_topic?.title || `Content Draft #${draft.id}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm">
                <strong>Utworzono:</strong> {new Date(draft.created_at).toLocaleDateString('pl-PL')}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm">
                <strong>Status:</strong> {getStatusBadge(draft.status)}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm">
                <strong>Warianty:</strong> {variants.length}
              </span>
            </div>
          </div>
          
          {draft.suggested_topic?.description && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-sm mb-2">Opis tematu:</h4>
              <p className="text-sm text-gray-600">
                {draft.suggested_topic.description}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Warianty treści w zakładkach */}
      <Tabs defaultValue={Object.keys(variantsByPlatform)[0]} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          {Object.keys(variantsByPlatform).map((platform) => (
            <TabsTrigger key={platform} value={platform} className="flex items-center gap-2">
              {getPlatformName(platform)}
              <Badge variant="default" className="text-xs">
                {variantsByPlatform[platform].length}
              </Badge>
            </TabsTrigger>
          ))}
        </TabsList>

        {Object.entries(variantsByPlatform).map(([platform, platformVariants]) => (
          <TabsContent key={platform} value={platform} className="space-y-4">
            {platformVariants.map((variant) => (
              <Card key={variant.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">
                      {getPlatformName(platform)} - Wersja {variant.version}
                    </CardTitle>
                    {getStatusBadge(variant.status)}
                  </div>
                  <CardDescription>
                    Utworzono: {new Date(variant.created_at).toLocaleDateString('pl-PL', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Treść wariantu - edytowalna */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium">Treść:</h5>
                      {!editingVariants[variant.id] && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleStartEditing(variant)}
                          className="gap-1"
                        >
                          <Edit3 className="h-3 w-3" />
                          Edytuj
                        </Button>
                      )}
                    </div>
                    
                    {editingVariants[variant.id] !== undefined ? (
                      <div className="space-y-2">
                        <Textarea
                          value={editingVariants[variant.id]}
                          onChange={(e) => setEditingVariants(prev => ({
                            ...prev,
                            [variant.id]: e.target.value
                          }))}
                          className="min-h-[150px]"
                          placeholder="Wprowadź treść wariantu..."
                        />
                        <div className="flex gap-2">
                          <Button
                            onClick={() => handleSaveEdit(variant.id)}
                            disabled={updateContentMutation.isPending}
                            size="sm"
                            className="gap-1"
                          >
                            {updateContentMutation.isPending ? (
                              <Loader2 className="h-3 w-3 animate-spin" />
                            ) : (
                              <Save className="h-3 w-3" />
                            )}
                            Zapisz Zmiany
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => handleCancelEdit(variant.id)}
                            size="sm"
                          >
                            Anuluj
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-gray-50 p-4 rounded-lg border">
                        <pre className="whitespace-pre-wrap text-sm font-mono">
                          {variant.content_text}
                        </pre>
                      </div>
                    )}
                  </div>

                  {/* Przyciski akcji */}
                  {variant.status === 'pending_approval' && (
                    <div className="flex flex-wrap gap-2">
                      <Button
                        onClick={() => handleApprove(variant)}
                        disabled={updateStatusMutation.isPending}
                        className="bg-green-600 hover:bg-green-700 text-white gap-1"
                      >
                        {updateStatusMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle className="h-4 w-4" />
                        )}
                        Akceptuj
                      </Button>
                      <Button
                        onClick={() => handleReject(variant)}
                        disabled={updateStatusMutation.isPending}
                        variant="destructive"
                        className="gap-1"
                      >
                        {updateStatusMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <XCircle className="h-4 w-4" />
                        )}
                        Odrzuć
                      </Button>
                      <Button
                        onClick={() => handleRequestRevision(variant)}
                        disabled={requestRevisionMutation.isPending}
                        variant="outline"
                        className="gap-1"
                      >
                        <MessageCircle className="h-4 w-4" />
                        Poproś o Poprawki
                      </Button>
                      <Button
                        onClick={() => handleRegenerateVariant(variant)}
                        disabled={regenerateVariantMutation.isPending}
                        variant="outline"
                        className="gap-1"
                      >
                        {regenerateVariantMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <RefreshCw className="h-4 w-4" />
                        )}
                        Wygeneruj Nową Wersję
                      </Button>
                    </div>
                  )}

                  {/* Status indicators */}
                  {variant.status === 'needs_revision' && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <MessageCircle className="h-4 w-4 text-yellow-600" />
                        <span className="text-sm text-yellow-800">
                          Ten wariant wymaga rewizji i zostanie automatycznie przetworzony.
                        </span>
                      </div>
                    </div>
                  )}

                  {variant.status === 'approved' && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-800">
                          Ten wariant został zaakceptowany i jest gotowy do publikacji.
                        </span>
                      </div>
                    </div>
                  )}

                  {variant.status === 'rejected' && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <XCircle className="h-4 w-4 text-red-600" />
                        <span className="text-sm text-red-800">
                          Ten wariant został odrzucony.
                        </span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        ))}
      </Tabs>

      {/* Finalizacja planu */}
      <Card className="border-2 border-dashed border-gray-300">
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <CheckCircle2 className={`h-6 w-6 ${allVariantsApproved ? 'text-green-600' : 'text-gray-400'}`} />
              <h3 className="text-lg font-semibold">
                Finalizacja Harmonogramu
              </h3>
            </div>
            
            {allVariantsApproved ? (
              <div className="space-y-3">
                <p className="text-green-700 text-sm">
                  ✅ Wszystkie warianty zostały zatwierdzone i są gotowe do publikacji
                </p>
                <Button 
                  size="lg" 
                  className="bg-green-600 hover:bg-green-700 text-white gap-2"
                  onClick={handleFinalizeDraft}
                  disabled={finalizeDraftMutation.isPending}
                >
                  {finalizeDraftMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Calendar className="h-4 w-4" />
                  )}
                  Zakończ Pracę i Zatwierdź Harmonogram
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-gray-600 text-sm">
                  Aby sfinalizować harmonogram, wszystkie warianty muszą mieć status "Zaakceptowany"
                </p>
                <div className="text-sm text-gray-500">
                  Status wariantów: {variants.filter(v => v.status === 'approved').length} / {variants.length} zatwierdzonych
                </div>
                <Button 
                  size="lg" 
                  disabled
                  variant="outline"
                  className="gap-2"
                >
                  <Calendar className="h-4 w-4" />
                  Zakończ Pracę i Zatwierdź Harmonogram
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Dialog dla feedback */}
      <Dialog open={showFeedbackDialog} onOpenChange={setShowFeedbackDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Poproś o Poprawki</DialogTitle>
            <DialogDescription>
              Opisz co należy poprawić w tym wariancie treści. Twój feedback zostanie użyty do wygenerowania ulepszonej wersji.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Textarea
              placeholder="Opisz konkretne zmiany, które chcesz wprowadzić..."
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              className="min-h-[100px]"
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowFeedbackDialog(false)}
            >
              Anuluj
            </Button>
            <Button
              onClick={handleSubmitFeedback}
              disabled={!feedbackText.trim() || requestRevisionMutation.isPending}
            >
              {requestRevisionMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <MessageCircle className="h-4 w-4 mr-2" />
              )}
              Wyślij Feedback
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
