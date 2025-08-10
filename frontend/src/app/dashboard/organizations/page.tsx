'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Plus, Building2, Globe, Users, ExternalLink, Edit, Settings } from 'lucide-react'
import { api } from '@/lib/api'
import { useOrganizationStore } from '@/stores'
import { useDashboard } from '@/contexts/dashboard-context'
import { OrganizationModal } from '@/components/organization/organization-modal'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Organization } from '@/types'

export default function OrganizationsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingOrganization, setEditingOrganization] = useState<Organization | null>(null)
  const { organizations, setOrganizations, setCurrentOrganization } = useOrganizationStore()
  const { setActiveView } = useDashboard()
  const router = useRouter()

  const { data: organizationsData, isLoading, error, refetch } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      const response = await api.organizations.getAll()
      return response
    },
    initialData: organizations,
  })

  // Synchronizacja danych ze store
  useEffect(() => {
    if (organizationsData) {
      setOrganizations(organizationsData)
    }
  }, [organizationsData, setOrganizations])

  const handleAddOrganization = () => {
    setEditingOrganization(null)
    setIsModalOpen(true)
  }

  const handleManageOrganization = (organization: Organization) => {
    // Ustawiamy wybraną organizację jako aktywną
    setCurrentOrganization(organization)
    // Ustawiamy widok na content-plans dla lepszego UX
    setActiveView('content-plans')
    // Przekierowujemy na główny dashboard (główna strona)
    router.push('/')
  }

  const handleEditOrganization = (organization: Organization) => {
    setEditingOrganization(organization)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingOrganization(null)
    // Odświeżamy listę po zamknięciu modala
    refetch()
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">Błąd podczas ładowania organizacji</p>
          <p className="text-sm text-gray-500 mt-2">
            {error instanceof Error ? error.message : 'Wystąpił nieznany błąd'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Organizacje</h1>
            <p className="text-gray-600 mt-1">
              Zarządzaj swoimi organizacjami i wybierz aktywną organizację
            </p>
          </div>
          <button
            onClick={handleAddOrganization}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            Dodaj organizację
          </button>
        </div>
      </div>

      {/* Tabela organizacji */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {organizations.length === 0 ? (
          <div className="p-12 text-center">
            <Building2 size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Brak organizacji
            </h3>
            <p className="text-gray-600 mb-6">
              Dodaj swoją pierwszą organizację, aby rozpocząć pracę
            </p>
            <button
              onClick={handleAddOrganization}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus size={20} />
              Dodaj organizację
            </button>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Organizacja
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Branża
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rozmiar
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Strona WWW
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data utworzenia
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Akcje
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {organizations.map((org, index) => (
                <motion.tr
                  key={org.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="hover:bg-gray-50"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <Building2 className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {org.name}
                        </div>
                        {org.description && (
                          <div className="text-sm text-gray-500 truncate max-w-xs">
                            {org.description}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {org.industry || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-sm text-gray-900">
                      <Users className="h-4 w-4 mr-1" />
                      {org.size || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {org.website ? (
                      <a
                        href={org.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                      >
                        <Globe className="h-4 w-4 mr-1" />
                        Odwiedź
                        <ExternalLink className="h-3 w-3 ml-1" />
                      </a>
                    ) : (
                      <span className="text-sm text-gray-500">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(org.created_at).toLocaleDateString('pl-PL')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleManageOrganization(org)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                      >
                        Zarządzaj
                      </button>
                      <button
                        onClick={() => handleEditOrganization(org)}
                        className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                      >
                        Edytuj
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      <OrganizationModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        organization={editingOrganization || undefined}
      />
    </div>
  )
} 