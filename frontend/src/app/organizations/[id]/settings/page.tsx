'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Save, Trash2, Users, Globe, Building2, Shield, Bell, FileText, Bot } from 'lucide-react'
import { api } from '@/lib/api'
import { useOrganizationStore } from '@/stores'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Organization } from '@/types'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { StrategyPanel } from '@/components/settings/strategy-panel'
import { AIManagementPanelOrg } from '@/components/settings/ai-management-panel-org'
import { WebsiteAnalysisStatus } from '@/components/organization/website-analysis-status'

const organizationSettingsSchema = z.object({
  name: z.string().min(2, 'Nazwa musi mieć co najmniej 2 znaki'),
  description: z.string().optional(),
  website: z.string().url('Nieprawidłowy adres URL').optional().or(z.literal('')),
  industry: z.string().optional(),
  size: z.string().optional(),
})

type OrganizationSettingsForm = z.infer<typeof organizationSettingsSchema>

export default function OrganizationSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { updateOrganization, deleteOrganization } = useOrganizationStore()
  const [activeTab, setActiveTab] = useState<'general' | 'strategy' | 'ai' | 'members' | 'security' | 'notifications'>('general')
  
  const organizationId = params?.id ? parseInt(params.id as string) : null

  // Pobieranie danych organizacji
  const { data: organization, isLoading, error } = useQuery({
    queryKey: ['organization', organizationId],
    queryFn: async () => {
      const orgs = await api.organizations.getAll()
      return orgs.find(org => org.id === organizationId)
    },
    enabled: !!organizationId && organizationId > 0
  })

  // Formularz ustawień
  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset
  } = useForm<OrganizationSettingsForm>({
    resolver: zodResolver(organizationSettingsSchema),
    values: organization ? {
      name: organization.name,
      description: organization.description || '',
      website: organization.website || '',
      industry: organization.industry || '',
      size: organization.size || '',
    } : undefined
  })

  // Mutacja do aktualizacji organizacji
  const updateMutation = useMutation({
    mutationFn: async (data: OrganizationSettingsForm) => {
      if (!organization) throw new Error('Brak danych organizacji')
      return await api.organizations.update(organization.id, data)
    },
    onSuccess: (updatedOrg) => {
      updateOrganization(updatedOrg.id, updatedOrg)
      queryClient.invalidateQueries({ queryKey: ['organization', organizationId] })
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      queryClient.invalidateQueries({ queryKey: ['website-analysis', organizationId] })
      reset(updatedOrg)
      
      // Jeśli dodano/zmieniono URL strony, pokaż powiadomienie
      if (updatedOrg.website && updatedOrg.website !== organization?.website) {
        // Analiza strony została automatycznie uruchomiona w backend
        console.log('Website URL changed, analysis triggered automatically')
      }
    }
  })

  // Mutacja do usuwania organizacji
  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!organization) throw new Error('Brak danych organizacji')
      await api.organizations.delete(organization.id)
    },
    onSuccess: () => {
      if (organization) {
        deleteOrganization(organization.id)
      }
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      router.push('/')
    }
  })

  const handleSave = (data: OrganizationSettingsForm) => {
    updateMutation.mutate(data)
  }

  const handleDelete = () => {
    if (confirm('Czy na pewno chcesz usunąć tę organizację? Ta akcja jest nieodwracalna.')) {
      deleteMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (error || !organization) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Organizacja nie została znaleziona</h1>
          <p className="text-gray-600 mb-4">Sprawdź czy masz dostęp do tej organizacji</p>
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            <ArrowLeft size={16} />
            Powrót do dashboard
          </button>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'general', label: 'Ogólne', icon: Building2 },
    { id: 'strategy', label: 'Strategia komunikacji', icon: FileText },
    { id: 'ai', label: 'AI & Prompty', icon: Bot },
    { id: 'members', label: 'Członkowie', icon: Users },
    { id: 'security', label: 'Bezpieczeństwo', icon: Shield },
    { id: 'notifications', label: 'Powiadomienia', icon: Bell },
  ] as const

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft size={20} />
                Powrót
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Ustawienia: {organization.name}
                </h1>
                <p className="text-sm text-gray-600">
                  Zarządzaj ustawieniami organizacji
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar z tabami */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors
                      ${activeTab === tab.id
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                        : 'text-gray-700 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon size={18} />
                    {tab.label}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Główna zawartość */}
          <div className="flex-1">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'general' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Ustawienia ogólne</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Podstawowe informacje o organizacji
                    </p>
                  </div>

                  <form onSubmit={handleSubmit(handleSave)} className="p-6 space-y-6">
                    {/* Nazwa organizacji */}
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                        Nazwa organizacji *
                      </label>
                      <input
                        type="text"
                        id="name"
                        {...register('name')}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      {errors.name && (
                        <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                      )}
                    </div>

                    {/* Opis */}
                    <div>
                      <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                        Opis
                      </label>
                      <textarea
                        id="description"
                        rows={3}
                        {...register('description')}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Krótki opis organizacji..."
                      />
                    </div>

                    {/* Strona internetowa */}
                    <div>
                      <label htmlFor="website" className="block text-sm font-medium text-gray-700">
                        Strona internetowa
                      </label>
                      <input
                        type="url"
                        id="website"
                        {...register('website')}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="https://example.com"
                      />
                      {errors.website && (
                        <p className="mt-1 text-sm text-red-600">{errors.website.message}</p>
                      )}
                    </div>
                    
                    {/* Analiza strony internetowej */}
                    <div>
                      {organization.website ? (
                        <WebsiteAnalysisStatus 
                          organizationId={organization.id} 
                          onAnalysisComplete={() => {
                            queryClient.invalidateQueries({ queryKey: ['organization', organizationId] })
                          }}
                        />
                      ) : (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                          <div className="flex items-center gap-3">
                            <Globe className="h-5 w-5 text-amber-600" />
                            <div>
                              <p className="text-sm font-medium text-amber-900">
                                Brak adresu strony internetowej
                              </p>
                              <p className="text-xs text-amber-700">
                                Dodaj adres strony internetowej powyżej, aby móc przeprowadzić analizę
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Branża */}
                    <div>
                      <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
                        Branża
                      </label>
                      <select
                        id="industry"
                        {...register('industry')}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Wybierz branżę</option>
                        <option value="Technology">Technologia</option>
                        <option value="Healthcare">Ochrona zdrowia</option>
                        <option value="Finance">Finanse</option>
                        <option value="Education">Edukacja</option>
                        <option value="Retail">Handel detaliczny</option>
                        <option value="Manufacturing">Produkcja</option>
                        <option value="Consulting">Konsulting</option>
                        <option value="Non-profit">Organizacja non-profit</option>
                        <option value="Other">Inne</option>
                      </select>
                    </div>

                    {/* Rozmiar organizacji */}
                    <div>
                      <label htmlFor="size" className="block text-sm font-medium text-gray-700">
                        Rozmiar organizacji
                      </label>
                      <select
                        id="size"
                        {...register('size')}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Wybierz rozmiar</option>
                        <option value="startup">Startup</option>
                        <option value="small">Mała (1-10 pracowników)</option>
                        <option value="medium">Średnia (11-50 pracowników)</option>
                        <option value="large">Duża (51-200 pracowników)</option>
                        <option value="enterprise">Korporacja (200+ pracowników)</option>
                      </select>
                    </div>

                    {/* Przyciski akcji */}
                    <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                      <button
                        type="button"
                        onClick={handleDelete}
                        disabled={deleteMutation.isPending}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                      >
                        <Trash2 size={16} />
                        {deleteMutation.isPending ? 'Usuwanie...' : 'Usuń organizację'}
                      </button>

                      <button
                        type="submit"
                        disabled={!isDirty || updateMutation.isPending}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                      >
                        <Save size={16} />
                        {updateMutation.isPending ? 'Zapisywanie...' : 'Zapisz zmiany'}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {activeTab === 'strategy' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Strategia komunikacji</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Zarządzaj strategią komunikacji organizacji za pomocą analizy AI
                    </p>
                  </div>
                  <div className="p-6">
                    <StrategyPanel organizationId={organizationId!} />
                  </div>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Zarządzanie AI & Prompty</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Konfiguruj prompty AI i przypisania modeli dla tej organizacji
                    </p>
                  </div>
                  <div className="p-6">
                    <AIManagementPanelOrg organizationId={organizationId!} />
                  </div>
                </div>
              )}

              {activeTab === 'members' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Członkowie organizacji</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Zarządzaj członkami organizacji i ich uprawnieniami
                    </p>
                  </div>
                  <div className="p-6">
                    <div className="text-center py-8">
                      <Users size={48} className="mx-auto text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Funkcjonalność w przygotowaniu
                      </h3>
                      <p className="text-gray-600">
                        Zarządzanie członkami organizacji będzie dostępne wkrótce
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Ustawienia bezpieczeństwa</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Konfiguruj ustawienia bezpieczeństwa organizacji
                    </p>
                  </div>
                  <div className="p-6">
                    <div className="text-center py-8">
                      <Shield size={48} className="mx-auto text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Funkcjonalność w przygotowaniu
                      </h3>
                      <p className="text-gray-600">
                        Ustawienia bezpieczeństwa będą dostępne wkrótce
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'notifications' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Powiadomienia</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Konfiguruj preferencje powiadomień dla organizacji
                    </p>
                  </div>
                  <div className="p-6">
                    <div className="text-center py-8">
                      <Bell size={48} className="mx-auto text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Funkcjonalność w przygotowaniu
                      </h3>
                      <p className="text-gray-600">
                        Ustawienia powiadomień będą dostępne wkrótce
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
