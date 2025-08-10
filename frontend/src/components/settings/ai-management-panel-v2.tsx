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
  Check,
  ExternalLink
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

interface AIPrompt {
  id: number
  prompt_name: string
  prompt_template: string
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
  description: string
  status: string
  model_assignment?: AIModelAssignment
  prompts: AIPrompt[]
  last_used?: string
  usage_count?: number
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

export function AIManagementPanelV2() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [expandedFunctions, setExpandedFunctions] = useState<Set<string>>(new Set())
  const [editingPrompt, setEditingPrompt] = useState<AIPrompt | null>(null)
  const [editingModel, setEditingModel] = useState<string | null>(null)
  const [editPromptContent, setEditPromptContent] = useState('')
  const [editModelName, setEditModelName] = useState('')
  const [showPromptContent, setShowPromptContent] = useState<Set<number>>(new Set())

  // Fetch AI functions data
  const { data: aiData, isLoading, error } = useQuery<AIFunctionsGrouped>({
    queryKey: ['ai-functions-grouped'],
    queryFn: () => api.aiManagement.getAIFunctions(),
  })

  // Fetch health check data
  const { data: healthData } = useQuery<AIHealthCheck>({
    queryKey: ['ai-functions-health'],
    queryFn: () => api.aiManagement.getHealthCheck(),
  })

  // Mutations
  const updatePromptMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: any }) => {
      console.log('[AI Management] updatePrompt mutation called', { id, data })
      return api.aiManagement.updatePrompt(id, data)
    },
    onSuccess: (result) => {
      console.log('[AI Management] updatePrompt success', result)
      queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped'] })
      queryClient.invalidateQueries({ queryKey: ['ai-functions-health'] })
      setEditingPrompt(null)
      setEditPromptContent('')
    },
    onError: (error) => {
      console.error('[AI Management] updatePrompt error', error)
    }
  })

  const createModelAssignmentMutation = useMutation({
    mutationFn: (data: { task_name: string, model_name: string }) => {
      console.log('[AI Management] createModelAssignment mutation called', data)
      return api.aiManagement.createModelAssignment({ 
        function_name: data.task_name, 
        task_name: data.task_name, 
        model_name: data.model_name 
      })
    },
    onSuccess: (result) => {
      console.log('[AI Management] createModelAssignment success', result)
      queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped'] })
      queryClient.invalidateQueries({ queryKey: ['ai-functions-health'] })
      setEditingModel(null)
      setEditModelName('')
    },
    onError: (error) => {
      console.error('[AI Management] createModelAssignment error', error)
    }
  })

  const updateModelAssignmentMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: any }) => {
      console.log('[AI Management] updateModelAssignment mutation called', { id, data })
      return api.aiManagement.updateModelAssignment(id, data)
    },
    onSuccess: (result) => {
      console.log('[AI Management] updateModelAssignment success', result)
      queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped'] })
      queryClient.invalidateQueries({ queryKey: ['ai-functions-health'] })
      setEditingModel(null)
      setEditModelName('')
    },
    onError: (error) => {
      console.error('[AI Management] updateModelAssignment error', error)
    }
  })

  // Handlers
  const handleEditPrompt = (prompt: AIPrompt) => {
    setEditingPrompt(prompt)
    setEditPromptContent(prompt.prompt_template)
  }

  const handleSavePrompt = () => {
    console.log('[AI Management] handleSavePrompt called', {
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

  const handleEditModel = (functionName: string, currentModel?: string) => {
    setEditingModel(functionName)
    setEditModelName(currentModel || '')
  }

  const handleSaveModel = (functionName: string, existingAssignment?: AIModelAssignment) => {
    console.log('[AI Management] handleSaveModel called', {
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'critical': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-50 border-green-200'
      case 'warning': return 'bg-yellow-50 border-yellow-200'
      case 'critical': return 'bg-red-50 border-red-200'
      default: return 'bg-gray-50 border-gray-200'
    }
  }

  const getCategoryIcon = (iconName: string) => {
    switch (iconName) {
      case 'edit': return <FileText className="w-5 h-5" />
      case 'analytics': return <BarChart3 className="w-5 h-5" />
      case 'settings': return <Settings className="w-5 h-5" />
      default: return <Bot className="w-5 h-5" />
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">Ładowanie konfiguracji AI...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-red-50 border border-red-200 rounded-xl p-6"
      >
        <div className="flex items-start">
          <AlertCircle className="w-6 h-6 text-red-500 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-red-800">Błąd ładowania danych</h3>
            <p className="text-red-700 mt-1">
              Nie udało się załadować konfiguracji AI. Sprawdź połączenie z serwerem i spróbuj ponownie.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Odśwież stronę
            </button>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-100"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl mr-4">
                <Brain className="w-8 h-8 text-white" />
              </div>
              Zarządzanie AI & Prompts
            </h1>
            <p className="text-gray-600 mt-2 text-lg">
              Konfiguruj modele sztucznej inteligencji i zarządzaj promptami systemowymi
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              queryClient.invalidateQueries({ queryKey: ['ai-functions-grouped'] })
              queryClient.invalidateQueries({ queryKey: ['ai-functions-health'] })
            }}
            className="flex items-center px-4 py-2 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all shadow-sm"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Odśwież
          </motion.button>
        </div>
      </motion.div>

      {/* Health Dashboard */}
      {healthData && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`rounded-2xl border-2 p-6 ${getStatusBg(healthData.status)}`}
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="p-3 bg-white rounded-xl shadow-sm mr-4">
                <Activity className={`w-6 h-6 ${getStatusColor(healthData.status)}`} />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Status Systemu AI</h2>
                <p className="text-gray-600">Ogólny stan konfiguracji</p>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-3xl font-bold ${getStatusColor(healthData.status)}`}>
                {Math.round(healthData.health_score * 100)}%
              </div>
              <div className={`text-sm font-medium ${getStatusColor(healthData.status)}`}>
                {healthData.status === 'healthy' ? 'Zdrowy' : 
                 healthData.status === 'warning' ? 'Ostrzeżenie' : 'Krytyczny'}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl p-4 shadow-sm border">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Cpu className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="text-sm font-medium text-gray-700">Funkcje AI</span>
                </div>
                <span className="text-xl font-bold text-gray-900">
                  {healthData.configured_functions}/{healthData.total_functions}
                </span>
              </div>
              <div className="mt-2 bg-gray-100 rounded-full h-2">
                <div 
                  className="bg-blue-600 rounded-full h-2 transition-all duration-500"
                  style={{ width: `${(healthData.configured_functions / healthData.total_functions) * 100}%` }}
                />
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-4 shadow-sm border">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Terminal className="w-5 h-5 text-green-600 mr-2" />
                  <span className="text-sm font-medium text-gray-700">Prompty</span>
                </div>
                <span className="text-xl font-bold text-gray-900">
                  {aiData?.total_prompts || 0}
                </span>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-4 shadow-sm border">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Database className="w-5 h-5 text-purple-600 mr-2" />
                  <span className="text-sm font-medium text-gray-700">Modele</span>
                </div>
                <span className="text-xl font-bold text-gray-900">
                  {aiData?.total_model_assignments || 0}
                </span>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {healthData.recommendations && healthData.recommendations.filter(Boolean).length > 0 && (
            <div className="mt-6 bg-white rounded-xl p-4 border border-amber-200">
              <div className="flex items-start">
                <Sparkles className="w-5 h-5 text-amber-600 mr-3 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-amber-800">Zalecenia optymalizacji</h4>
                  <ul className="text-sm text-amber-700 mt-2 space-y-1">
                    {healthData.recommendations.filter(Boolean).map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="w-1.5 h-1.5 bg-amber-600 rounded-full mr-2 mt-2 flex-shrink-0" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* AI Functions Categories */}
      <div className="space-y-4">
        {aiData && Object.entries(aiData.categories).map(([categoryKey, category], index) => (
          category.functions.length > 0 && (
            <motion.div 
              key={categoryKey}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden"
            >
              <motion.div 
                className="p-6 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setSelectedCategory(selectedCategory === categoryKey ? null : categoryKey)}
                whileHover={{ x: 4 }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="p-3 bg-gradient-to-r from-gray-100 to-gray-200 rounded-xl mr-4">
                      {getCategoryIcon(category.icon)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                      <p className="text-gray-600">{category.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                      {category.functions.length} funkcji
                    </span>
                    <motion.div
                      animate={{ rotate: selectedCategory === categoryKey ? 180 : 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    </motion.div>
                  </div>
                </div>
              </motion.div>

              <AnimatePresence>
                {selectedCategory === categoryKey && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="p-6 bg-gray-50 space-y-4">
                      {category.functions.map((func) => (
                        <motion.div 
                          key={func.function_name}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="bg-white rounded-xl border border-gray-200 overflow-hidden"
                        >
                          <div 
                            className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                            onClick={() => {
                              const newExpanded = new Set(expandedFunctions)
                              if (newExpanded.has(func.function_name)) {
                                newExpanded.delete(func.function_name)
                              } else {
                                newExpanded.add(func.function_name)
                              }
                              setExpandedFunctions(newExpanded)
                            }}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center">
                                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                                  <Zap className="w-4 h-4 text-blue-600" />
                                </div>
                                <div>
                                  <h4 className="font-medium text-gray-900">{func.function_name}</h4>
                                  <p className="text-sm text-gray-600">{func.description}</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <span className={`text-xs px-2 py-1 rounded-full ${
                                  func.model_assignment ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {func.model_assignment ? 'Skonfigurowano' : 'Wymaga konfiguracji'}
                                </span>
                                <motion.div
                                  animate={{ rotate: expandedFunctions.has(func.function_name) ? 180 : 0 }}
                                  transition={{ duration: 0.2 }}
                                >
                                  <ChevronDown className="w-4 h-4 text-gray-400" />
                                </motion.div>
                              </div>
                            </div>
                          </div>

                          <AnimatePresence>
                            {expandedFunctions.has(func.function_name) && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.3 }}
                                className="border-t border-gray-100 bg-gray-50 p-4 space-y-4"
                              >
                                {/* Model Assignment Section */}
                                <div className="bg-white rounded-lg border border-gray-200 p-4">
                                  <div className="flex items-center justify-between mb-3">
                                    <h5 className="font-medium text-gray-900 flex items-center">
                                      <Cpu className="w-4 h-4 mr-2 text-blue-600" />
                                      Przypisanie Modelu AI
                                    </h5>
                                    {!editingModel || editingModel !== func.function_name ? (
                                      <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => handleEditModel(func.function_name, func.model_assignment?.model_name)}
                                        className="text-blue-600 hover:text-blue-700 p-1"
                                      >
                                        <Edit3 className="w-4 h-4" />
                                      </motion.button>
                                    ) : null}
                                  </div>
                                  
                                  {editingModel === func.function_name ? (
                                    <div className="space-y-3">
                                      <select
                                        value={editModelName}
                                        onChange={(e) => setEditModelName(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      >
                                        <option value="">Wybierz model AI</option>
                                        {aiData.available_models.map(model => (
                                          <option key={model} value={model}>{model}</option>
                                        ))}
                                      </select>
                                      <div className="flex space-x-2">
                                        <motion.button
                                          whileHover={{ scale: 1.05 }}
                                          whileTap={{ scale: 0.95 }}
                                          onClick={() => handleSaveModel(func.function_name, func.model_assignment || undefined)}
                                          disabled={!editModelName || updateModelAssignmentMutation.isPending || createModelAssignmentMutation.isPending}
                                          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                        >
                                          {(updateModelAssignmentMutation.isPending || createModelAssignmentMutation.isPending) ? (
                                            <LoadingSpinner size="small" className="mr-2" />
                                          ) : (
                                            <Save className="w-4 h-4 mr-2" />
                                          )}
                                          Zapisz
                                        </motion.button>
                                        <motion.button
                                          whileHover={{ scale: 1.05 }}
                                          whileTap={{ scale: 0.95 }}
                                          onClick={() => {
                                            setEditingModel(null)
                                            setEditModelName('')
                                          }}
                                          className="flex items-center px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-all"
                                        >
                                          <X className="w-4 h-4 mr-2" />
                                          Anuluj
                                        </motion.button>
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="flex items-center justify-between">
                                      {func.model_assignment ? (
                                        <div className="flex items-center">
                                          <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                                          <span className="text-sm text-gray-700">
                                            <strong>{func.model_assignment.model_name}</strong>
                                          </span>
                                        </div>
                                      ) : (
                                        <div className="flex items-center">
                                          <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2" />
                                          <span className="text-sm text-gray-500">Brak przypisanego modelu</span>
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>

                                {/* Prompts Section */}
                                <div className="bg-white rounded-lg border border-gray-200 p-4">
                                  <h5 className="font-medium text-gray-900 flex items-center mb-3">
                                    <Terminal className="w-4 h-4 mr-2 text-green-600" />
                                    Prompty Systemowe
                                    <span className="ml-2 text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                      {func.prompts.length}
                                    </span>
                                  </h5>
                                  
                                  <div className="space-y-3">
                                    {func.prompts.map((prompt) => (
                                      <motion.div 
                                        key={prompt.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="border border-gray-200 rounded-lg overflow-hidden"
                                      >
                                        <div className="p-3 bg-gray-50 border-b border-gray-200">
                                          <div className="flex items-center justify-between">
                                            <div>
                                              <h6 className="text-sm font-medium text-gray-900">{prompt.prompt_name}</h6>
                                              <p className="text-xs text-gray-500">Wersja {prompt.version}</p>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                              <motion.button
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                                onClick={() => {
                                                  const newVisible = new Set(showPromptContent)
                                                  if (newVisible.has(prompt.id)) {
                                                    newVisible.delete(prompt.id)
                                                  } else {
                                                    newVisible.add(prompt.id)
                                                  }
                                                  setShowPromptContent(newVisible)
                                                }}
                                                className="text-gray-400 hover:text-gray-600 p-1"
                                              >
                                                {showPromptContent.has(prompt.id) ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                              </motion.button>
                                              <motion.button
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                                onClick={() => copyToClipboard(prompt.prompt_template)}
                                                className="text-gray-400 hover:text-gray-600 p-1"
                                              >
                                                <Copy className="w-4 h-4" />
                                              </motion.button>
                                              <motion.button
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                                onClick={() => handleEditPrompt(prompt)}
                                                className="text-blue-600 hover:text-blue-700 p-1"
                                              >
                                                <Edit3 className="w-4 h-4" />
                                              </motion.button>
                                            </div>
                                          </div>
                                        </div>
                                        
                                        <AnimatePresence>
                                          {showPromptContent.has(prompt.id) && (
                                            <motion.div
                                              initial={{ height: 0, opacity: 0 }}
                                              animate={{ height: 'auto', opacity: 1 }}
                                              exit={{ height: 0, opacity: 0 }}
                                              transition={{ duration: 0.3 }}
                                              className="p-3"
                                            >
                                              {editingPrompt?.id === prompt.id ? (
                                                <div className="space-y-3">
                                                  <textarea
                                                    value={editPromptContent}
                                                    onChange={(e) => setEditPromptContent(e.target.value)}
                                                    className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-mono"
                                                    placeholder="Wprowadź szablon promptu..."
                                                  />
                                                  <div className="flex space-x-2">
                                                    <motion.button
                                                      whileHover={{ scale: 1.05 }}
                                                      whileTap={{ scale: 0.95 }}
                                                      onClick={handleSavePrompt}
                                                      disabled={updatePromptMutation.isPending}
                                                      className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                                    >
                                                      {updatePromptMutation.isPending ? (
                                                        <LoadingSpinner size="small" className="mr-2" />
                                                      ) : (
                                                        <Save className="w-4 h-4 mr-2" />
                                                      )}
                                                      Zapisz
                                                    </motion.button>
                                                    <motion.button
                                                      whileHover={{ scale: 1.05 }}
                                                      whileTap={{ scale: 0.95 }}
                                                      onClick={() => {
                                                        setEditingPrompt(null)
                                                        setEditPromptContent('')
                                                      }}
                                                      className="flex items-center px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-all"
                                                    >
                                                      <X className="w-4 h-4 mr-2" />
                                                      Anuluj
                                                    </motion.button>
                                                  </div>
                                                </div>
                                              ) : (
                                                <div className="bg-gray-900 rounded-lg p-3">
                                                  <pre className="text-sm text-green-400 whitespace-pre-wrap break-words font-mono">
                                                    {prompt.prompt_template}
                                                  </pre>
                                                </div>
                                              )}
                                            </motion.div>
                                          )}
                                        </AnimatePresence>
                                      </motion.div>
                                    ))}
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        ))}
      </div>
    </div>
  )
}
