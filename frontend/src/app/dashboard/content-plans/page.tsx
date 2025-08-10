'use client'

import { useRouter } from 'next/navigation'
import { Building2, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

import { useOrganizationStore } from '@/stores'
import { ContentPlansManager } from '@/components/dashboard/content-plans-manager'
import { Card } from '@/components/ui/cards'

export default function ContentPlansPage() {
  const router = useRouter()
  const { currentOrganization } = useOrganizationStore()

  // Jeśli nie ma wybranej organizacji, pokaż empty state
  if (!currentOrganization) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md w-full"
        >
          <Card className="p-8 text-center">
            <div className="mb-6">
              <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Nie wybrano organizacji
              </h2>
              <p className="text-gray-600">
                Aby rozpocząć planowanie treści, musisz najpierw wybrać organizację, 
                dla której chcesz tworzyć content plans.
              </p>
            </div>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => router.push('/dashboard/organizations')}
              className="flex items-center gap-2 w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Building2 className="w-5 h-5" />
              Wybierz organizację
              <ArrowRight className="w-5 h-5 ml-auto" />
            </motion.button>
          </Card>
        </motion.div>
      </div>
    )
  }

  // Jeśli organizacja jest wybrana, pokaż Content Plans Manager
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <ContentPlansManager 
          organizationId={currentOrganization.id}
          organizationName={currentOrganization.name}
        />
      </div>
    </div>
  )
} 