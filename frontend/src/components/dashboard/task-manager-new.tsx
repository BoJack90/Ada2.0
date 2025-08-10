'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Clock, CheckCircle, AlertCircle, Plus, Filter } from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { useOrganizationStore } from '@/stores'
import { TaskWithDetails, TaskStatus, TaskPriority } from '@/types'

interface TaskManagerProps {
  expanded?: boolean
}

export function TaskManager({ expanded = false }: TaskManagerProps) {
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

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.PENDING:
        return 'text-yellow-600 bg-yellow-100'
      case TaskStatus.IN_PROGRESS:
        return 'text-blue-600 bg-blue-100'
      case TaskStatus.COMPLETED:
        return 'text-green-600 bg-green-100'
      case TaskStatus.CANCELLED:
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.LOW:
        return 'text-green-600'
      case TaskPriority.MEDIUM:
        return 'text-yellow-600'
      case TaskPriority.HIGH:
        return 'text-orange-600'
      case TaskPriority.URGENT:
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  if (!currentOrganization) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Zarządzanie zadaniami
        </h3>
        <p className="text-gray-500 text-center py-8">
          Wybierz organizację, aby zobaczyć zadania
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">
          Zadania {currentOrganization.name}
        </h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleRunCeleryTest}
            disabled={testCeleryMutation.isPending}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {testCeleryMutation.isPending ? (
              <LoadingSpinner size="small" />
            ) : (
              'Test Celery'
            )}
          </button>
          <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center space-x-1">
            <Plus className="w-4 h-4" />
            <span>Nowe zadanie</span>
          </button>
        </div>
      </div>

      {/* Filter controls */}
      <div className="flex items-center space-x-4 mb-4">
        <select
          value={filter.status || ''}
          onChange={(e) => setFilter(prev => ({ ...prev, status: e.target.value as TaskStatus || undefined }))}
          className="px-3 py-1 border border-gray-300 rounded text-sm"
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
          className="px-3 py-1 border border-gray-300 rounded text-sm"
        >
          <option value="">Wszystkie priorytety</option>
          <option value={TaskPriority.LOW}>Niski</option>
          <option value={TaskPriority.MEDIUM}>Średni</option>
          <option value={TaskPriority.HIGH}>Wysoki</option>
          <option value={TaskPriority.URGENT}>Pilny</option>
        </select>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner size="medium" />
        </div>
      ) : !tasks || tasks.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">Brak zadań w tej organizacji</p>
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Utwórz pierwsze zadanie
          </button>
        </div>
      ) : (
        <div className={`grid gap-4 ${expanded ? 'grid-cols-1' : 'grid-cols-1'}`}>
          <AnimatePresence>
            {tasks.map((task) => (
              <motion.div
                key={task.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium text-gray-900">{task.title}</h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(task.status)}`}>
                        {task.status}
                      </span>
                      <span className={`text-xs font-medium ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                    </div>
                    
                    {task.description && (
                      <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                    )}
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      {task.assignee && (
                        <span>Przypisane: {task.assignee.first_name} {task.assignee.last_name}</span>
                      )}
                      {task.due_date && (
                        <span>Termin: {new Date(task.due_date).toLocaleDateString('pl-PL')}</span>
                      )}
                      {task.project && (
                        <span>Projekt: {task.project.name}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <motion.button
                      className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Edytuj
                    </motion.button>
                    <motion.button
                      className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded transition-colors"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Szczegóły
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Celery test results */}
      {testCeleryMutation.isError && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg"
        >
          <p className="text-red-600 text-sm">
            Błąd Celery: {testCeleryMutation.error?.message}
          </p>
        </motion.div>
      )}

      {testCeleryMutation.isSuccess && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg"
        >
          <p className="text-green-600 text-sm">
            Celery działa poprawnie!
          </p>
        </motion.div>
      )}
    </div>
  )
}
