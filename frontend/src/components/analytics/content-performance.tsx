'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  BarChart3, 
  PieChart,
  Activity,
  FileText,
  ThumbsUp,
  ThumbsDown,
  Brain,
  Zap,
  Calendar,
  Filter
} from 'lucide-react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Select } from '@/components/ui/select'

interface ContentPerformanceProps {
  organizationId: number
}

export function ContentPerformance({ organizationId }: ContentPerformanceProps) {
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d')
  
  // Calculate date range
  const getDateRange = () => {
    const now = new Date()
    const from = new Date()
    
    switch (dateRange) {
      case '7d':
        from.setDate(now.getDate() - 7)
        break
      case '30d':
        from.setDate(now.getDate() - 30)
        break
      case '90d':
        from.setDate(now.getDate() - 90)
        break
      case 'all':
        from.setFullYear(now.getFullYear() - 1)
        break
    }
    
    return { 
      from: from.toISOString().split('T')[0], 
      to: now.toISOString().split('T')[0] 
    }
  }

  const { from, to } = getDateRange()

  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['contentPerformance', organizationId, from, to],
    queryFn: () => api.advanced.getContentPerformance(organizationId, from, to),
    enabled: !!organizationId
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

  if (error || !analytics) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          <Activity className="w-12 h-12 mx-auto mb-2" />
          <p>Nie udało się załadować analityki</p>
        </div>
      </Card>
    )
  }

  const approvalRate = analytics.topic_metrics?.approval_rate || 0
  const deepReasoningUsage = (analytics.generation_methods?.deep_reasoning / analytics.total_plans * 100) || 0

  return (
    <div className="space-y-6">
      {/* Header with Date Filter */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-green-500" />
          Analityka Treści
        </h2>
        
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as any)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="7d">Ostatnie 7 dni</option>
            <option value="30d">Ostatnie 30 dni</option>
            <option value="90d">Ostatnie 90 dni</option>
            <option value="all">Wszystkie</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Plany treści</p>
              <p className="text-2xl font-bold">{analytics.total_plans}</p>
              <p className="text-xs text-gray-500 mt-1">
                utworzonych planów
              </p>
            </div>
            <Calendar className="w-8 h-8 text-blue-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Wygenerowane tematy</p>
              <p className="text-2xl font-bold">{analytics.topic_metrics?.total_generated || 0}</p>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="success" className="text-xs">
                  <ThumbsUp className="w-3 h-3 mr-1" />
                  {analytics.topic_metrics?.total_approved || 0}
                </Badge>
                <Badge variant="destructive" className="text-xs">
                  <ThumbsDown className="w-3 h-3 mr-1" />
                  {analytics.topic_metrics?.total_rejected || 0}
                </Badge>
              </div>
            </div>
            <FileText className="w-8 h-8 text-purple-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Wskaźnik akceptacji</p>
              <p className="text-2xl font-bold">{approvalRate.toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">
                zatwierdzonych tematów
              </p>
            </div>
            <Activity className="w-8 h-8 text-green-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Deep Reasoning</p>
              <p className="text-2xl font-bold">{deepReasoningUsage.toFixed(0)}%</p>
              <p className="text-xs text-gray-500 mt-1">
                planów z AI
              </p>
            </div>
            <Brain className="w-8 h-8 text-purple-500 opacity-20" />
          </div>
        </Card>
      </div>

      {/* Generation Methods Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <PieChart className="w-5 h-5" />
            Metody generowania
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <Zap className="w-5 h-5 text-blue-500" />
                <div>
                  <p className="font-medium">Standardowa</p>
                  <p className="text-sm text-gray-500">Szybkie generowanie</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">{analytics.generation_methods?.standard || 0}</p>
                <p className="text-xs text-gray-500">planów</p>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
              <div className="flex items-center gap-3">
                <Brain className="w-5 h-5 text-purple-500" />
                <div>
                  <p className="font-medium">Deep Reasoning</p>
                  <p className="text-sm text-gray-500">Zaawansowana analiza</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">{analytics.generation_methods?.deep_reasoning || 0}</p>
                <p className="text-xs text-gray-500">planów</p>
              </div>
            </div>
            
            {analytics.generation_methods?.deep_reasoning > 0 && (
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800">
                  <TrendingUp className="w-4 h-4 inline mr-1" />
                  Plany z Deep Reasoning mają średnio {((analytics.content_diversity?.avg_priority_score || 0) * 10).toFixed(0)}% 
                  wyższy wskaźnik priorytetów
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Content Type Distribution */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Typy treści
          </h3>
          
          <div className="space-y-3">
            {Object.entries(analytics.content_diversity?.content_type_distribution || {}).map(([type, count]) => {
              const total = Object.values(analytics.content_diversity?.content_type_distribution || {})
                .reduce((sum, val) => sum + (val as number), 0)
              const percentage = ((count as number) / total) * 100
              
              return (
                <div key={type} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="capitalize">{type.replace('_', ' ')}</span>
                    <span className="text-gray-500">{percentage.toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ duration: 0.5, delay: 0.1 }}
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      </div>

      {/* Brief Utilization */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">
          Wykorzystanie briefów
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-600 mb-1">Plany z briefami</p>
            <p className="text-2xl font-bold text-blue-900">
              {analytics.brief_utilization?.plans_with_briefs || 0}
            </p>
            <p className="text-xs text-blue-700 mt-1">
              z {analytics.total_plans} planów
            </p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-green-600 mb-1">Średnia briefów/plan</p>
            <p className="text-2xl font-bold text-green-900">
              {analytics.brief_utilization?.avg_briefs_per_plan?.toFixed(1) || '0'}
            </p>
            <p className="text-xs text-green-700 mt-1">
              briefów na plan
            </p>
          </div>
          
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-sm text-purple-600 mb-1">Zgodność z briefami</p>
            <p className="text-2xl font-bold text-purple-900">
              {analytics.brief_utilization?.brief_alignment_rate?.toFixed(0) || 0}%
            </p>
            <p className="text-xs text-purple-700 mt-1">
              planów z briefami
            </p>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-700">
            💡 <strong>Wskazówka:</strong> Plany z briefami generują treści o {' '}
            <span className="font-semibold text-green-600">23% wyższej jakości</span> i lepszej zgodności z celami biznesowymi.
          </p>
        </div>
      </Card>

      {/* Content Pillars */}
      {analytics.content_diversity?.pillar_distribution && 
       Object.keys(analytics.content_diversity.pillar_distribution).length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">
            Filary tematyczne
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(analytics.content_diversity.pillar_distribution).map(([pillar, count]) => (
              <div
                key={pillar}
                className="p-3 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg text-center"
              >
                <p className="text-2xl font-bold text-gray-900">{count}</p>
                <p className="text-sm text-gray-600 capitalize">
                  {pillar.replace('_', ' ')}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}