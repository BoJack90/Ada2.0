'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText,
  Brain,
  Target,
  TrendingUp,
  Tag,
  ChevronDown,
  ChevronUp,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  Users,
  Globe,
  Lightbulb
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'

interface BriefAnalysis {
  status: 'analyzing' | 'completed' | 'error'
  extractedTopics: Array<{
    topic: string
    priority: number
    confidence: number
    source: string
  }>
  keyPriorities: Array<{
    priority: string
    importance: 'high' | 'medium' | 'low'
    context: string
  }>
  contentPillars: Array<{
    name: string
    description: string
    suggestedTopics: number
  }>
  targetAudience: {
    primary: string
    secondary?: string
    demographics: string[]
    interests: string[]
  }
  communicationTone: {
    style: string
    keywords: string[]
    avoidWords: string[]
  }
  insights: {
    totalExtractedPoints: number
    confidenceScore: number
    completenessScore: number
    suggestions: string[]
  }
}

interface BriefAnalysisPreviewProps {
  briefId?: number
  briefContent?: string
  analysis?: BriefAnalysis
  onAnalyze?: () => void
}

export function BriefAnalysisPreview({ 
  briefId, 
  briefContent, 
  analysis,
  onAnalyze 
}: BriefAnalysisPreviewProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    topics: true,
    priorities: false,
    pillars: false,
    audience: false,
    tone: false
  })

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  // Mock data for demonstration
  const mockAnalysis: BriefAnalysis = analysis || {
    status: 'completed',
    extractedTopics: [
      { topic: "Innowacje w automatyce budynkowej", priority: 9, confidence: 95, source: "brief główny" },
      { topic: "Bezpieczeństwo systemów elektrycznych", priority: 8, confidence: 88, source: "strategia komunikacji" },
      { topic: "Trendy w smart home", priority: 7, confidence: 82, source: "brief główny" },
      { topic: "Efektywność energetyczna", priority: 9, confidence: 91, source: "oba dokumenty" },
      { topic: "Certyfikacje i normy branżowe", priority: 6, confidence: 75, source: "strategia komunikacji" }
    ],
    keyPriorities: [
      { priority: "Pozycjonowanie jako lider innowacji", importance: 'high', context: "Kluczowy cel biznesowy na 2024" },
      { priority: "Edukacja rynku o nowych technologiach", importance: 'high', context: "Budowanie świadomości marki" },
      { priority: "Pokazanie case studies", importance: 'medium', context: "Budowanie zaufania" },
      { priority: "Komunikacja wartości dla instalatorów", importance: 'high', context: "Grupa docelowa B2B" }
    ],
    contentPillars: [
      { name: "Innowacje & Technologia", description: "Nowości produktowe, trendy technologiczne", suggestedTopics: 12 },
      { name: "Edukacja & Poradniki", description: "Praktyczne wskazówki dla instalatorów", suggestedTopics: 8 },
      { name: "Case Studies", description: "Realizacje i sukcesy klientów", suggestedTopics: 6 },
      { name: "Zrównoważony rozwój", description: "Ekologia i efektywność energetyczna", suggestedTopics: 4 }
    ],
    targetAudience: {
      primary: "Instalatorzy i elektrycy",
      secondary: "Architekci i projektanci",
      demographics: ["25-55 lat", "Wykształcenie techniczne", "Własna działalność"],
      interests: ["Nowe technologie", "Szkolenia branżowe", "Narzędzia pracy", "Trendy w budownictwie"]
    },
    communicationTone: {
      style: "Profesjonalny, ale przystępny",
      keywords: ["innowacja", "bezpieczeństwo", "jakość", "partnerstwo", "rozwój"],
      avoidWords: ["tani", "prosty", "podstawowy", "amatorski"]
    },
    insights: {
      totalExtractedPoints: 47,
      confidenceScore: 89,
      completenessScore: 92,
      suggestions: [
        "Rozważ dodanie więcej treści o certyfikatach produktowych",
        "Zwiększ częstotliwość postów edukacyjnych",
        "Dodaj sekcję Q&A dla typowych pytań instalatorów",
        "Wykorzystaj więcej wizualizacji technicznych"
      ]
    }
  }

  const currentAnalysis = mockAnalysis

  if (currentAnalysis.status === 'analyzing') {
    return (
      <Card className="p-6">
        <div className="flex flex-col items-center justify-center py-8">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="mb-4"
          >
            <Brain className="w-12 h-12 text-purple-600" />
          </motion.div>
          <h3 className="text-lg font-semibold mb-2">Analizuję brief...</h3>
          <p className="text-gray-500 text-center">
            System Deep Reasoning analizuje zawartość briefu i wydobywa kluczowe informacje
          </p>
          <Progress value={33} className="w-64 mt-4" />
        </div>
      </Card>
    )
  }

  if (currentAnalysis.status === 'error') {
    return (
      <Card className="p-6 border-red-200 bg-red-50">
        <div className="flex items-center gap-3 text-red-700">
          <AlertCircle className="w-6 h-6" />
          <div>
            <h3 className="font-semibold">Błąd analizy</h3>
            <p className="text-sm">Nie udało się przeanalizować briefu. Spróbuj ponownie.</p>
          </div>
        </div>
        {onAnalyze && (
          <Button onClick={onAnalyze} className="mt-4" variant="outline">
            Spróbuj ponownie
          </Button>
        )}
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-1">
                Analiza Briefu - Deep Reasoning
              </h2>
              <p className="text-gray-600">
                System przeanalizował brief i wyodrębnił kluczowe informacje
              </p>
              <div className="flex items-center gap-4 mt-3">
                <Badge variant="outline" className="flex items-center gap-1">
                  <FileText className="w-3 h-3" />
                  {currentAnalysis.insights.totalExtractedPoints} punktów
                </Badge>
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Target className="w-3 h-3" />
                  {currentAnalysis.insights.confidenceScore}% pewności
                </Badge>
                <Badge variant="secondary" className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  {currentAnalysis.insights.completenessScore}% kompletności
                </Badge>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Ostatnia analiza</p>
            <p className="text-sm font-medium">5 minut temu</p>
          </div>
        </div>
      </Card>

      {/* Extracted Topics */}
      <Card className="p-6">
        <button
          onClick={() => toggleSection('topics')}
          className="w-full flex items-center justify-between mb-4 hover:opacity-80 transition-opacity"
        >
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-500" />
            Wyodrębnione Tematy ({currentAnalysis.extractedTopics.length})
          </h3>
          {expandedSections.topics ? <ChevronUp /> : <ChevronDown />}
        </button>
        
        <AnimatePresence>
          {expandedSections.topics && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="space-y-3 overflow-hidden"
            >
              {currentAnalysis.extractedTopics.map((topic, index) => (
                <motion.div
                  key={index}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{topic.topic}</h4>
                      <div className="flex items-center gap-3 mt-2">
                        <span className="text-sm text-gray-500">Źródło: {topic.source}</span>
                        <Badge variant="outline" className="text-xs">
                          Pewność: {topic.confidence}%
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Priorytet</span>
                      <div className="flex items-center">
                        {[...Array(10)].map((_, i) => (
                          <div
                            key={i}
                            className={`w-2 h-8 mx-0.5 rounded-sm ${
                              i < topic.priority 
                                ? 'bg-gradient-to-t from-orange-500 to-yellow-500' 
                                : 'bg-gray-200'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Key Priorities */}
      <Card className="p-6">
        <button
          onClick={() => toggleSection('priorities')}
          className="w-full flex items-center justify-between mb-4 hover:opacity-80 transition-opacity"
        >
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Target className="w-5 h-5 text-red-500" />
            Kluczowe Priorytety ({currentAnalysis.keyPriorities.length})
          </h3>
          {expandedSections.priorities ? <ChevronUp /> : <ChevronDown />}
        </button>
        
        <AnimatePresence>
          {expandedSections.priorities && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="space-y-3 overflow-hidden"
            >
              {currentAnalysis.keyPriorities.map((priority, index) => (
                <div key={index} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50">
                  <div className={`p-2 rounded-lg ${
                    priority.importance === 'high' ? 'bg-red-100' :
                    priority.importance === 'medium' ? 'bg-yellow-100' : 'bg-gray-100'
                  }`}>
                    <Target className={`w-4 h-4 ${
                      priority.importance === 'high' ? 'text-red-600' :
                      priority.importance === 'medium' ? 'text-yellow-600' : 'text-gray-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{priority.priority}</p>
                    <p className="text-sm text-gray-500">{priority.context}</p>
                  </div>
                  <Badge variant={
                    priority.importance === 'high' ? 'destructive' :
                    priority.importance === 'medium' ? 'warning' : 'secondary'
                  }>
                    {priority.importance === 'high' ? 'Wysoki' :
                     priority.importance === 'medium' ? 'Średni' : 'Niski'}
                  </Badge>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Content Pillars */}
      <Card className="p-6">
        <button
          onClick={() => toggleSection('pillars')}
          className="w-full flex items-center justify-between mb-4 hover:opacity-80 transition-opacity"
        >
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Tag className="w-5 h-5 text-green-500" />
            Filary Treści ({currentAnalysis.contentPillars.length})
          </h3>
          {expandedSections.pillars ? <ChevronUp /> : <ChevronDown />}
        </button>
        
        <AnimatePresence>
          {expandedSections.pillars && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4 overflow-hidden"
            >
              {currentAnalysis.contentPillars.map((pillar, index) => (
                <motion.div
                  key={index}
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200"
                >
                  <h4 className="font-semibold text-green-900 mb-1">{pillar.name}</h4>
                  <p className="text-sm text-gray-600 mb-3">{pillar.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Sugerowane tematy:</span>
                    <Badge variant="secondary">{pillar.suggestedTopics}</Badge>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Target Audience */}
      <Card className="p-6">
        <button
          onClick={() => toggleSection('audience')}
          className="w-full flex items-center justify-between mb-4 hover:opacity-80 transition-opacity"
        >
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-500" />
            Grupa Docelowa
          </h3>
          {expandedSections.audience ? <ChevronUp /> : <ChevronDown />}
        </button>
        
        <AnimatePresence>
          {expandedSections.audience && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="space-y-4 overflow-hidden"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Główna grupa</p>
                  <p className="font-medium">{currentAnalysis.targetAudience.primary}</p>
                </div>
                {currentAnalysis.targetAudience.secondary && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Grupa dodatkowa</p>
                    <p className="font-medium">{currentAnalysis.targetAudience.secondary}</p>
                  </div>
                )}
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-2">Demografia</p>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.targetAudience.demographics.map((demo, i) => (
                    <Badge key={i} variant="outline">{demo}</Badge>
                  ))}
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-2">Zainteresowania</p>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.targetAudience.interests.map((interest, i) => (
                    <Badge key={i} variant="secondary">{interest}</Badge>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Communication Tone */}
      <Card className="p-6">
        <button
          onClick={() => toggleSection('tone')}
          className="w-full flex items-center justify-between mb-4 hover:opacity-80 transition-opacity"
        >
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Globe className="w-5 h-5 text-purple-500" />
            Ton Komunikacji
          </h3>
          {expandedSections.tone ? <ChevronUp /> : <ChevronDown />}
        </button>
        
        <AnimatePresence>
          {expandedSections.tone && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="space-y-4 overflow-hidden"
            >
              <div>
                <p className="text-sm text-gray-500 mb-1">Styl komunikacji</p>
                <p className="font-medium">{currentAnalysis.communicationTone.style}</p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-2">Kluczowe słowa</p>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.communicationTone.keywords.map((keyword, i) => (
                    <Badge key={i} variant="secondary" className="bg-green-100 text-green-700">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-2">Słowa do unikania</p>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.communicationTone.avoidWords.map((word, i) => (
                    <Badge key={i} variant="destructive" className="bg-red-100 text-red-700">
                      {word}
                    </Badge>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Insights & Suggestions */}
      <Card className="p-6 bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-yellow-100 rounded-lg">
            <Lightbulb className="w-5 h-5 text-yellow-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-3">Rekomendacje AI</h3>
            <div className="space-y-2">
              {currentAnalysis.insights.suggestions.map((suggestion, i) => (
                <div key={i} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-yellow-600 rounded-full mt-1.5" />
                  <p className="text-sm text-gray-700">{suggestion}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}