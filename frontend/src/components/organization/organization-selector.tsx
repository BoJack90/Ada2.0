'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useOrganizationStore, useAuthStore } from '@/stores'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Organization } from '@/types'

interface OrganizationSelectorProps {
  onOrganizationSelected?: (org: Organization) => void
}

export function OrganizationSelector({ onOrganizationSelected }: OrganizationSelectorProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newOrgData, setNewOrgData] = useState({
    name: '',
    slug: '',
    description: ''
  })
  const [error, setError] = useState('')

  const { currentOrganization, organizations, setCurrentOrganization, setOrganizations, addOrganization } = useOrganizationStore()
  const { user } = useAuthStore()

  useEffect(() => {
    loadOrganizations()
  }, [])

  const loadOrganizations = async () => {
    try {
      const orgs = await api.users.organizations()
      setOrganizations(orgs)
      
      // Set first organization as current if none selected
      if (!currentOrganization && orgs.length > 0) {
        setCurrentOrganization(orgs[0])
        onOrganizationSelected?.(orgs[0])
      }
    } catch (err) {
      console.error('Failed to load organizations:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleOrganizationSelect = (org: Organization) => {
    setCurrentOrganization(org)
    onOrganizationSelected?.(org)
  }

  const handleCreateOrganization = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const newOrg = await api.organizations.create({
        name: newOrgData.name,
        description: newOrgData.description
      })
      
      addOrganization(newOrg)
      setCurrentOrganization(newOrg)
      onOrganizationSelected?.(newOrg)
      setShowCreateForm(false)
      setNewOrgData({ name: '', slug: '', description: '' })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Błąd podczas tworzenia organizacji')
    }
  }

  const generateSlug = (name: string) => {
    return name.toLowerCase()
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
  }

  const handleNameChange = (name: string) => {
    setNewOrgData(prev => ({
      ...prev,
      name,
      slug: generateSlug(name)
    }))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="medium" />
      </div>
    )
  }

  if (organizations.length === 0 && !showCreateForm) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center p-8"
      >
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Witaj w Ada 2.0!
        </h3>
        <p className="text-gray-600 mb-6">
          Aby rozpocząć, utwórz swoją pierwszą organizację.
        </p>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Utwórz organizację
        </button>
      </motion.div>
    )
  }

  return (
    <div className="space-y-4">
      {!showCreateForm ? (
        <>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Wybierz organizację
            </h3>
            <button
              onClick={() => setShowCreateForm(true)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              + Nowa organizacja
            </button>
          </div>

          <div className="grid gap-3">
            {organizations.map((org) => (
              <motion.button
                key={org.id}
                onClick={() => handleOrganizationSelect(org)}
                className={`p-4 rounded-lg border text-left transition-all ${
                  currentOrganization?.id === org.id
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="font-medium text-gray-900">{org.name}</div>
                {org.description && (
                  <div className="text-sm text-gray-600 mt-1">{org.description}</div>
                )}
                <div className="text-xs text-gray-500 mt-2">
                  Właściciel: {org.owner_id === user?.id ? 'Ty' : 'Inny'}
                </div>
              </motion.button>
            ))}
          </div>
        </>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Nowa organizacja
            </h3>
            <button
              onClick={() => setShowCreateForm(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleCreateOrganization} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nazwa organizacji
              </label>
              <input
                type="text"
                value={newOrgData.name}
                onChange={(e) => handleNameChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="np. Moja Firma"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Identyfikator (slug)
              </label>
              <input
                type="text"
                value={newOrgData.slug}
                onChange={(e) => setNewOrgData(prev => ({ ...prev, slug: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="moja-firma"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Używany w adresach URL, tylko małe litery, cyfry i myślniki
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Opis (opcjonalny)
              </label>
              <textarea
                value={newOrgData.description}
                onChange={(e) => setNewOrgData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                placeholder="Krótki opis organizacji..."
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm">{error}</div>
            )}

            <div className="flex space-x-3">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                Utwórz
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
              >
                Anuluj
              </button>
            </div>
          </form>
        </motion.div>
      )}
    </div>
  )
}
