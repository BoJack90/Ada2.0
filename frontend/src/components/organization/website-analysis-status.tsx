'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { WebsiteAnalysis } from '@/types'
import { 
  Globe, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle,
  Building,
  Target,
  MessageSquare,
  TrendingUp,
  Users,
  Lightbulb,
  Sparkles,
  Brain,
  Zap,
  Shield,
  Cpu
} from 'lucide-react'

interface WebsiteAnalysisStatusProps {
  organizationId: number
  onAnalysisComplete?: () => void
}

export function WebsiteAnalysisStatus({ 
  organizationId, 
  onAnalysisComplete 
}: WebsiteAnalysisStatusProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)
  
  const { data: analysis, isLoading, refetch } = useQuery<WebsiteAnalysis>({
    queryKey: ['website-analysis', organizationId],
    queryFn: async () => {
      const response = await api.organizations.getWebsiteAnalysis(organizationId)
      return response
    },
    refetchInterval: (data) => {
      // Poll every 5 seconds if processing
      if (data?.status === 'processing') return 5000
      return false
    },
    enabled: !!organizationId
  })
  
  useEffect(() => {
    if (analysis?.status === 'completed' && onAnalysisComplete) {
      onAnalysisComplete()
    }
  }, [analysis?.status, onAnalysisComplete])
  
  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      await api.organizations.refreshWebsiteAnalysis(organizationId)
      setTimeout(() => refetch(), 1000)
    } catch (error) {
      console.error('Failed to refresh website analysis:', error)
    } finally {
      setIsRefreshing(false)
    }
  }
  
  const handleCancel = async () => {
    try {
      await api.organizations.cancelWebsiteAnalysis(organizationId)
      setTimeout(() => refetch(), 500)
    } catch (error) {
      console.error('Failed to cancel website analysis:', error)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <RefreshCw className="h-5 w-5 animate-spin text-blue-500" />
      </div>
    )
  }
  
  if (!analysis || analysis.status === 'not_found') {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Globe className="h-5 w-5 text-gray-400" />
            <div className="flex-1">
              <p className="text-sm text-gray-600">Analiza strony internetowej</p>
              <p className="text-xs text-gray-500">Brak analizy - kliknij aby rozpocząć</p>
            </div>
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
            title="Rozpocznij analizę"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            Rozpocznij analizę
          </button>
        </div>
      </div>
    )
  }
  
  const getStatusIcon = () => {
    switch (analysis?.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'processing':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />
    }
  }
  
  const getStatusText = () => {
    switch (analysis.status) {
      case 'completed':
        return 'Analiza zakończona'
      case 'processing':
        return 'Analizowanie...'
      case 'failed':
        return 'Błąd analizy'
      case 'pending':
        return 'Oczekuje na analizę'
      default:
        return 'Status nieznany'
    }
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <div>
              <h3 className="text-sm font-medium text-gray-900">
                Analiza strony internetowej
              </h3>
              <p className="text-xs text-gray-500">{getStatusText()}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {analysis.status === 'completed' && (
              <span className="text-xs text-gray-500">
                {analysis.last_analysis_date && 
                  `Ostatnia: ${new Date(analysis.last_analysis_date).toLocaleDateString('pl-PL')}`
                }
              </span>
            )}
            
            <button
              onClick={handleRefresh}
              disabled={isRefreshing || analysis.status === 'processing'}
              className={`
                px-3 py-1.5 text-xs font-medium rounded-md transition-all 
                ${analysis.status === 'completed' 
                  ? 'text-gray-700 bg-gray-100 hover:bg-gray-200' 
                  : 'text-white bg-blue-600 hover:bg-blue-700'
                }
                disabled:opacity-50 disabled:cursor-not-allowed 
                flex items-center gap-1.5
              `}
              title={analysis.status === 'completed' ? 'Odśwież analizę' : 'Rozpocznij analizę'}
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              {analysis.status === 'completed' ? 'Odśwież' : 'Analizuj'}
            </button>
          </div>
        </div>
      </div>
      
      {/* Content */}
      {analysis.status === 'completed' && (
        <div className="p-4 space-y-4">
          {/* Website URL */}
          <div className="flex items-start gap-3">
            <Globe className="h-4 w-4 text-gray-400 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs text-gray-500">Analizowana strona</p>
              <a 
                href={analysis.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline"
              >
                {analysis.website_url}
              </a>
            </div>
          </div>
          
          {/* Industry */}
          {analysis.industry_detected && (
            <div className="flex items-start gap-3">
              <Building className="h-4 w-4 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-gray-500">Wykryta branża</p>
                <p className="text-sm text-gray-900 capitalize">
                  {analysis.industry_detected}
                </p>
              </div>
            </div>
          )}
          
          {/* Services */}
          {analysis.services_detected && analysis.services_detected.length > 0 && (
            <div className="flex items-start gap-3">
              <TrendingUp className="h-4 w-4 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-gray-500 mb-1">Wykryte usługi</p>
                <div className="flex flex-wrap gap-1">
                  {analysis.services_detected.slice(0, 3).map((service, index) => (
                    <span 
                      key={index}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {service.length > 50 ? service.substring(0, 50) + '...' : service}
                    </span>
                  ))}
                  {analysis.services_detected.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{analysis.services_detected.length - 3} więcej
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Target Audience */}
          {analysis.target_audience && analysis.target_audience.length > 0 && (
            <div className="flex items-start gap-3">
              <Users className="h-4 w-4 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-gray-500 mb-1">Grupa docelowa</p>
                <div className="flex flex-wrap gap-1">
                  {analysis.target_audience.map((audience, index) => (
                    <span 
                      key={index}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
                    >
                      {audience}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          
          {/* Key Topics */}
          {analysis.key_topics && analysis.key_topics.length > 0 && (
            <div className="flex items-start gap-3">
              <Target className="h-4 w-4 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-gray-500 mb-1">Kluczowe tematy</p>
                <ul className="text-sm text-gray-700 space-y-1">
                  {analysis.key_topics.slice(0, 3).map((topic, index) => (
                    <li key={index} className="text-xs line-clamp-2">
                      • {topic}
                    </li>
                  ))}
                  {analysis.key_topics.length > 3 && (
                    <li className="text-xs text-gray-500">
                      • +{analysis.key_topics.length - 3} więcej tematów
                    </li>
                  )}
                </ul>
              </div>
            </div>
          )}
          
          {/* Competitors */}
          {analysis.competitors_mentioned && analysis.competitors_mentioned.length > 0 && (
            <div className="flex items-start gap-3">
              <Users className="h-4 w-4 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-gray-500 mb-1">Konkurenci wymienieni na stronie</p>
                <div className="flex flex-wrap gap-1">
                  {analysis.competitors_mentioned.map((competitor, index) => (
                    <span 
                      key={index}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800"
                    >
                      {competitor}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {/* Enhanced AI Analysis Section - Only show if available */}
          {(analysis.company_overview || analysis.unique_selling_points?.length > 0 || 
            analysis.brand_personality || analysis.market_positioning) && (
            <>
              <div className="border-t border-gray-100 pt-4 mt-4">
                <h4 className="text-xs font-semibold text-gray-700 mb-3 flex items-center gap-1">
                  <Brain className="h-3.5 w-3.5" />
                  Analiza AI
                </h4>
                
                {/* Company Overview */}
                {analysis.company_overview && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-1">Opis firmy</p>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {analysis.company_overview}
                    </p>
                  </div>
                )}
                
                {/* Market Positioning */}
                {analysis.market_positioning && (
                  <div className="flex items-start gap-3 mb-3">
                    <Target className="h-4 w-4 text-gray-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500">Pozycja rynkowa</p>
                      <p className="text-sm text-gray-900">
                        {analysis.market_positioning}
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Unique Selling Points */}
                {analysis.unique_selling_points && analysis.unique_selling_points.length > 0 && (
                  <div className="flex items-start gap-3 mb-3">
                    <Sparkles className="h-4 w-4 text-gray-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 mb-1">Unikalne przewagi</p>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {analysis.unique_selling_points.slice(0, 3).map((usp, index) => (
                          <li key={index} className="text-xs">
                            • {usp}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
                
                {/* Brand Personality */}
                {analysis.brand_personality && (
                  <div className="flex items-start gap-3 mb-3">
                    <MessageSquare className="h-4 w-4 text-gray-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500">Osobowość marki</p>
                      <p className="text-sm text-gray-700">
                        {analysis.brand_personality}
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Customer Pain Points */}
                {analysis.customer_pain_points && analysis.customer_pain_points.length > 0 && (
                  <div className="flex items-start gap-3 mb-3">
                    <Zap className="h-4 w-4 text-gray-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 mb-1">Problemy klientów rozwiązywane</p>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {analysis.customer_pain_points.slice(0, 3).map((pain, index) => (
                          <li key={index} className="text-xs">
                            • {pain}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
                
                {/* Recommended Content Topics */}
                {analysis.recommended_content_topics && analysis.recommended_content_topics.length > 0 && (
                  <div className="flex items-start gap-3 mb-3">
                    <Lightbulb className="h-4 w-4 text-gray-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 mb-1">Rekomendowane tematy treści</p>
                      <div className="flex flex-wrap gap-1">
                        {analysis.recommended_content_topics.slice(0, 5).map((topic, index) => (
                          <span 
                            key={index}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Content Strategy Insights */}
                {analysis.content_strategy_insights && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-1">Wnioski o strategii treści</p>
                    <p className="text-xs text-gray-700 leading-relaxed">
                      {analysis.content_strategy_insights}
                    </p>
                  </div>
                )}
                
                {/* Technology Stack */}
                {analysis.technology_stack && analysis.technology_stack.length > 0 && (
                  <div className="flex items-start gap-3 mb-3">
                    <Cpu className="h-4 w-4 text-gray-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 mb-1">Technologie</p>
                      <div className="flex flex-wrap gap-1">
                        {analysis.technology_stack.slice(0, 5).map((tech, index) => (
                          <span 
                            key={index}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
          
          {/* Last Analysis Date */}
          {analysis.last_analysis_date && (
            <div className="pt-2 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Ostatnia analiza: {new Date(analysis.last_analysis_date).toLocaleString('pl-PL')}
              </p>
            </div>
          )}
        </div>
      )}
      
      {/* Error State */}
      {analysis.status === 'failed' && (
        <div className="p-4">
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <div className="flex items-start gap-3">
              <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-red-800 font-medium">Błąd analizy</p>
                <p className="text-xs text-red-600 mt-1">
                  {analysis.error_message || 'Wystąpił błąd podczas analizy strony'}
                </p>
                {analysis.error_message?.includes('Tavily API limit') && (
                  <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
                    <p className="text-xs text-yellow-800 font-medium">
                      Limit API Tavily został przekroczony
                    </p>
                    <p className="text-xs text-yellow-700 mt-1">
                      Sprawdź swój klucz API Tavily lub zaktualizuj plan na{' '}
                      <a 
                        href="https://tavily.com" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        tavily.com
                      </a>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Processing State */}
      {analysis.status === 'processing' && (
        <div className="p-4">
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <div className="flex items-start gap-3">
              <RefreshCw className="h-5 w-5 text-blue-500 animate-spin mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-blue-800 font-medium">Analizowanie strony</p>
                <p className="text-xs text-blue-600 mt-1">
                  Trwa pobieranie i analiza zawartości strony internetowej...
                </p>
                <div className="mt-2 space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-1.5 bg-blue-500 rounded-full animate-pulse" />
                    <span className="text-xs text-blue-700">Pobieranie zawartości strony</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-1.5 bg-blue-500 rounded-full animate-pulse" />
                    <span className="text-xs text-blue-700">Analiza branży i usług</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-1.5 bg-blue-500 rounded-full animate-pulse" />
                    <span className="text-xs text-blue-700">Wykrywanie kluczowych tematów</span>
                  </div>
                </div>
                <button
                  onClick={handleCancel}
                  className="mt-3 px-3 py-1.5 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-md transition-colors flex items-center gap-1.5"
                >
                  <XCircle className="h-3.5 w-3.5" />
                  Anuluj analizę
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Pending State */}
      {analysis.status === 'pending' && (
        <div className="p-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
            <div className="flex items-start gap-3">
              <Clock className="h-5 w-5 text-yellow-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-yellow-800 font-medium">Oczekuje na analizę</p>
                <p className="text-xs text-yellow-600 mt-1">
                  Analiza rozpocznie się wkrótce...
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}