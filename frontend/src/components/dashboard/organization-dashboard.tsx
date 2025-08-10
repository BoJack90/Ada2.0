'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useOrganizationStore } from '@/stores'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { DashboardStats } from '@/types'
import { useToast } from '@/hooks/use-toast'
import { 
  Building2, 
  Users, 
  Target, 
  CheckCircle, 
  Clock, 
  AlertTriangle,
  BarChart3,
  Plus,
  UserPlus,
  FolderPlus,
  Megaphone
} from 'lucide-react'

export function OrganizationDashboard() {
  const { currentOrganization } = useOrganizationStore()
  const toast = useToast()

  const { data: stats, isLoading } = useQuery({
    queryKey: ['organization-dashboard', currentOrganization?.id],
    queryFn: () => currentOrganization ? api.organizations.dashboard(currentOrganization.id) : Promise.resolve(null),
    enabled: !!currentOrganization,
  })

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
            <Building2 className="h-8 w-8" />
          </motion.div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Dashboard organizacji
          </h3>
          <p className="text-gray-500">
            Wybierz organizację, aby zobaczyć statystyki i metryki
          </p>
        </div>
      </motion.div>
    )
  }

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8"
      >
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="medium" />
        </div>
      </motion.div>
    )
  }

  if (!stats) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8"
      >
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-gray-400 to-gray-600 rounded-2xl text-white mb-4"
          >
            <BarChart3 className="h-8 w-8" />
          </motion.div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Dashboard - {currentOrganization.name}
          </h3>
          <p className="text-gray-500">
            Brak danych do wyświetlenia
          </p>
        </div>
      </motion.div>
    )
  }

  const statCards = [
    {
      title: 'Zadania ogółem',
      value: stats.total_tasks,
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100',
      icon: BarChart3,
      iconColor: 'text-blue-600'
    },
    {
      title: 'Oczekujące',
      value: stats.pending_tasks,
      gradient: 'from-yellow-500 to-orange-600',
      bgGradient: 'from-yellow-50 to-orange-100',
      icon: Clock,
      iconColor: 'text-yellow-600'
    },
    {
      title: 'W trakcie',
      value: stats.in_progress_tasks,
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100',
      icon: Target,
      iconColor: 'text-purple-600'
    },
    {
      title: 'Zakończone',
      value: stats.completed_tasks,
      gradient: 'from-emerald-500 to-emerald-600',
      bgGradient: 'from-emerald-50 to-emerald-100',
      icon: CheckCircle,
      iconColor: 'text-emerald-600'
    },
    {
      title: 'Przeterminowane',
      value: stats.overdue_tasks,
      gradient: 'from-red-500 to-red-600',
      bgGradient: 'from-red-50 to-red-100',
      icon: AlertTriangle,
      iconColor: 'text-red-600'
    },
    {
      title: 'Projekty',
      value: stats.total_projects,
      gradient: 'from-indigo-500 to-indigo-600',
      bgGradient: 'from-indigo-50 to-indigo-100',
      icon: FolderPlus,
      iconColor: 'text-indigo-600'
    },
    {
      title: 'Kampanie',
      value: stats.active_campaigns,
      gradient: 'from-pink-500 to-pink-600',
      bgGradient: 'from-pink-50 to-pink-100',
      icon: Megaphone,
      iconColor: 'text-pink-600'
    },
    {
      title: 'Członkowie',
      value: stats.organization_members,
      gradient: 'from-teal-500 to-teal-600',
      bgGradient: 'from-teal-50 to-teal-100',
      icon: Users,
      iconColor: 'text-teal-600'
    }
  ]

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-8"
    >
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 rounded-2xl p-8 text-white shadow-xl"
      >
        <div className="flex items-center space-x-4">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="p-3 bg-white/20 rounded-xl backdrop-blur-sm"
          >
            <Building2 className="h-8 w-8" />
          </motion.div>
          <div>
            <h1 className="text-3xl font-bold">Dashboard - {currentOrganization.name}</h1>
            <p className="text-blue-100 mt-1">Przegląd aktywności i kluczowych metryk organizacji</p>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-6"
      >
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.3 + index * 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.05, y: -5 }}
            className={`bg-gradient-to-br ${stat.bgGradient} rounded-2xl p-6 border border-white shadow-lg hover:shadow-xl transition-all duration-300`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 bg-white rounded-xl ${stat.iconColor} shadow-sm`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${stat.gradient}`}></div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {stat.value}
            </div>
            <div className="text-sm font-medium text-gray-700">
              {stat.title}
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
      >
        <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white">
          <div className="flex items-center space-x-3">
            <Plus className="h-6 w-6" />
            <div>
              <h2 className="text-xl font-semibold">Szybkie akcje</h2>
              <p className="text-emerald-100">Najczęściej używane funkcje organizacji</p>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.button 
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => toast.info('Funkcja tworzenia zadań będzie dostępna wkrótce')}
              className="p-4 text-left bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-xl transition-all duration-300 border border-blue-100 group"
            >
              <div className="flex items-center space-x-3 mb-2">
                <Plus className="h-5 w-5 text-blue-600 group-hover:scale-110 transition-transform" />
                <div className="font-semibold text-blue-900">Nowe zadanie</div>
              </div>
              <div className="text-sm text-blue-600">Utwórz nowe zadanie dla zespołu</div>
            </motion.button>
            
            <motion.button 
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => toast.info('Funkcja tworzenia projektów będzie dostępna wkrótce')}
              className="p-4 text-left bg-gradient-to-br from-emerald-50 to-teal-50 hover:from-emerald-100 hover:to-teal-100 rounded-xl transition-all duration-300 border border-emerald-100 group"
            >
              <div className="flex items-center space-x-3 mb-2">
                <FolderPlus className="h-5 w-5 text-emerald-600 group-hover:scale-110 transition-transform" />
                <div className="font-semibold text-emerald-900">Nowy projekt</div>
              </div>
              <div className="text-sm text-emerald-600">Rozpocznij nowy projekt</div>
            </motion.button>
            
            <motion.button 
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => toast.info('Funkcja tworzenia kampanii będzie dostępna wkrótce')}
              className="p-4 text-left bg-gradient-to-br from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 rounded-xl transition-all duration-300 border border-purple-100 group"
            >
              <div className="flex items-center space-x-3 mb-2">
                <Megaphone className="h-5 w-5 text-purple-600 group-hover:scale-110 transition-transform" />
                <div className="font-semibold text-purple-900">Nowa kampania</div>
              </div>
              <div className="text-sm text-purple-600">Stwórz kampanię marketingową</div>
            </motion.button>
            
            <motion.button 
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => toast.info('Funkcja zapraszania członków będzie dostępna wkrótce')}
              className="p-4 text-left bg-gradient-to-br from-gray-50 to-slate-50 hover:from-gray-100 hover:to-slate-100 rounded-xl transition-all duration-300 border border-gray-100 group"
            >
              <div className="flex items-center space-x-3 mb-2">
                <UserPlus className="h-5 w-5 text-gray-600 group-hover:scale-110 transition-transform" />
                <div className="font-semibold text-gray-900">Zaproś członka</div>
              </div>
              <div className="text-sm text-gray-600">Dodaj nową osobę do zespołu</div>
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
