'use client'

import React, { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Users, 
  MessageSquare, 
  Target,
  Palette,
  Ban,
  Heart,
  MousePointer,
  Eye,
  ArrowLeft,
  List,
  Calendar,
  ChevronRight
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { CommunicationStrategy, StrategyUploadResponse, StrategyTaskStatus } from '@/types'

interface StrategyPanelProps {
  organizationId: number
}

type ViewMode = 'upload' | 'list' | 'details'

export function StrategyPanel({ organizationId }: StrategyPanelProps) {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadingTask, setUploadingTask] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [selectedStrategyId, setSelectedStrategyId] = useState<number | null>(null)

  // Pobieranie listy strategii
  const { data: strategiesData, isLoading, error } = useQuery({
    queryKey: ['strategies', organizationId],
    queryFn: () => api.strategies.getStrategies(organizationId),
    enabled: !!organizationId
  })

  // Pobieranie szczegółów strategii
  const { data: selectedStrategy, isLoading: strategyLoading } = useQuery({
    queryKey: ['strategy-details', organizationId, selectedStrategyId],
    queryFn: () => selectedStrategyId ? api.strategies.getStrategy(organizationId, selectedStrategyId) : null,
    enabled: !!selectedStrategyId && viewMode === 'details'
  })

  // Monitoring statusu uploadu
  const { data: taskStatus } = useQuery({
    queryKey: ['strategy-task', uploadingTask],
    queryFn: () => uploadingTask ? api.strategies.getTaskStatus(organizationId, uploadingTask) : null,
    enabled: !!uploadingTask,
    refetchInterval: 2000
  })

  // Mutacja uploadu pliku
  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.strategies.upload(organizationId, file),
    onSuccess: (response: StrategyUploadResponse) => {
      setUploadingTask(response.task_id)
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    },
    onError: (error) => {
      console.error('Upload failed:', error)
      setSelectedFile(null)
    }
  })

  // Obsługa zakończenia zadania
  React.useEffect(() => {
    if (taskStatus?.status === 'SUCCESS') {
      queryClient.invalidateQueries({ queryKey: ['strategies', organizationId] })
      setUploadingTask(null)
    } else if (taskStatus?.status === 'FAILURE') {
      setUploadingTask(null)
    }
  }, [taskStatus, queryClient, organizationId])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile)
    }
  }

  const handleFileClick = () => {
    fileInputRef.current?.click()
  }

  const handleStrategyClick = (strategyId: number) => {
    setSelectedStrategyId(strategyId)
    setViewMode('details')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const renderUploadStatus = () => {
    if (uploadMutation.isPending) {
      return (
        <div className="flex items-center gap-2 text-blue-600">
          <Clock className="animate-spin" size={20} />
          <span>Przesyłanie pliku...</span>
        </div>
      )
    }

    if (uploadingTask && taskStatus) {
      const { status, result, current, total } = taskStatus
      
      if (status === 'PENDING' || status === 'PROGRESS') {
        return (
          <div className="flex items-center gap-2 text-blue-600">
            <Clock className="animate-spin" size={20} />
            <div>
              <span>Analizowanie strategii...</span>
              {current && total && (
                <div className="text-sm text-gray-500 mt-1">
                  Krok {current} z {total}
                </div>
              )}
            </div>
          </div>
        )
      }

      if (status === 'SUCCESS' && result?.status === 'SUCCESS') {
        return (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle size={20} />
            <span>Strategia została pomyślnie przeanalizowana!</span>
          </div>
        )
      }

      if (status === 'FAILURE' || result?.status === 'FAILED') {
        return (
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle size={20} />
            <div>
              <span>Błąd podczas analizy strategii</span>
              {result?.error && (
                <div className="text-sm text-red-500 mt-1">{result.error}</div>
              )}
            </div>
          </div>
        )
      }
    }

    return null
  }

  const renderNavigation = () => (
    <div className="flex items-center gap-4 mb-6">
      {viewMode !== 'list' && (
        <button
          onClick={() => {
            setViewMode('list')
            setSelectedStrategyId(null)
          }}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft size={20} />
          <span>Powrót do listy</span>
        </button>
      )}
      
      <div className="flex items-center gap-2">
        <button
          onClick={() => setViewMode('list')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium ${
            viewMode === 'list' 
              ? 'bg-blue-100 text-blue-700' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <List size={16} />
          <span>Lista strategii</span>
        </button>
        
        <button
          onClick={() => setViewMode('upload')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium ${
            viewMode === 'upload' 
              ? 'bg-blue-100 text-blue-700' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Upload size={16} />
          <span>Wgraj strategię</span>
        </button>
      </div>
    </div>
  )

  const renderUploadView = () => (
    <Card>
      <div className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Wgraj nową strategię komunikacji
        </h3>
        
        <div className="space-y-4">
          <div>
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.txt,.html,.rtf"
              className="hidden"
            />
            
            <div 
              onClick={handleFileClick}
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 cursor-pointer transition-colors"
            >
              <Upload size={32} className="mx-auto text-gray-400 mb-2" />
              <p className="text-sm text-gray-600 mb-1">
                Kliknij aby wybrać plik lub przeciągnij tutaj
              </p>
              <p className="text-xs text-gray-500">
                Obsługiwane formaty: PDF, DOC, DOCX, TXT, HTML, RTF (max 10MB)
              </p>
            </div>
          </div>

          {selectedFile && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={20} className="text-blue-600" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">{selectedFile.name}</p>
                    <p className="text-xs text-blue-600">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  onClick={handleUpload}
                  disabled={uploadMutation.isPending || !!uploadingTask}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Prześlij do analizy
                </button>
              </div>
            </div>
          )}

          {renderUploadStatus()}
        </div>
      </div>
    </Card>
  )

  const renderStrategyList = () => {
    const strategies = strategiesData?.strategies || []

    if (strategies.length === 0) {
      return (
        <Card>
          <div className="p-6 text-center">
            <FileText size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Brak strategii komunikacji
            </h3>
            <p className="text-gray-600 mb-4">
              Wgraj plik ze strategią komunikacji, aby rozpocząć analizę AI
            </p>
            <button
              onClick={() => setViewMode('upload')}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Wgraj pierwszą strategię
            </button>
          </div>
        </Card>
      )
    }

    return (
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Strategie komunikacji ({strategies.length})
            </h3>
            <button
              onClick={() => setViewMode('upload')}
              className="px-3 py-1 text-sm font-medium text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50"
            >
              Wgraj nową
            </button>
          </div>
          
          <div className="space-y-3">
            {strategies.map((strategy: any) => (
              <motion.div
                key={strategy.id}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => handleStrategyClick(strategy.id)}
                className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-gray-900 group-hover:text-blue-600">
                        {strategy.name}
                      </h4>
                      {strategy.id === strategies[0].id && (
                        <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">
                          Najnowsza
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Calendar size={14} />
                        <span>{new Date(strategy.created_at).toLocaleDateString('pl-PL')}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Eye size={14} />
                        <span>ID: {strategy.id}</span>
                      </div>
                      {strategy.target_audiences && (
                        <div className="flex items-center gap-1">
                          <Users size={14} />
                          <span>{strategy.target_audiences.length} grup docelowych</span>
                        </div>
                      )}
                    </div>

                    {strategy.description && (
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                        {strategy.description}
                      </p>
                    )}
                  </div>
                  
                  <ChevronRight size={20} className="text-gray-400 group-hover:text-blue-600" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </Card>
    )
  }

  const renderStrategyDetails = () => {
    if (strategyLoading) {
      return (
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner size="large" />
        </div>
      )
    }

    if (!selectedStrategy) {
      return (
        <Card>
          <div className="p-6 text-center">
            <AlertCircle size={48} className="mx-auto text-red-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Błąd ładowania strategii</h3>
            <p className="text-gray-600">Nie udało się załadować szczegółów strategii</p>
          </div>
        </Card>
      )
    }

    return (
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{selectedStrategy.name}</h3>
              <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                <div className="flex items-center gap-1">
                  <Calendar size={14} />
                  <span>Utworzona: {new Date(selectedStrategy.created_at).toLocaleDateString('pl-PL')}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Eye size={14} />
                  <span>ID: {selectedStrategy.id}</span>
                </div>
              </div>
            </div>
          </div>

          {selectedStrategy.description && (
            <div className="mb-6">
              <p className="text-gray-700">{selectedStrategy.description}</p>
            </div>
          )}
          
          <div className="space-y-6">
            {/* Cele komunikacyjne */}
            {selectedStrategy.communication_goals && selectedStrategy.communication_goals.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Target size={20} className="text-blue-600" />
                  <h5 className="font-medium text-gray-900">Cele komunikacyjne</h5>
                </div>
                <ul className="space-y-2">
                  {selectedStrategy.communication_goals.map((goal: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-gray-700">{goal}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Grupy docelowe */}
            {selectedStrategy.target_audiences && selectedStrategy.target_audiences.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Users size={20} className="text-green-600" />
                  <h5 className="font-medium text-gray-900">Grupy docelowe</h5>
                </div>
                <div className="grid md:grid-cols-2 gap-3">
                  {selectedStrategy.target_audiences.map((audience: any) => (
                    <div key={audience.id} className="bg-gray-50 p-4 rounded-lg">
                      <h6 className="font-medium text-gray-900 mb-2">{audience.name}</h6>
                      <p className="text-sm text-gray-600">{audience.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Style platformowe */}
            {selectedStrategy.platform_styles && selectedStrategy.platform_styles.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare size={20} className="text-purple-600" />
                  <h5 className="font-medium text-gray-900">Style platformowe</h5>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  {selectedStrategy.platform_styles.map((style: any) => (
                    <div key={style.id} className="bg-gray-50 p-4 rounded-lg">
                      <h6 className="font-medium text-gray-900 mb-2">{style.platform_name}</h6>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Długość: </span>
                          <span className="text-gray-600">{style.length_description}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Styl: </span>
                          <span className="text-gray-600">{style.style_description}</span>
                        </div>
                        {style.notes && (
                          <div>
                            <span className="font-medium text-gray-700">Uwagi: </span>
                            <span className="text-gray-600">{style.notes}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Styl komunikacji */}
            {selectedStrategy.general_style && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Palette size={20} className="text-indigo-600" />
                  <h5 className="font-medium text-gray-900">Ogólny styl komunikacji</h5>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg grid md:grid-cols-2 gap-4">
                  <div>
                    <span className="font-medium text-gray-700">Język: </span>
                    <span className="text-gray-600">{selectedStrategy.general_style.language}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Ton: </span>
                    <span className="text-gray-600">{selectedStrategy.general_style.tone}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Treści techniczne: </span>
                    <span className="text-gray-600">{selectedStrategy.general_style.technical_content}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Employer branding: </span>
                    <span className="text-gray-600">{selectedStrategy.general_style.employer_branding_content}</span>
                  </div>
                </div>
              </div>
            )}

            {/* CTA Rules */}
            {selectedStrategy.cta_rules && selectedStrategy.cta_rules.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <MousePointer size={20} className="text-orange-600" />
                  <h5 className="font-medium text-gray-900">Zasady Call-to-Action</h5>
                </div>
                <div className="space-y-3">
                  {selectedStrategy.cta_rules.map((rule: any) => (
                    <div key={rule.id} className="bg-gray-50 p-3 rounded-lg">
                      <div className="font-medium text-gray-900">{rule.content_type}</div>
                      <div className="text-gray-600 mt-1">"{rule.cta_text}"</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Zakazane i preferowane zwroty */}
            <div className="grid md:grid-cols-2 gap-6">
              {selectedStrategy.forbidden_phrases && selectedStrategy.forbidden_phrases.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Ban size={20} className="text-red-600" />
                    <h5 className="font-medium text-gray-900">Zakazane zwroty</h5>
                  </div>
                  <div className="space-y-2">
                    {selectedStrategy.forbidden_phrases.map((phrase: string, index: number) => (
                      <span key={index} className="inline-block bg-red-50 text-red-700 px-3 py-1 rounded-full text-sm mr-2 mb-2">
                        {phrase}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedStrategy.preferred_phrases && selectedStrategy.preferred_phrases.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Heart size={20} className="text-green-600" />
                    <h5 className="font-medium text-gray-900">Preferowane zwroty</h5>
                  </div>
                  <div className="space-y-2">
                    {selectedStrategy.preferred_phrases.map((phrase: string, index: number) => (
                      <span key={index} className="inline-block bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm mr-2 mb-2">
                        {phrase}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Sample Content Types */}
            {selectedStrategy.sample_content_types && selectedStrategy.sample_content_types.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <FileText size={20} className="text-cyan-600" />
                  <h5 className="font-medium text-gray-900">Przykładowe typy treści</h5>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedStrategy.sample_content_types.map((type: string, index: number) => (
                    <span key={index} className="bg-cyan-50 text-cyan-700 px-3 py-1 rounded-full text-sm">
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle size={48} className="mx-auto text-red-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Błąd ładowania strategii</h3>
        <p className="text-gray-600">Spróbuj odświeżyć stronę</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {renderNavigation()}
      
      {viewMode === 'upload' && renderUploadView()}
      {viewMode === 'list' && renderStrategyList()}
      {viewMode === 'details' && renderStrategyDetails()}
    </div>
  )
} 