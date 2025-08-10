'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  Brain, 
  TrendingUp, 
  Target, 
  BarChart3, 
  FileText, 
  Sparkles,
  CheckCircle,
  XCircle,
  Info,
  BookOpen,
  Tag
} from 'lucide-react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

interface GenerationInsightsProps {
  planId: number
}

export function GenerationInsights({ planId }: GenerationInsightsProps) {
  const { data: insights, isLoading, error } = useQuery({
    queryKey: ['generationInsights', planId],
    queryFn: () => api.contentPlans.getGenerationInsights(planId),
    enabled: !!planId
  })

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      </Card>
    )
  }

  if (error || !insights) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          <Info className="w-12 h-12 mx-auto mb-2" />
          <p>Nie udało się załadować insights</p>
        </div>
      </Card>
    )
  }

  const avgPriorityScore = insights.avg_priority_score || 0
  const avgBriefAlignment = insights.avg_brief_alignment || 0
  const hasReasoningData = insights.reasoning_available

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Brain className="w-6 h-6 text-purple-500" />
          Analiza Generowania
        </h2>
        {hasReasoningData && (
          <Badge variant="secondary" className="gap-1">
            <Sparkles className="w-3 h-3" />
            Deep Reasoning
          </Badge>
        )}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Wygenerowane tematy</p>
              <p className="text-2xl font-bold">{insights.total_topics}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Średni priorytet</p>
              <p className="text-2xl font-bold">{avgPriorityScore.toFixed(1)}/10</p>
            </div>
            <Target className="w-8 h-8 text-green-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Zgodność z briefem</p>
              <p className="text-2xl font-bold">{Math.round(avgBriefAlignment)}%</p>
            </div>
            <CheckCircle className="w-8 h-8 text-purple-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Analizowane briefy</p>
              <p className="text-2xl font-bold">
                {insights.brief_analysis?.analyzed_briefs || 0}/
                {insights.brief_analysis?.total_briefs || 0}
              </p>
            </div>
            <BookOpen className="w-8 h-8 text-orange-500 opacity-20" />
          </div>
        </Card>
      </div>

      {/* Content Type Distribution */}
      {insights.content_types && Object.keys(insights.content_types).length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Rozkład typów treści
          </h3>
          <div className="space-y-3">
            {Object.entries(insights.content_types).map(([type, count]) => {
              const percentage = ((count as number) / insights.total_topics) * 100
              return (
                <div key={type} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="capitalize">{type.replace('_', ' ')}</span>
                    <span className="text-gray-500">{count} ({percentage.toFixed(0)}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ duration: 0.5, delay: 0.1 }}
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      )}

      {/* Topic Distribution by Pillar */}
      {insights.topic_distribution && Object.keys(insights.topic_distribution).length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Filary tematyczne
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(insights.topic_distribution).map(([pillar, count]) => (
              <div 
                key={pillar}
                className="p-3 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200"
              >
                <p className="text-sm font-medium text-gray-700 capitalize">
                  {pillar.replace('_', ' ')}
                </p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{count}</p>
                <p className="text-xs text-gray-500">tematów</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Brief Analysis */}
      {insights.brief_analysis && insights.brief_analysis.total_briefs > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Tag className="w-5 h-5" />
            Analiza briefów
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-blue-900">
                  Przeanalizowane briefy
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  System wyekstrahował kluczowe tematy i priorytety
                </p>
              </div>
              <div className="text-2xl font-bold text-blue-900">
                {insights.brief_analysis.analyzed_briefs}/{insights.brief_analysis.total_briefs}
              </div>
            </div>

            {insights.brief_analysis.key_topics_extracted.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Kluczowe tematy z briefów:
                </p>
                <div className="flex flex-wrap gap-2">
                  {insights.brief_analysis.key_topics_extracted.map((topic: string, index: number) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className="text-xs"
                    >
                      {topic}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Priority Score Distribution */}
      {insights.priority_scores && insights.priority_scores.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">
            Rozkład priorytetów
          </h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Najwyższy priorytet</span>
              <span className="font-bold">{Math.max(...insights.priority_scores)}/10</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Średni priorytet</span>
              <span className="font-bold">{avgPriorityScore.toFixed(1)}/10</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Najniższy priorytet</span>
              <span className="font-bold">{Math.min(...insights.priority_scores)}/10</span>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600">
              <Info className="w-3 h-3 inline mr-1" />
              Wyższy priorytet oznacza lepszą zgodność z briefami i celami biznesowymi
            </p>
          </div>
        </Card>
      )}

      {/* Reasoning Available Info */}
      {hasReasoningData && (
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-pink-50">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-purple-900 mb-2">
                Deep Reasoning użyte
              </h3>
              <p className="text-sm text-purple-700 mb-3">
                Tematy zostały wygenerowane z wykorzystaniem zaawansowanej analizy wieloetapowej, 
                która uwzględniła:
              </p>
              <ul className="space-y-1 text-sm text-purple-600">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Głęboką analizę briefów i kontekstu
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Research trendów branżowych
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Formułowanie strategii treści
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Iteracyjną ocenę i optymalizację
                </li>
              </ul>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}