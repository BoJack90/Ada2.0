'use client'

import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { TrendingUp, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ContentPerformance } from '@/components/analytics/content-performance'
import { useRouter } from 'next/navigation'

export default function AnalyticsPage() {
  const params = useParams()
  const router = useRouter()
  const organizationId = params?.id ? parseInt(params.id as string) : null

  if (!organizationId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Invalid organization ID</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center gap-4 mb-6">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Powrót
            </Button>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Analityka Treści
                </h1>
                <p className="text-gray-500">
                  Monitoruj wydajność generowania treści
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Analytics Content */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <ContentPerformance organizationId={organizationId} />
        </motion.div>
      </div>
    </div>
  )
}