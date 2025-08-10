'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Bot, 
  Edit3, 
  Save, 
  X, 
  ChevronDown, 
  ChevronRight, 
  Activity, 
  Settings, 
  CheckCircle,
  AlertCircle,
  Clock,
  Database,
  Zap,
  BarChart3,
  FileText,
  Shield,
  Plus,
  Trash2,
  RefreshCw,
  AlertTriangle,
  Info,
  Copy,
  Eye,
  EyeOff,
  Sparkles,
  Brain,
  Cpu,
  Terminal,
  Code2,
  Layers,
  Check
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

interface AIPrompt {
  id: number
  prompt_name: string
  prompt_template: string
  description?: string
  version: number
  created_at: string
  updated_at: string
}

interface AIModelAssignment {
  id: number
  task_name: string
  model_name: string
  created_at: string
  updated_at: string
}

interface AIFunction {
  function_name: string
  display_name: string
  prompts: AIPrompt[]
  model_assignment: AIModelAssignment | null
  category: string
}

interface AICategory {
  name: string
  description: string
  icon: string
  functions: AIFunction[]
}

interface AIFunctionsGrouped {
  categories: Record<string, AICategory>
  total_functions: number
  total_prompts: number
  total_model_assignments: number
  available_models: string[]
}

interface AIHealthCheck {
  health_score: number
  status: 'healthy' | 'warning' | 'critical'
  total_functions: number
  configured_functions: number
  missing_model_assignments: string[]
  orphaned_models: string[]
  recommendations: (string | null)[]
}

interface AIManagementPanelOrgProps {
  organizationId: number
}

// Mapowanie ikon dla kategorii
const categoryIcons: Record<string, React.ReactNode> = {
  'content_generation': <FileText className="w-5 h-5" />,
  'social_media': <Zap className="w-5 h-5" />,
  'planning': <BarChart3 className="w-5 h-5" />,
  'analysis': <Brain className="w-5 h-5" />,
  'deep_reasoning': <Layers className="w-5 h-5" />,
  'review': <Shield className="w-5 h-5" />,
  'default': <Code2 className="w-5 h-5" />
}

// Opisy kategorii po polsku
const categoryDescriptions: Record<string, string> = {
  'content_generation': 'Tworzenie artykułów blogowych i różnych wariantów treści',
  'social_media': 'Generowanie postów dedykowanych dla platform społecznościowych',
  'planning': 'Harmonogramowanie i optymalizacja publikacji',
  'analysis': 'Analiza briefów, strategii i dokumentów',
  'deep_reasoning': 'Zaawansowany proces wieloetapowego generowania',
  'review': 'Ocena jakości i iteracyjne ulepszanie treści'
}

export function AIManagementPanelOrg({ organizationId }: AIManagementPanelOrgProps) {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [expandedFunctions, setExpandedFunctions] = useState<Set<string>>(new Set())
  const [editingPrompt, setEditingPrompt] = useState<AIPrompt | null>(null)
  const [editingModel, setEditingModel] = useState<string | null>(null)
  const [editPromptContent, setEditPromptContent] = useState('')
  const [editModelName, setEditModelName] = useState('')
  const [showPromptContent, setShowPromptContent] = useState<Set<number>>(new Set())
  
  // Fetch AI functions data for organization
  const { data: aiData, isLoading, error } = useQuery<AIFunctionsGrouped>({
    queryKey: ['ai-functions-grouped', organizationId],
    queryFn: () => api.aiManagement.getOrganizationAIFunctions(organizationId)
  })

  // Mutations for CRUD operations
  const updatePromptMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: any }) => {
      console.log('[AI Management Org] updatePrompt mutation called', { organizationId, id, data })
      return api.aiManagement.updateOrganizationPrompt(organizationId, id, data)
    },
    onSuccess: (result) => {
      console.log('[AI Management Org] updatePrompt success', result)
      queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped', organizationId] })
      setEditingPrompt(null)
      setEditPromptContent('')
    },
    onError: (error) => {
      console.error('[AI Management Org] updatePrompt error', error)
    }
  })

  const createModelAssignmentMutation = useMutation({
    mutationFn: (data: { task_name: string, model_name: string }) => {
      console.log('[AI Management Org] createModelAssignment mutation called', { organizationId, data })
      return api.aiManagement.createOrganizationModelAssignment(organizationId, { 
        task_name: data.task_name, 
        model_name: data.model_name 
      })
    },
    onSuccess: (result) => {
      console.log('[AI Management Org] createModelAssignment success', result)
      queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped', organizationId] })
      setEditingModel(null)
      setEditModelName('')
    },
    onError: (error) => {
      console.error('[AI Management Org] createModelAssignment error', error)
    }
  })

  const updateModelAssignmentMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: any }) => {
      console.log('[AI Management Org] updateModelAssignment mutation called', { organizationId, id, data })
      return api.aiManagement.updateOrganizationModelAssignment(organizationId, id, data)
    },
    onSuccess: (result) => {
      console.log('[AI Management Org] updateModelAssignment success', result)
      queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped', organizationId] })
      setEditingModel(null)
      setEditModelName('')
    },
    onError: (error) => {
      console.error('[AI Management Org] updateModelAssignment error', error)
    }
  })

  const toggleFunctionExpansion = (functionName: string) => {
    const newExpanded = new Set(expandedFunctions)
    if (newExpanded.has(functionName)) {
      newExpanded.delete(functionName)
    } else {
      newExpanded.add(functionName)
    }
    setExpandedFunctions(newExpanded)
  }

  const togglePromptVisibility = (promptId: number) => {
    const newVisible = new Set(showPromptContent)
    if (newVisible.has(promptId)) {
      newVisible.delete(promptId)
    } else {
      newVisible.add(promptId)
    }
    setShowPromptContent(newVisible)
  }

  const handleEditPrompt = (prompt: AIPrompt) => {
    setEditingPrompt(prompt)
    setEditPromptContent(prompt.prompt_template)
  }

  const handleSavePrompt = () => {
    console.log('[AI Management Org] handleSavePrompt called', {
      editingPrompt,
      editPromptContent
    })
    if (editingPrompt) {
      updatePromptMutation.mutate({
        id: editingPrompt.id,
        data: { prompt_template: editPromptContent }
      })
    }
  }

  const handleCancelEdit = () => {
    setEditingPrompt(null)
    setEditPromptContent('')
  }

  const handleEditModel = (functionName: string, currentModel?: string) => {
    setEditingModel(functionName)
    setEditModelName(currentModel || '')
  }

  const handleSaveModel = (functionName: string, existingAssignment?: AIModelAssignment) => {
    console.log('[AI Management Org] handleSaveModel called', {
      functionName,
      existingAssignment,
      editModelName
    })
    if (existingAssignment) {
      updateModelAssignmentMutation.mutate({
        id: existingAssignment.id,
        data: { model_name: editModelName }
      })
    } else {
      createModelAssignmentMutation.mutate({
        task_name: functionName,
        model_name: editModelName
      })
    }
  }

  const getCategoryIcon = (iconName: string) => {
    // Użyj mapy ikon według klucza kategorii
    const categoryKey = iconName.toLowerCase().replace(' ', '_');
    return categoryIcons[categoryKey] || categoryIcons['default'];
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Błąd ładowania danych</h3>
            <p className="text-sm text-red-700 mt-1">
              Nie udało się załadować konfiguracji AI. Spróbuj odświeżyć stronę.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">
            Skonfiguruj modele AI i prompty specyficzne dla tej organizacji
          </p>
        </div>
        <button
          onClick={() => {
            queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped', organizationId] })
          }}
          className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Odśwież
        </button>
      </div>

      {/* Statistics Cards */}
      {aiData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center">
              <Brain className="w-8 h-8 text-blue-500" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">Funkcje AI</p>
                <p className="text-xl font-semibold">{aiData.total_functions}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-green-500" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">Prompty</p>
                <p className="text-xl font-semibold">{aiData.total_prompts}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center">
              <Cpu className="w-8 h-8 text-purple-500" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">Modele</p>
                <p className="text-xl font-semibold">{aiData.total_model_assignments}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center">
              <Sparkles className="w-8 h-8 text-yellow-500" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">Dostępne modele</p>
                <p className="text-xl font-semibold">{aiData.available_models.length}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Functions by Category */}
      <div className="space-y-4">
        {aiData && Object.entries(aiData.categories).map(([categoryKey, category]) => (
          category.functions.length > 0 && (
            <div key={categoryKey} className="bg-white rounded-lg border shadow-sm">
              <div 
                className="p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setSelectedCategory(selectedCategory === categoryKey ? null : categoryKey)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {getCategoryIcon(category.icon)}
                    <div className="ml-3">
                      <h3 className="text-lg font-medium text-gray-900">{category.name}</h3>
                      <p className="text-sm text-gray-600">
                        {categoryDescriptions[categoryKey] || category.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-sm text-gray-500 mr-2">
                      {category.functions.length} funkcji
                    </span>
                    {selectedCategory === categoryKey ? 
                      <ChevronDown className="w-5 h-5 text-gray-400" /> : 
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    }
                  </div>
                </div>
              </div>

              {selectedCategory === categoryKey && (
                <div className="p-4 space-y-4">
                  {category.functions.map((func) => (
                    <div key={func.function_name} className="border rounded-lg">
                      <div 
                        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => toggleFunctionExpansion(func.function_name)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="flex items-center">
                              {expandedFunctions.has(func.function_name) ? 
                                <ChevronDown className="w-4 h-4 text-gray-400 mr-2" /> : 
                                <ChevronRight className="w-4 h-4 text-gray-400 mr-2" />
                              }
                              <h4 className="text-lg font-medium text-gray-900">
                                {func.display_name}
                              </h4>
                            </div>
                            <span className="ml-3 text-sm text-gray-500">
                              {func.function_name}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            {/* Model Status */}
                            {func.model_assignment ? (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                {func.model_assignment.model_name}
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                Brak modelu
                              </span>
                            )}
                            <span className="text-sm text-gray-500">
                              {func.prompts.length} prompt{func.prompts.length !== 1 ? 'y' : ''}
                            </span>
                          </div>
                        </div>
                      </div>

                      {expandedFunctions.has(func.function_name) && (
                        <div className="border-t bg-gray-50 p-4 space-y-4">
                          {/* Model Assignment Section */}
                          <div className="bg-white rounded-lg border p-4">
                            <div className="flex items-center justify-between mb-3">
                              <h5 className="text-sm font-medium text-gray-900">Przypisanie Modelu</h5>
                              <button
                                onClick={() => handleEditModel(func.function_name, func.model_assignment?.model_name)}
                                className="text-sm text-blue-600 hover:text-blue-700"
                              >
                                <Edit3 className="w-4 h-4" />
                              </button>
                            </div>
                            
                            {editingModel === func.function_name ? (
                              <div className="space-y-2">
                                <select
                                  value={editModelName}
                                  onChange={(e) => setEditModelName(e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                  <option value="">Wybierz model</option>
                                  {aiData.available_models.map(model => (
                                    <option key={model} value={model}>{model}</option>
                                  ))}
                                </select>
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => handleSaveModel(func.function_name, func.model_assignment || undefined)}
                                    disabled={!editModelName}
                                    className="flex items-center px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                                  >
                                    <Save className="w-3 h-3 mr-1" />
                                    Zapisz
                                  </button>
                                  <button
                                    onClick={() => {
                                      setEditingModel(null)
                                      setEditModelName('')
                                    }}
                                    className="flex items-center px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
                                  >
                                    <X className="w-3 h-3 mr-1" />
                                    Anuluj
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <div className="flex items-center">
                                {func.model_assignment ? (
                                  <span className="text-sm text-gray-700">
                                    Aktualny model: <strong>{func.model_assignment.model_name}</strong>
                                  </span>
                                ) : (
                                  <span className="text-sm text-red-600">
                                    Brak przypisanego modelu
                                  </span>
                                )}
                              </div>
                            )}
                          </div>

                          {/* Prompts Section */}
                          <div className="space-y-3">
                            <h5 className="text-sm font-medium text-gray-900">Prompty</h5>
                            {func.prompts.map((prompt) => (
                              <div key={prompt.id} className="bg-white rounded-lg border p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <div className="flex-1">
                                    <div className="flex items-center">
                                      <h6 className="text-sm font-medium text-gray-900">
                                        {prompt.prompt_name}
                                      </h6>
                                      <span className="ml-2 text-xs text-gray-500">
                                        v{prompt.version}
                                      </span>
                                      {prompt.is_custom && (
                                        <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                                          Własny
                                        </span>
                                      )}
                                    </div>
                                    {prompt.description && (
                                      <p className="mt-1 text-xs text-gray-600">
                                        {prompt.description}
                                      </p>
                                    )}
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <button
                                      onClick={() => togglePromptVisibility(prompt.id)}
                                      className="text-gray-400 hover:text-gray-600"
                                    >
                                      {showPromptContent.has(prompt.id) ? 
                                        <EyeOff className="w-4 h-4" /> : 
                                        <Eye className="w-4 h-4" />
                                      }
                                    </button>
                                    <button
                                      onClick={() => copyToClipboard(prompt.prompt_template)}
                                      className="text-gray-400 hover:text-gray-600"
                                    >
                                      <Copy className="w-4 h-4" />
                                    </button>
                                    <button
                                      onClick={() => handleEditPrompt(prompt)}
                                      className="text-blue-600 hover:text-blue-700"
                                    >
                                      <Edit3 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </div>
                                
                                {showPromptContent.has(prompt.id) && (
                                  <div className="mt-3">
                                    {editingPrompt?.id === prompt.id ? (
                                      <div className="space-y-2">
                                        <textarea
                                          value={editPromptContent}
                                          onChange={(e) => setEditPromptContent(e.target.value)}
                                          className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-mono"
                                          placeholder="Wprowadź szablon promptu..."
                                        />
                                        <div className="flex space-x-2">
                                          <button
                                            onClick={handleSavePrompt}
                                            disabled={updatePromptMutation.isPending}
                                            className="flex items-center px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                                          >
                                            <Save className="w-3 h-3 mr-1" />
                                            Zapisz
                                          </button>
                                          <button
                                            onClick={handleCancelEdit}
                                            className="flex items-center px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
                                          >
                                            <X className="w-3 h-3 mr-1" />
                                            Anuluj
                                          </button>
                                        </div>
                                      </div>
                                    ) : (
                                      <div className="bg-gray-50 rounded-md p-3">
                                        <pre className="text-sm text-gray-700 whitespace-pre-wrap break-words">
                                          {prompt.prompt_template}
                                        </pre>
                                      </div>
                                    )}
                                  </div>
                                )}
                                
                                <div className="mt-2 text-xs text-gray-500">
                                  Utworzono: {new Date(prompt.created_at).toLocaleString('pl-PL')}
                                  {prompt.updated_at && prompt.updated_at !== prompt.created_at && (
                                    <span className="ml-2">
                                      • Ostatnia modyfikacja: {new Date(prompt.updated_at).toLocaleString('pl-PL')}
                                    </span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        ))}
      </div>
    </div>
  )
}