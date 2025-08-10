'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useOrganizationStore } from '@/stores'
import { api } from '@/lib/api'
import { ContentDraft } from '@/types'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { 
  FileEdit, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  ArrowRight,
  Info,
  Calendar
} from 'lucide-react'

export default function ContentWorkspacePage() {
  const params = useParams()
  const organizationId = params?.id ? parseInt(params.id as string) : 0
  const { currentOrganization } = useOrganizationStore()

  // Lista wszystkich content drafts dla organizacji - na razie bez API
  const { data: contentDrafts, isLoading: isLoadingDrafts, error } = useQuery({
    queryKey: ['contentDrafts', organizationId],
    queryFn: async () => {
      // Pokazujemy przykładowe dane do demonstracji interfejsu
      return [
        {
          id: 3,
          suggested_topic_id: 104,
          status: 'pending_approval' as const,
          created_by_task_id: undefined,
          is_active: true,
          created_at: '2025-07-14T16:14:13.988275',
          updated_at: '2025-07-14T16:14:13.988275',
          suggested_topic: {
            id: 104,
            content_plan_id: 20,
            title: 'Czy Twój obiekt jest bezpieczny? 🤔',
            description: 'Post o znaczeniu systemów bezpieczeństwa w obiektach komercyjnych',
            category: 'security',
            status: 'approved',
            is_active: true,
            created_at: '2025-07-14T16:00:00.000000'
          }
        },
        {
          id: 4,
          suggested_topic_id: 105,
          status: 'pending_approval' as const,
          created_by_task_id: undefined,
          is_active: true,
          created_at: '2025-07-14T16:14:38.009328',
          updated_at: '2025-07-14T16:14:38.009328',
          suggested_topic: {
            id: 105,
            content_plan_id: 20,
            title: 'SSP, DSO/PAS, SSWiN - co to takiego? 🤔',
            description: 'Wyjaśnienie skrótów i systemów bezpieczeństwa',
            category: 'education',
            status: 'approved',
            is_active: true,
            created_at: '2025-07-14T16:00:00.000000'
          }
        }
      ] as ContentDraft[]
    },
    enabled: !!organizationId && organizationId > 0,
  })

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'pending_approval': return <Clock size={16} className="text-yellow-500" />
      case 'approved': return <CheckCircle size={16} className="text-green-500" />
      case 'rejected': return <XCircle size={16} className="text-red-500" />
      default: return <AlertTriangle size={16} className="text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'pending_approval': return 'bg-gradient-to-r from-yellow-50 to-orange-50 text-yellow-700 border-yellow-200'
      case 'approved': return 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 border-green-200'
      case 'rejected': return 'bg-gradient-to-r from-red-50 to-pink-50 text-red-700 border-red-200'
      default: return 'bg-gradient-to-r from-gray-50 to-slate-50 text-gray-700 border-gray-200'
    }
  }

  const getStatusText = (status: string) => {
    switch(status) {
      case 'pending_approval': return 'Oczekuje zatwierdzenia'
      case 'approved': return 'Zatwierdzony'
      case 'rejected': return 'Odrzucony'
      default: return status
    }
  }

  if (isLoadingDrafts) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <LoadingSpinner />
          <p className="mt-4 text-gray-600 font-medium">Ładowanie pulpitu treści...</p>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full"
        >
          <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-2xl p-6 text-center">
            <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-500 rounded-xl flex items-center justify-center mx-auto mb-4">
              <XCircle size={24} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-red-900 mb-2">Błąd ładowania</h3>
            <p className="text-red-700">Nie udało się załadować pulpitu roboczego treści.</p>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-white/20 shadow-xl">
            <div className="flex items-center gap-4 mb-4">
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center"
              >
                <FileEdit size={24} className="text-white" />
              </motion.div>
              <div>
                <motion.h1 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent"
                >
                  Pulpit Roboczy Treści
                </motion.h1>
                <motion.p 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="text-gray-600 font-medium"
                >
                  Zarządzaj i akceptuj warianty treści dla {currentOrganization?.name}
                </motion.p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Lista Content Drafts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-white/20 shadow-xl overflow-hidden">
            <div className="px-6 py-4 bg-gradient-to-r from-orange-50 to-red-50 border-b border-white/20">
              <h2 className="text-lg font-semibold text-gray-900">Drafts oczekujące na zatwierdzenie</h2>
            </div>
            
            <div className="p-6">
              {contentDrafts && contentDrafts.length > 0 ? (
                <div className="space-y-4">
                  {contentDrafts.map((draft, index) => (
                    <motion.div 
                      key={draft.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1, duration: 0.4 }}
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-200"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 mb-2 text-lg">
                            {draft.suggested_topic?.title || `Draft #${draft.id}`}
                          </h3>
                          <p className="text-gray-600 mb-3 leading-relaxed">
                            {draft.suggested_topic?.description}
                          </p>
                        </div>
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          className={`ml-4 px-3 py-1.5 rounded-lg text-xs font-medium border ${getStatusColor(draft.status)} flex items-center gap-2`}
                        >
                          {getStatusIcon(draft.status)}
                          {getStatusText(draft.status)}
                        </motion.div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <div className="flex items-center gap-1">
                            <Calendar size={14} />
                            <span>Utworzono: {new Date(draft.created_at).toLocaleDateString('pl-PL')}</span>
                          </div>
                        </div>
                        
                        <motion.a 
                          href={`/dashboard/drafts/${draft.id}`}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                        >
                          Otwórz w Workspace
                          <ArrowRight size={16} />
                        </motion.a>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.7, duration: 0.4 }}
                  className="text-center py-12"
                >
                  <div className="w-16 h-16 bg-gradient-to-r from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <FileEdit size={32} className="text-gray-400" />
                  </div>
                  <p className="text-gray-500 mb-2 font-medium">Brak drafts oczekujących na zatwierdzenie</p>
                  <p className="text-sm text-gray-400">
                    Drafts pojawią się tutaj gdy zostaną wygenerowane przez system
                  </p>
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Instrukcje dla użytkownika */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
          className="mt-8"
        >
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <Info size={20} className="text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-blue-900 mb-3">Jak używać Pulpitu Roboczego Treści</h3>
                <ul className="text-blue-800 space-y-2 leading-relaxed">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    Po wygenerowaniu treści w Content Plans, drafts pojawią się w tej sekcji
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    Kliknij "Otwórz w Workspace" aby przejść do szczegółowego widoku wariantów
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    W widoku szczegółowym możesz akceptować, odrzucać lub wymagać rewizji poszczególnych wariantów
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    Zaakceptowane warianty będą gotowe do publikacji w harmonogramie
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
