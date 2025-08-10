'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Plus, 
  Filter, 
  User,
  Calendar,
  FolderOpen,
  CheckSquare,
  Zap
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { useOrganizationStore } from '@/stores'
import { TaskWithDetails, TaskStatus, TaskPriority } from '@/types'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'

interface TaskManagerProps {
  expanded?: boolean
}

export function TaskManager({ expanded = false }: TaskManagerProps) {
  const toast = useToast()
  const router = useRouter()
  const [selectedTask, setSelectedTask] = useState<string>('')
  const [filter, setFilter] = useState<{
    status?: TaskStatus
    priority?: TaskPriority
  }>({})
  
  const { currentOrganization } = useOrganizationStore()

  // Fetch tasks for current organization
  const { data: tasks, isLoading, refetch } = useQuery({
    queryKey: ['tasks', currentOrganization?.id, filter],
    queryFn: () => currentOrganization ? api.tasks.list({
      org_id: currentOrganization.id,
      status: filter.status,
    }) : Promise.resolve([]),
    enabled: !!currentOrganization,
  })

  // Test Celery connection
  const testCeleryMutation = useMutation({
    mutationFn: () => api.health.celery(),
    onSuccess: (data) => {
      console.log('Celery task started:', data.data)
    },
  })

  const handleRunCeleryTest = async () => {
    setSelectedTask('celery-test')
    try {
      await testCeleryMutation.mutateAsync()
    } catch (error) {
      console.error('Celery test failed:', error)
    } finally {
      setSelectedTask('')
    }
  }

  const getStatusStyles = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.PENDING:
        return {
          bg: 'bg-gradient-to-r from-yellow-50 to-orange-50',
          border: 'border-yellow-200',
          badge: 'bg-yellow-500',
          text: 'text-yellow-700'
        }
      case TaskStatus.IN_PROGRESS:
        return {
          bg: 'bg-gradient-to-r from-blue-50 to-indigo-50',
          border: 'border-blue-200',
          badge: 'bg-blue-500',
          text: 'text-blue-700'
        }
      case TaskStatus.COMPLETED:
        return {
          bg: 'bg-gradient-to-r from-emerald-50 to-teal-50',
          border: 'border-emerald-200',
          badge: 'bg-emerald-500',
          text: 'text-emerald-700'
        }
      case TaskStatus.CANCELLED:
        return {
          bg: 'bg-gradient-to-r from-red-50 to-pink-50',
          border: 'border-red-200',
          badge: 'bg-red-500',
          text: 'text-red-700'
        }
      default:
        return {
          bg: 'bg-gradient-to-r from-gray-50 to-slate-50',
          border: 'border-gray-200',
          badge: 'bg-gray-500',
          text: 'text-gray-700'
        }
    }
  }

  const getPriorityStyles = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.LOW:
        return { color: 'text-emerald-600', icon: '🟢' }
      case TaskPriority.MEDIUM:
        return { color: 'text-yellow-600', icon: '🟡' }
      case TaskPriority.HIGH:
        return { color: 'text-orange-600', icon: '🟠' }
      case TaskPriority.URGENT:
        return { color: 'text-red-600', icon: '🔴' }
      default:
        return { color: 'text-gray-600', icon: '⚫' }
    }
  }

  if (!currentOrganization) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-2xl shadow-lg border border-gray-100 p-8"
      >
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl text-white mb-4"
          >
            <CheckSquare className="h-8 w-8" />
          </motion.div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Zarządzanie zadaniami
          </h3>
          <p className="text-gray-500">
            Wybierz organizację, aby zobaczyć zadania i projekty
          </p>
        </div>
      </motion.div>
    )
  }

  return (
    <div className="space-y-6">
      {!expanded && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-700 rounded-2xl p-6 text-white shadow-xl"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="p-3 bg-white/20 rounded-xl backdrop-blur-sm"
              >
                <CheckSquare className="h-6 w-6" />
              </motion.div>
              <div>
                <h2 className="text-xl font-semibold">Zadania {currentOrganization.name}</h2>
                <p className="text-purple-100">Zarządzanie projektami i zadaniami zespołu</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleRunCeleryTest}
                disabled={testCeleryMutation.isPending}
                className="px-4 py-2 bg-white/20 rounded-xl backdrop-blur-sm hover:bg-white/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                {testCeleryMutation.isPending ? (
                  <LoadingSpinner size="small" />
                ) : (
                  <Zap className="w-4 h-4" />
                )}
                <span>Test Celery</span>
              </motion.button>
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  toast.info('Funkcja tworzenia zadań będzie dostępna wkrótce')
                  // TODO: W przyszłości otworzyć modal lub nawigować do formularza
                }}
                className="px-4 py-2 bg-white/20 rounded-xl backdrop-blur-sm hover:bg-white/30 transition-colors flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Nowe zadanie</span>
              </motion.button>
            </div>
          </div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6"
      >
        {/* Filter controls */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filtry:</span>
          </div>
          <select
            value={filter.status || ''}
            onChange={(e) => setFilter(prev => ({ ...prev, status: e.target.value as TaskStatus || undefined }))}
            className="px-4 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Wszystkie statusy</option>
            <option value={TaskStatus.PENDING}>Oczekujące</option>
            <option value={TaskStatus.IN_PROGRESS}>W trakcie</option>
            <option value={TaskStatus.COMPLETED}>Zakończone</option>
            <option value={TaskStatus.CANCELLED}>Anulowane</option>
          </select>
          
          <select
            value={filter.priority || ''}
            onChange={(e) => setFilter(prev => ({ ...prev, priority: e.target.value as TaskPriority || undefined }))}
            className="px-4 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Wszystkie priorytety</option>
            <option value={TaskPriority.LOW}>Niski</option>
            <option value={TaskPriority.MEDIUM}>Średni</option>
            <option value={TaskPriority.HIGH}>Wysoki</option>
            <option value={TaskPriority.URGENT}>Pilny</option>
          </select>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="medium" />
          </div>
        ) : !tasks || tasks.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-12 bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl border border-gray-100"
          >
            <CheckSquare size={80} className="text-blue-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Brak zadań</h3>
            <p className="text-gray-600 mb-6">Nie ma jeszcze żadnych zadań w tej organizacji</p>
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                toast.info('Funkcja tworzenia zadań będzie dostępna wkrótce')
                // TODO: W przyszłości otworzyć modal lub nawigować do formularza
              }}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all flex items-center space-x-2 mx-auto"
            >
              <Plus className="h-5 w-5" />
              <span>Utwórz pierwsze zadanie</span>
            </motion.button>
          </motion.div>
        ) : (
          <div className={`grid gap-6 ${expanded ? 'grid-cols-1' : 'grid-cols-1'}`}>
            <AnimatePresence>
              {tasks.map((task, index) => {
                const statusStyles = getStatusStyles(task.status)
                const priorityStyles = getPriorityStyles(task.priority)
                
                return (
                  <motion.div
                    key={task.id}
                    className={`border rounded-2xl p-6 hover:shadow-lg transition-all duration-300 ${statusStyles.border} ${statusStyles.bg}`}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.95 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.02, y: -2 }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <h3 className="font-semibold text-gray-900 text-lg">{task.title}</h3>
                          <span className={`px-3 py-1 text-xs font-medium text-white rounded-full ${statusStyles.badge}`}>
                            {task.status}
                          </span>
                          <div className="flex items-center space-x-1">
                            <span className="text-sm">{priorityStyles.icon}</span>
                            <span className={`text-xs font-medium ${priorityStyles.color}`}>
                              {task.priority}
                            </span>
                          </div>
                        </div>
                        
                        {task.description && (
                          <p className="text-gray-600 mb-4 bg-white/50 p-3 rounded-lg">{task.description}</p>
                        )}
                        
                        <div className="flex items-center space-x-6 text-sm text-gray-600">
                          {task.assignee && (
                            <div className="flex items-center space-x-2">
                              <User className="h-4 w-4" />
                              <span>{task.assignee.first_name} {task.assignee.last_name}</span>
                            </div>
                          )}
                          {task.due_date && (
                            <div className="flex items-center space-x-2">
                              <Calendar className="h-4 w-4" />
                              <span>{new Date(task.due_date).toLocaleDateString('pl-PL')}</span>
                            </div>
                          )}
                          {task.project && (
                            <div className="flex items-center space-x-2">
                              <FolderOpen className="h-4 w-4" />
                              <span>{task.project.name}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <motion.button
                          className="px-4 py-2 text-sm bg-blue-500 text-white hover:bg-blue-600 rounded-lg transition-colors"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => {
                            toast.info(`Edycja zadania "${task.title}" będzie dostępna wkrótce`)
                            // TODO: Otworzyć modal edycji zadania
                          }}
                        >
                          Edytuj
                        </motion.button>
                        <motion.button
                          className="px-4 py-2 text-sm bg-white/70 text-gray-700 hover:bg-white rounded-lg transition-colors border border-gray-200"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => {
                            toast.info(`Szczegóły zadania "${task.title}" będą dostępne wkrótce`)
                            // TODO: Nawigować do strony szczegółów zadania
                          }}
                        >
                          Szczegóły
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </div>
        )}

        {/* Celery test results */}
        <AnimatePresence>
          {testCeleryMutation.isError && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-6 p-4 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl"
            >
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <p className="text-red-600 font-medium">
                  Błąd Celery: {testCeleryMutation.error?.message}
                </p>
              </div>
            </motion.div>
          )}

          {testCeleryMutation.isSuccess && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl"
            >
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-emerald-500" />
                <p className="text-emerald-600 font-medium">
                  Celery działa poprawnie! System kolejek jest gotowy do pracy.
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  )
}
