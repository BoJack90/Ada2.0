'use client'

import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { useOrganizationStore } from '@/stores'
import { ContentPlansManager } from '@/components/dashboard/content-plans-manager'
import { Building2, FileText } from 'lucide-react'

export default function OrganizationContentPlansPage() {
  const params = useParams()
  const { currentOrganization } = useOrganizationStore()
  const organizationId = params?.id ? parseInt(params.id as string) : null

  console.log('OrganizationContentPlansPage - params.id:', params?.id, 'currentOrganization:', currentOrganization)

  // Jeśli nie ma wybranej organizacji, pokaż informację
  if (!currentOrganization || !organizationId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center p-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md w-full text-center"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="w-20 h-20 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-6"
          >
            <Building2 size={32} className="text-white" />
          </motion.div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-2">
            Brak wybranej organizacji
          </h1>
          <p className="text-gray-600">
            Wybierz organizację z menu nawigacji, aby uzyskać dostęp do planów treści.
          </p>
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
                className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center"
              >
                <FileText size={24} className="text-white" />
              </motion.div>
              <div>
                <motion.h1 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent"
                >
                  Plany Treści
                </motion.h1>
                <motion.p 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="text-gray-600 font-medium"
                >
                  {currentOrganization?.name || 'Organization'}
                </motion.p>
              </div>
            </div>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 0.3 }}
              className="flex items-center gap-2 text-sm text-gray-500 bg-gray-50 px-3 py-2 rounded-lg"
            >
              <Building2 size={14} />
              <span>ID organizacji: {organizationId}</span>
            </motion.div>
          </div>
        </motion.div>
        
        {/* Content Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <ContentPlansManager 
            organizationId={organizationId}
            organizationName={currentOrganization.name}
          />
        </motion.div>
      </div>
    </div>
  )
} 