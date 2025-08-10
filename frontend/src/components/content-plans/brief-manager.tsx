'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, FileText, X, AlertCircle, Loader2, Sparkles, Brain } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

import { api } from '@/lib/api'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { cn } from '@/lib/utils'
import { BriefAnalysisPreview } from './brief-analysis-preview'

interface BriefManagerProps {
  contentPlanId: number
  isReadOnly?: boolean
}

interface ContentBrief {
  id: number
  title: string
  description?: string
  priority_level: number
  file_path?: string
  file_type?: string
  key_topics?: string[]
  ai_analysis?: any
  created_at: string
}

export function BriefManager({ contentPlanId, isReadOnly = false }: BriefManagerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedBrief, setSelectedBrief] = useState<ContentBrief | null>(null)
  const [showAnalysisDialog, setShowAnalysisDialog] = useState(false)
  const queryClient = useQueryClient()
  const { success: toastSuccess, error: toastError } = useToast()

  // Fetch briefs
  const { data: briefs = [], isLoading } = useQuery({
    queryKey: ['contentBriefs', contentPlanId],
    queryFn: async () => {
      return await api.contentPlans.getBriefs(contentPlanId)
    },
    enabled: !!contentPlanId
  })

  // Create brief mutation
  const createBriefMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      return await api.contentPlans.createBrief(contentPlanId, formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentBriefs', contentPlanId] })
      toastSuccess('Brief został dodany pomyślnie')
      setIsOpen(false)
    },
    onError: (error: any) => {
      toastError(error.response?.data?.detail || 'Błąd podczas dodawania briefu')
    }
  })

  // Delete brief mutation
  const deleteBriefMutation = useMutation({
    mutationFn: async (briefId: number) => {
      await api.contentPlans.deleteBrief(briefId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contentBriefs', contentPlanId] })
      toastSuccess('Brief został usunięty')
    },
    onError: (error: any) => {
      toastError(error.response?.data?.detail || 'Błąd podczas usuwania briefu')
    }
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    createBriefMutation.mutate(formData)
  }

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'text-red-600 bg-red-100'
    if (priority >= 5) return 'text-yellow-600 bg-yellow-100'
    return 'text-blue-600 bg-blue-100'
  }

  const getPriorityLabel = (priority: number) => {
    if (priority >= 8) return 'Wysoki'
    if (priority >= 5) return 'Średni'
    return 'Niski'
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Briefy treściowe</h3>
          <p className="text-sm text-gray-600 mt-1">
            Dodaj briefy z ważnymi informacjami, które AI uwzględni przy generowaniu treści
          </p>
        </div>
        {!isReadOnly && (
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="gap-2">
                <Upload className="w-4 h-4" />
                Dodaj brief
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Dodaj nowy brief</DialogTitle>
                <DialogDescription>
                  Prześlij plik z briefem lub opisz go tekstowo. AI przeanalizuje treść i wykorzysta podczas generowania.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  name="title"
                  label="Tytuł briefu"
                  placeholder="np. Kluczowe wydarzenia Q1 2025"
                  required
                />
                <Textarea
                  name="description"
                  label="Opis (opcjonalny)"
                  placeholder="Dodatkowy kontekst..."
                  rows={3}
                />
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Priorytet
                  </label>
                  <input
                    type="range"
                    name="priority_level"
                    min="1"
                    max="10"
                    defaultValue="5"
                    className="w-full mt-2"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Niski</span>
                    <span>Średni</span>
                    <span>Wysoki</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Plik briefu (opcjonalny)
                  </label>
                  <input
                    type="file"
                    name="file"
                    accept=".pdf,.doc,.docx,.txt,.html,.rtf"
                    className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    PDF, Word, TXT, HTML lub RTF (maks. 10MB)
                  </p>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsOpen(false)}
                  >
                    Anuluj
                  </Button>
                  <Button
                    type="submit"
                    disabled={createBriefMutation.isPending}
                    className="gap-2"
                  >
                    {createBriefMutation.isPending && (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    )}
                    Dodaj brief
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Briefs list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : briefs.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Brak briefów</p>
          <p className="text-sm text-gray-400 mt-1">
            Dodaj briefy, aby AI mogło lepiej dostosować treści
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {briefs.map((brief: ContentBrief, index: number) => (
              <motion.div
                key={brief.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ delay: index * 0.05 }}
                className={cn(
                  "relative p-4 rounded-lg border",
                  selectedBrief?.id === brief.id
                    ? "border-blue-300 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 cursor-pointer" onClick={() => setSelectedBrief(brief)}>
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <h4 className="font-medium text-gray-900">{brief.title}</h4>
                      <Badge className={cn("text-xs", getPriorityColor(brief.priority_level))}>
                        {getPriorityLabel(brief.priority_level)}
                      </Badge>
                    </div>
                    {brief.description && (
                      <p className="text-sm text-gray-600 mb-2">{brief.description}</p>
                    )}
                    {brief.key_topics && brief.key_topics.length > 0 && (
                      <div className="flex items-center gap-2 flex-wrap">
                        <Sparkles className="w-4 h-4 text-yellow-500" />
                        <span className="text-xs text-gray-500">Kluczowe tematy:</span>
                        {brief.key_topics.slice(0, 3).map((topic, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                        {brief.key_topics.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{brief.key_topics.length - 3} więcej
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  {!isReadOnly && (
                    <button
                      onClick={() => deleteBriefMutation.mutate(brief.id)}
                      className="ml-4 p-1 text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
                
                {/* Expanded details */}
                <AnimatePresence>
                  {selectedBrief?.id === brief.id && brief.ai_analysis && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-4 pt-4 border-t border-gray-200"
                    >
                      <div className="space-y-3 text-sm">
                        {brief.ai_analysis.important_dates?.length > 0 && (
                          <div>
                            <span className="font-medium text-gray-700">Ważne daty:</span>
                            <ul className="list-disc list-inside text-gray-600 mt-1">
                              {brief.ai_analysis.important_dates.map((date: string, i: number) => (
                                <li key={i}>{date}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {brief.ai_analysis.context_summary && (
                          <div>
                            <span className="font-medium text-gray-700">Podsumowanie:</span>
                            <p className="text-gray-600 mt-1">{brief.ai_analysis.context_summary}</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
      
      {/* Show analysis button when briefs exist */}
      {briefs.length > 0 && (
        <div className="mt-4 flex justify-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAnalysisDialog(true)}
            className="gap-2"
          >
            <Brain className="w-4 h-4" />
            Zobacz analizę briefów
          </Button>
        </div>
      )}

      {/* Brief Analysis Dialog */}
      <Dialog open={showAnalysisDialog} onOpenChange={setShowAnalysisDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Analiza Briefów - Deep Reasoning</DialogTitle>
            <DialogDescription>
              Zobacz jak AI interpretuje i analizuje zawartość briefów
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            <BriefAnalysisPreview 
              briefId={selectedBrief?.id}
              briefContent={selectedBrief?.description}
            />
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  )
}