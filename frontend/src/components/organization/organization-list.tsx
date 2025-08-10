'use client'

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Plus, Building2, Globe, Edit, Settings } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { useOrganizationStore } from '@/stores'
import { OrganizationModal } from './organization-modal'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Organization } from '@/types'

export function OrganizationList() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingOrganization, setEditingOrganization] = useState<Organization | null>(null)
  const { organizations, setOrganizations } = useOrganizationStore()
  const router = useRouter()

  console.log('[OrganizationList] Component rendered')
  console.log('[OrganizationList] Organizations from store:', organizations)

  const { data: organizationsData, isLoading, error } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      console.log('[OrganizationList] Fetching organizations...')
      const response = await api.organizations.getAll()
      console.log('[OrganizationList] Organizations response:', response)
      return response
    }
  })

  // Synchronizacja danych ze store
  React.useEffect(() => {
    console.log('[OrganizationList] organizationsData changed:', organizationsData)
    if (organizationsData) {
      setOrganizations(organizationsData)
    }
  }, [organizationsData, setOrganizations])

  console.log('[OrganizationList] isLoading:', isLoading)
  console.log('[OrganizationList] error:', error)
  console.log('[OrganizationList] organizationsData:', organizationsData)

  const handleAddOrganization = () => {
    setEditingOrganization(null)
    setIsModalOpen(true)
  }

  const handleEditOrganization = (organization: Organization) => {
    setEditingOrganization(organization)
    setIsModalOpen(true)
  }

  const handleOrganizationSettings = (organization: Organization) => {
    router.push(`/organizations/${organization.id}/settings`)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingOrganization(null)
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner size="medium" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center py-8">
          <p className="text-red-600">Błąd podczas ładowania organizacji</p>
          <p className="text-sm text-gray-500 mt-2">
            {error instanceof Error ? error.message : 'Wystąpił nieznany błąd'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header z przyciskiem */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Organizacje</h2>
            <p className="text-sm text-gray-600 mt-1">
              Zarządzaj swoimi organizacjami
            </p>
          </div>
          <button
            onClick={handleAddOrganization}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <Plus size={20} />
            Dodaj organizację
          </button>
        </div>
      </div>

      {/* Lista organizacji */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {organizations.length === 0 ? (
          <div className="p-8 text-center">
            <Building2 size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Brak organizacji
            </h3>
            <p className="text-gray-600 mb-4">
              Dodaj swoją pierwszą organizację, aby rozpocząć pracę
            </p>
            <button
              onClick={handleAddOrganization}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <Plus size={20} />
              Dodaj organizację
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {organizations.map((org, index) => (
              <motion.div
                key={org.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {org.name}
                    </h3>
                    
                    {org.description && (
                      <p className="text-gray-600 mb-3">
                        {org.description}
                      </p>
                    )}
                    
                    <div className="flex flex-wrap gap-3 text-sm text-gray-500">
                      {org.website && (
                        <a
                          href={org.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 hover:text-blue-600 transition-colors"
                        >
                          <Globe size={16} />
                          Strona www
                        </a>
                      )}
                      
                      {org.industry && (
                        <span className="flex items-center gap-1">
                          <Building2 size={16} />
                          {org.industry}
                        </span>
                      )}
                      
                      {org.size && (
                        <span className="flex items-center gap-1">
                          👥 {org.size}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => handleEditOrganization(org)}
                      className="flex items-center gap-1 px-2 py-1 text-xs text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
                      title="Edytuj organizację"
                    >
                      <Edit size={14} />
                      Edytuj
                    </button>
                    <button
                      onClick={() => handleOrganizationSettings(org)}
                      className="flex items-center gap-1 px-2 py-1 text-xs text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                      title="Ustawienia organizacji"
                    >
                      <Settings size={14} />
                      Ustawienia
                    </button>
                    <span className="text-xs text-gray-500">
                      {new Date(org.created_at).toLocaleDateString('pl-PL')}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      <OrganizationModal 
        isOpen={isModalOpen} 
        organization={editingOrganization || undefined}
        onClose={handleCloseModal}
      />
    </div>
  )
}
