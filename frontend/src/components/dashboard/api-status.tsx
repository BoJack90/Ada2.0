'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, AlertCircle, Activity, Database, Zap } from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

interface StatusCardProps {
  title: string
  status: 'healthy' | 'unhealthy' | 'loading'
  message?: string
  icon: React.ElementType
  index: number
}

function StatusCard({ title, status, message, icon: Icon, index }: StatusCardProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-6 h-6 text-emerald-500" />
      case 'unhealthy':
        return <XCircle className="w-6 h-6 text-red-500" />
      case 'loading':
        return <LoadingSpinner size="small" />
      default:
        return <AlertCircle className="w-6 h-6 text-yellow-500" />
    }
  }

  const getStatusStyles = () => {
    switch (status) {
      case 'healthy':
        return {
          bg: 'bg-gradient-to-br from-emerald-50 to-teal-50',
          border: 'border-emerald-200',
          iconBg: 'bg-emerald-500',
          dot: 'bg-emerald-400'
        }
      case 'unhealthy':
        return {
          bg: 'bg-gradient-to-br from-red-50 to-pink-50',
          border: 'border-red-200',
          iconBg: 'bg-red-500',
          dot: 'bg-red-400'
        }
      case 'loading':
        return {
          bg: 'bg-gradient-to-br from-gray-50 to-slate-50',
          border: 'border-gray-200',
          iconBg: 'bg-gray-500',
          dot: 'bg-gray-400'
        }
      default:
        return {
          bg: 'bg-gradient-to-br from-yellow-50 to-orange-50',
          border: 'border-yellow-200',
          iconBg: 'bg-yellow-500',
          dot: 'bg-yellow-400'
        }
    }
  }

  const styles = getStatusStyles()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      whileHover={{ scale: 1.02, y: -2 }}
      className={`p-6 rounded-2xl border ${styles.border} ${styles.bg} shadow-lg hover:shadow-xl transition-all duration-300`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-3 ${styles.iconBg} text-white rounded-xl`}>
            <Icon className="w-6 h-6" />
          </div>
          <h3 className="font-semibold text-gray-900 text-lg">{title}</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${styles.dot} animate-pulse`}></div>
          {getStatusIcon()}
        </div>
      </div>
      {message && (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-sm text-gray-600 bg-white/50 p-3 rounded-lg"
        >
          {message}
        </motion.p>
      )}
    </motion.div>
  )
}

export function ApiStatus() {
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.health.general(),
    refetchInterval: 30000, // Sprawdź co 30 sekund
  })

  const { data: dbData, isLoading: dbLoading } = useQuery({
    queryKey: ['health-db'],
    queryFn: () => api.health.database(),
    refetchInterval: 30000,
  })

  const { data: redisData, isLoading: redisLoading } = useQuery({
    queryKey: ['health-redis'],
    queryFn: () => api.health.redis(),
    refetchInterval: 30000,
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 rounded-2xl p-8 text-white shadow-xl">
          <div className="flex items-center space-x-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="p-3 bg-white/20 rounded-xl backdrop-blur-sm"
            >
              <Activity className="h-8 w-8" />
            </motion.div>
            <div>
              <h1 className="text-3xl font-bold">Status API</h1>
              <p className="text-blue-100 mt-2">Monitorowanie zdrowia systemu i połączeń</p>
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <StatusCard
          title="Aplikacja"
          status={healthLoading ? 'loading' : (healthData?.data?.status === 'healthy' ? 'healthy' : 'unhealthy')}
          message={healthData?.data?.message}
          icon={Activity}
          index={0}
        />
        <StatusCard
          title="Baza danych"
          status={dbLoading ? 'loading' : (dbData?.data?.status === 'healthy' ? 'healthy' : 'unhealthy')}
          message={dbData?.data?.message}
          icon={Database}
          index={1}
        />
        <StatusCard
          title="Redis"
          status={redisLoading ? 'loading' : (redisData?.data?.status === 'healthy' ? 'healthy' : 'unhealthy')}
          message={redisData?.data?.message}
          icon={Zap}
          index={2}
        />
      </motion.div>
    </div>
  )
}
