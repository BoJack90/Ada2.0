'use client'

import { useEffect, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Brain, Loader2, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

interface AutoGenerateTopicsProps {
  planId: number
  planMetadata?: any
  onSuccess?: () => void
  onError?: (error: any) => void
}

export function AutoGenerateTopics({ planId, planMetadata, onSuccess, onError }: AutoGenerateTopicsProps) {
  const [generationStarted, setGenerationStarted] = useState(false)
  const [generationMethod, setGenerationMethod] = useState<'standard' | 'deep_reasoning'>('standard')
  const [taskId, setTaskId] = useState<string | null>(null)

  // Determine generation method from meta_data
  useEffect(() => {
    if (planMetadata?.generation_method) {
      setGenerationMethod(planMetadata.generation_method)
    }
  }, [planMetadata])

  // Standard generation mutation
  const standardGenerateMutation = useMutation({
    mutationFn: () => api.contentPlans.generateTopics(planId),
    onSuccess: (data) => {
      setTaskId(data.task_id)
      onSuccess?.()
    },
    onError: (error) => {
      console.error('Standard generation error:', error)
      onError?.(error)
    }
  })

  // Deep reasoning generation mutation
  const deepReasoningMutation = useMutation({
    mutationFn: () => api.contentPlans.generateTopicsWithReasoning(planId, {
      forceRegenerate: false,
      useDeepResearch: planMetadata?.use_deep_research ?? true
    }),
    onSuccess: (data) => {
      setTaskId(data.task_id)
      onSuccess?.()
    },
    onError: (error) => {
      console.error('Deep reasoning generation error:', error)
      onError?.(error)
    }
  })

  // Auto-trigger generation on mount if not started
  useEffect(() => {
    if (!generationStarted && planId) {
      setGenerationStarted(true)
      
      if (generationMethod === 'deep_reasoning') {
        deepReasoningMutation.mutate()
      } else {
        standardGenerateMutation.mutate()
      }
    }
  }, [planId, generationStarted, generationMethod])

  const isLoading = standardGenerateMutation.isPending || deepReasoningMutation.isPending
  const isSuccess = standardGenerateMutation.isSuccess || deepReasoningMutation.isSuccess
  const isError = standardGenerateMutation.isError || deepReasoningMutation.isError
  const error = standardGenerateMutation.error || deepReasoningMutation.error

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            {generationMethod === 'deep_reasoning' ? (
              <>
                <Brain className="w-5 h-5 text-purple-500" />
                Generowanie z Deep Reasoning
              </>
            ) : (
              <>
                <AlertCircle className="w-5 h-5 text-blue-500" />
                Generowanie Standardowe
              </>
            )}
          </h3>
          
          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin" />
              Trwa generowanie...
            </div>
          )}
          
          {isSuccess && (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <CheckCircle className="w-4 h-4" />
              Zadanie uruchomione
            </div>
          )}
          
          {isError && (
            <div className="flex items-center gap-2 text-sm text-red-600">
              <AlertCircle className="w-4 h-4" />
              Błąd generowania
            </div>
          )}
        </div>

        {/* Progress Info */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-blue-50 p-4 rounded-lg"
          >
            <div className="space-y-2">
              <p className="text-sm font-medium text-blue-900">
                {generationMethod === 'deep_reasoning' 
                  ? 'Uruchomiono zaawansowaną analizę...'
                  : 'Generowanie tematów...'}
              </p>
              
              {generationMethod === 'deep_reasoning' && (
                <div className="space-y-1 text-xs text-blue-700">
                  <p>• Analiza briefów i priorytetów</p>
                  {planMetadata?.use_deep_research && <p>• Research trendów branżowych</p>}
                  {planMetadata?.analyze_competitors && <p>• Analiza konkurencji</p>}
                  <p>• Formułowanie strategii treści</p>
                  <p>• Generowanie i ocena tematów</p>
                </div>
              )}
              
              <p className="text-xs text-blue-600 mt-2">
                {generationMethod === 'deep_reasoning' 
                  ? 'Proces może potrwać 2-5 minut...'
                  : 'Proces powinien zakończyć się w ciągu minuty...'}
              </p>
            </div>
          </motion.div>
        )}

        {/* Success Info */}
        {isSuccess && taskId && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-green-50 p-4 rounded-lg"
          >
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-green-900">
                  Zadanie generowania zostało uruchomione
                </p>
                <p className="text-xs text-green-700 mt-1">
                  ID zadania: {taskId}
                </p>
                {generationMethod === 'deep_reasoning' && (
                  <div className="mt-3 p-3 bg-purple-50 rounded-md">
                    <p className="text-xs font-medium text-purple-900 mb-1">
                      Opcje Deep Reasoning:
                    </p>
                    <ul className="text-xs text-purple-700 space-y-0.5">
                      {planMetadata?.use_deep_research && <li>✓ Głęboki research</li>}
                      {planMetadata?.analyze_competitors && <li>✓ Analiza konkurencji</li>}
                      {planMetadata?.include_trends && <li>✓ Trendy branżowe</li>}
                      {planMetadata?.optimize_seo && <li>✓ Optymalizacja SEO</li>}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* Error Info */}
        {isError && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 p-4 rounded-lg"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-900">
                  Nie udało się uruchomić generowania
                </p>
                <p className="text-xs text-red-700 mt-1">
                  {(error as any)?.response?.data?.detail || (error as any)?.message || 'Nieznany błąd'}
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    if (generationMethod === 'deep_reasoning') {
                      deepReasoningMutation.mutate()
                    } else {
                      standardGenerateMutation.mutate()
                    }
                  }}
                  className="mt-3"
                >
                  Spróbuj ponownie
                </Button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Info about next steps */}
        {!isLoading && !isError && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-gray-500 mt-0.5" />
              <div className="text-sm text-gray-600">
                <p className="font-medium mb-1">Co dalej?</p>
                <ul className="text-xs space-y-1">
                  <li>• Tematy zostaną wygenerowane w tle</li>
                  <li>• Po zakończeniu będziesz mógł je przejrzeć i zatwierdzić</li>
                  <li>• Odśwież stronę za chwilę, aby zobaczyć postęp</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}