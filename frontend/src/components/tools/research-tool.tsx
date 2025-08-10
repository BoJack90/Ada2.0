'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Globe, 
  TrendingUp, 
  Building2, 
  FileSearch,
  Loader2,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Tag,
  Calendar,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

interface ResearchToolProps {
  organizationId?: number
  industry?: string
  onResultsReceived?: (results: any) => void
}

export function ResearchTool({ organizationId, industry, onResultsReceived }: ResearchToolProps) {
  const [topic, setTopic] = useState('')
  const [researchDepth, setResearchDepth] = useState<'basic' | 'deep' | 'comprehensive'>('deep')
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [lastResults, setLastResults] = useState<any>(null)

  const researchMutation = useMutation({
    mutationFn: (data: any) => api.advanced.researchTopic(data),
    onSuccess: (data) => {
      setLastResults(data)
      onResultsReceived?.(data)
    }
  })

  const handleResearch = () => {
    if (!topic.trim()) return

    researchMutation.mutate({
      topic,
      organizationId,
      industry,
      depth: researchDepth,
      includeRawData: false,
      storeResults: !!organizationId
    })
  }

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-6">
      {/* Research Input */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Search className="w-5 h-5" />
          Research Tool
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temat do zbadania
            </label>
            <Textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="np. Sztuczna inteligencja w logistyce, Trendy e-commerce 2024, Marketing automation dla B2B..."
              className="w-full min-h-[80px]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Głębokość researchu
              </label>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  type="button"
                  variant={researchDepth === 'basic' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setResearchDepth('basic')}
                >
                  Podstawowy
                </Button>
                <Button
                  type="button"
                  variant={researchDepth === 'deep' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setResearchDepth('deep')}
                >
                  Głęboki
                </Button>
                <Button
                  type="button"
                  variant={researchDepth === 'comprehensive' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setResearchDepth('comprehensive')}
                >
                  Kompleksowy
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {researchDepth === 'basic' && 'Szybki przegląd (~1 min)'}
                {researchDepth === 'deep' && 'Dokładna analiza (~2-3 min)'}
                {researchDepth === 'comprehensive' && 'Pełny research (~3-5 min)'}
              </p>
            </div>

            <div className="flex items-end">
              <Button
                onClick={handleResearch}
                disabled={!topic.trim() || researchMutation.isPending}
                className="w-full"
              >
                {researchMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Researching...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-2" />
                    Rozpocznij Research
                  </>
                )}
              </Button>
            </div>
          </div>

          {industry && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Building2 className="w-4 h-4" />
              <span>Branża: {industry}</span>
            </div>
          )}
        </div>
      </Card>

      {/* Loading State */}
      {researchMutation.isPending && (
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-center">
              <LoadingSpinner size="large" />
            </div>
            <div className="text-center space-y-2">
              <p className="text-sm font-medium text-gray-700">
                Przeprowadzam research...
              </p>
              <div className="max-w-md mx-auto space-y-1 text-xs text-gray-500">
                <p>• Analizuję trendy branżowe</p>
                <p>• Sprawdzam najnowsze informacje</p>
                <p>• Badam strategie konkurencji</p>
                <p>• Syntetyzuję wyniki</p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Results */}
      {lastResults && !researchMutation.isPending && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Summary */}
          {lastResults.synthesis && (
            <Card className="p-6">
              <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileSearch className="w-5 h-5" />
                Podsumowanie Researchu
              </h4>

              <div className="space-y-4">
                {/* Key Findings */}
                {lastResults.synthesis.key_findings?.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">
                      Kluczowe odkrycia:
                    </h5>
                    <ul className="space-y-1">
                      {lastResults.synthesis.key_findings.map((finding: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Content Opportunities */}
                {lastResults.synthesis.content_opportunities?.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">
                      Możliwości content marketingowe:
                    </h5>
                    <div className="grid gap-2">
                      {lastResults.synthesis.content_opportunities.map((opp: any, idx: number) => (
                        <div key={idx} className="p-3 bg-blue-50 rounded-lg">
                          <p className="text-sm font-medium text-blue-900">
                            {opp.aspect}
                          </p>
                          <p className="text-xs text-blue-700 mt-1">
                            {opp.inspiration}
                          </p>
                          {opp.url && (
                            <a
                              href={opp.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 mt-2"
                            >
                              <ExternalLink className="w-3 h-3" />
                              Zobacz przykład
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Trending Angles */}
                {lastResults.synthesis.trending_angles?.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      Trendy i tematy na czasie:
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {lastResults.synthesis.trending_angles.map((angle: string, idx: number) => (
                        <Badge key={idx} variant="secondary">
                          {angle}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Detailed Sources */}
          {lastResults.sources_used && (
            <Card className="p-6">
              <h4 className="text-lg font-semibold mb-4">
                Wykorzystane źródła
              </h4>
              
              <div className="space-y-2">
                {lastResults.sources_used.map((source: string, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 text-sm text-gray-600"
                  >
                    <Globe className="w-4 h-4" />
                    <span className="capitalize">{source.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>

              {lastResults.stored_id && (
                <div className="mt-4 p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-800">
                    <CheckCircle className="w-4 h-4 inline mr-1" />
                    Research zapisany w bazie danych (ID: {lastResults.stored_id})
                  </p>
                </div>
              )}
            </Card>
          )}

          {/* Raw Research Data (Expandable) */}
          {lastResults.full_results && (
            <Card className="p-6">
              <button
                onClick={() => toggleSection('raw')}
                className="w-full flex items-center justify-between text-left"
              >
                <h4 className="text-lg font-semibold">
                  Surowe dane researchu
                </h4>
                {expandedSection === 'raw' ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </button>

              <AnimatePresence>
                {expandedSection === 'raw' && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mt-4 overflow-hidden"
                  >
                    <pre className="p-4 bg-gray-50 rounded-lg text-xs overflow-x-auto">
                      {JSON.stringify(lastResults.full_results, null, 2)}
                    </pre>
                  </motion.div>
                )}
              </AnimatePresence>
            </Card>
          )}
        </motion.div>
      )}

      {/* Error State */}
      {researchMutation.isError && (
        <Card className="p-6 border-red-200 bg-red-50">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-900">
                Wystąpił błąd podczas researchu
              </p>
              <p className="text-xs text-red-700 mt-1">
                {(researchMutation.error as any)?.response?.data?.detail || 
                 (researchMutation.error as any)?.message || 
                 'Nieznany błąd'}
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}