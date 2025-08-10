'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Calendar, FileText, Settings, Clock, CheckCircle, XCircle, AlertCircle, Loader2, RefreshCw, Trash2, MoreVertical } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

import { api } from '@/lib/api'
import { ContentPlan } from '@/types'
import { CreatePlanWizard } from '@/components/content-plans/create-plan-wizard'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/cards'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

interface ContentPlansManagerProps {
  organizationId: number
  organizationName: string
}

export function ContentPlansManager({ organizationId, organizationName }: ContentPlansManagerProps) {
  const [showCreateWizard, setShowCreateWizard] = useState(false)
  const [deleteContentDialog, setDeleteContentDialog] = useState<{ open: boolean; planId: number | null }>({ open: false, planId: null })
  const [deletePlanDialog, setDeletePlanDialog] = useState<{ open: boolean; planId: number | null }>({ open: false, planId: null })
  const [regenerateDialog, setRegenerateDialog] = useState<{ open: boolean; planId: number | null }>({ open: false, planId: null })
  const queryClient = useQueryClient()
  
  console.log('ContentPlansManager - organizationId:', organizationId, 'organizationName:', organizationName)

  const { data: contentPlans, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['contentPlans', organizationId],
    queryFn: async () => {
      const plans = await api.contentPlans.list(organizationId)
      return plans || []
    },
    enabled: !!organizationId
  })

  // Obsługa błędów
  if (isError) {
    console.error('Error loading content plans:', error)
  }

  // Mutacja do generowania propozycji
  const generateTopicsMutation = useMutation({
    mutationFn: (planId: number) => api.contentPlans.generateTopics(planId),
    onSuccess: () => {
      // Unieważnienie i odświeżenie zapytania
      queryClient.invalidateQueries({ queryKey: ['contentPlans', organizationId] })
    },
    onError: (error) => {
      console.error('Error generating topics:', error)
    },
  })

  // Mutacja do regeneracji całej treści
  const regenerateContentMutation = useMutation({
    mutationFn: (planId: number) => api.contentPlans.regenerateAllContent(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentPlans', organizationId] })
    },
    onError: (error) => {
      console.error('Error regenerating content:', error)
    },
  })

  // Mutacja do usuwania wygenerowanej treści
  const deleteGeneratedContentMutation = useMutation({
    mutationFn: (planId: number) => api.contentPlans.deleteGeneratedContent(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentPlans', organizationId] })
    },
    onError: (error) => {
      console.error('Error deleting generated content:', error)
    },
  })

  // Mutacja do trwałego usuwania planu
  const hardDeletePlanMutation = useMutation({
    mutationFn: (planId: number) => api.contentPlans.hardDelete(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentPlans', organizationId] })
    },
    onError: (error) => {
      console.error('Error hard deleting plan:', error)
    },
  })

  const handleCreateSuccess = (planId: number) => {
    console.log('Content plan created successfully:', planId)
    setShowCreateWizard(false)
    refetch()
  }

  const handleCreateCancel = () => {
    setShowCreateWizard(false)
  }

  const handleGenerateTopics = (planId: number) => {
    generateTopicsMutation.mutate(planId)
  }

  const handleRegenerateContent = () => {
    if (regenerateDialog.planId) {
      regenerateContentMutation.mutate(regenerateDialog.planId, {
        onSuccess: () => {
          setRegenerateDialog({ open: false, planId: null })
        }
      })
    }
  }

  const handleDeleteGeneratedContent = () => {
    if (deleteContentDialog.planId) {
      deleteGeneratedContentMutation.mutate(deleteContentDialog.planId, {
        onSuccess: () => {
          setDeleteContentDialog({ open: false, planId: null })
        }
      })
    }
  }

  const handleHardDeletePlan = () => {
    if (deletePlanDialog.planId) {
      hardDeletePlanMutation.mutate(deletePlanDialog.planId, {
        onSuccess: () => {
          setDeletePlanDialog({ open: false, planId: null })
        }
      })
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'new':
        return <Clock className="w-4 h-4 text-blue-500" />
      case 'generating_topics':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      case 'pending_blog_topic_approval':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'complete':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      default:
        return <XCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const formatStatus = (status: string) => {
    switch (status) {
      case 'new':
        return 'Nowy'
      case 'generating_topics':
        return 'Generowanie tematów'
      case 'pending_blog_topic_approval':
        return 'Oczekuje zatwierdzenia'
      case 'complete':
        return 'Zakończony'
      default:
        return status
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (showCreateWizard) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="min-h-screen bg-gray-50 pt-6"
      >
        <CreatePlanWizard
          organizationId={organizationId}
          onSuccess={handleCreateSuccess}
          onCancel={handleCreateCancel}
        />
      </motion.div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Plany Treści</h1>
          <p className="text-gray-600">
            Zarządzaj planami treści dla organizacji{' '}
            <span className="font-medium">{organizationName}</span>
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowCreateWizard(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Stwórz nowy plan
        </motion.button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner />
        </div>
      ) : isError ? (
        <div className="text-center py-12">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Wystąpił błąd podczas ładowania planów treści</p>
          {error && (
            <p className="text-sm text-red-500 mt-2">
              {(error as any)?.response?.data?.detail || (error as any)?.message || 'Nieznany błąd'}
            </p>
          )}
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Spróbuj ponownie
          </button>
        </div>
      ) : !contentPlans || contentPlans.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Brak planów treści
          </h3>
          <p className="text-gray-600 mb-6">
            Rozpocznij tworzenie treści, tworząc swój pierwszy plan
          </p>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowCreateWizard(true)}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mx-auto"
          >
            <Plus className="w-5 h-5" />
            Stwórz pierwszy plan
          </motion.button>
        </div>
      ) : (
        // Tabela z planami treści z użyciem komponentów Shadcn/ui
        <Card className="overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="px-6 py-3">
                  Okres Planu
                </TableHead>
                <TableHead className="px-6 py-3">
                  Status
                </TableHead>
                <TableHead className="px-6 py-3">
                  Utworzono
                </TableHead>
                <TableHead className="px-6 py-3">
                  Akcje
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {contentPlans.map((plan: ContentPlan, index: number) => (
                <TableRow
                  key={plan.id}
                  className="hover:bg-gray-50"
                >
                  <TableCell className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/dashboard/organization/${organizationId}/content-plans/${plan.id}`}
                      className="flex items-center hover:text-blue-600 transition-colors"
                    >
                      <Calendar className="w-5 h-5 text-blue-500 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {plan.plan_period}
                        </div>
                        <div className="text-sm text-gray-500">
                          {plan.blog_posts_quota} blogów • {plan.sm_posts_quota} SM
                        </div>
                      </div>
                    </Link>
                  </TableCell>
                  <TableCell className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(plan.status)}
                      <Badge variant={plan.status as any}>
                        {formatStatus(plan.status)}
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(plan.created_at)}
                  </TableCell>
                  <TableCell className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center gap-2">
                      {plan.status === 'new' ? (
                        <Button
                          onClick={() => handleGenerateTopics(plan.id)}
                          disabled={generateTopicsMutation.isPending}
                          size="sm"
                          className="gap-2"
                        >
                          {generateTopicsMutation.isPending ? (
                            <>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              Generowanie...
                            </>
                          ) : (
                            <>
                              <AlertCircle className="w-4 h-4" />
                              Generuj Propozycje
                            </>
                          )}
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          className="gap-2"
                          asChild
                        >
                          <Link href={`/dashboard/organization/${organizationId}/content-plans/${plan.id}`}>
                            <FileText className="w-4 h-4" />
                            Zobacz Szczegóły
                          </Link>
                        </Button>
                      )}
                      
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="p-2">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => setRegenerateDialog({ open: true, planId: plan.id })}
                            className="gap-2"
                          >
                            <RefreshCw className="w-4 h-4" />
                            Regeneruj całą treść
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => setDeleteContentDialog({ open: true, planId: plan.id })}
                            className="gap-2 text-orange-600"
                          >
                            <Trash2 className="w-4 h-4" />
                            Usuń wygenerowaną treść
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => setDeletePlanDialog({ open: true, planId: plan.id })}
                            className="gap-2 text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                            Usuń cały plan
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* Alert Dialogs */}
      <AlertDialog open={regenerateDialog.open} onOpenChange={(open) => setRegenerateDialog({ open, planId: regenerateDialog.planId })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Regeneruj treść planu</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz ponownie wygenerować całą treść dla tego planu? 
              Wszystkie obecne tematy i treści zostaną zdezaktywowane, a nowe zostaną wygenerowane od początku.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Anuluj</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleRegenerateContent}
              disabled={regenerateContentMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {regenerateContentMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Regenerowanie...
                </>
              ) : (
                'Regeneruj treść'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={deleteContentDialog.open} onOpenChange={(open) => setDeleteContentDialog({ open, planId: deleteContentDialog.planId })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Usuń wygenerowaną treść</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz usunąć całą wygenerowaną treść dla tego planu? 
              Usunięte zostaną wszystkie tematy, szkice i warianty. Sam plan pozostanie, a status zostanie zresetowany.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Anuluj</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteGeneratedContent}
              disabled={deleteGeneratedContentMutation.isPending}
              className="bg-orange-600 hover:bg-orange-700"
            >
              {deleteGeneratedContentMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Usuwanie...
                </>
              ) : (
                'Usuń treść'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={deletePlanDialog.open} onOpenChange={(open) => setDeletePlanDialog({ open, planId: deletePlanDialog.planId })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Usuń plan treści</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz trwale usunąć ten plan treści? 
              Ta operacja jest nieodwracalna i usunie plan oraz wszystkie powiązane dane, w tym tematy, treści, harmonogramy i briefy.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Anuluj</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleHardDeletePlan}
              disabled={hardDeletePlanMutation.isPending}
              className="bg-red-600 hover:bg-red-700"
            >
              {hardDeletePlanMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Usuwanie...
                </>
              ) : (
                'Usuń plan'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
} 