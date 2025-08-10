'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Settings, Bot, Database, Shield, Bell, Globe } from 'lucide-react'
import { AIManagementPanelV2 } from '@/components/settings/ai-management-panel-v2'

export default function SystemSettingsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'ai-management' | 'system' | 'security' | 'notifications'>('ai-management')

  const tabs = [
    { id: 'ai-management', label: 'AI & Prompts', icon: Bot },
    { id: 'system', label: 'System', icon: Settings },
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
                onClick={() => router.push('/dashboard')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft size={20} />
                Powrót
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Ustawienia systemowe
                </h1>
                <p className="text-sm text-gray-600">
                  Zarządzaj globalnymi ustawieniami systemu
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-600">Globalne</span>
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
              {activeTab === 'ai-management' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Zarządzanie AI & Prompts</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Konfiguruj prompty AI i przypisania modeli Gemini dla wszystkich funkcji systemu
                    </p>
                  </div>
                  <div className="p-6">
                    <AIManagementPanelV2 />
                  </div>
                </div>
              )}

              {activeTab === 'system' && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Ustawienia systemowe</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Podstawowe ustawienia systemu
                    </p>
                  </div>
                  <div className="p-6">
                    <div className="text-center py-8">
                      <Settings size={48} className="mx-auto text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Funkcjonalność w przygotowaniu
                      </h3>
                      <p className="text-gray-600">
                        Ustawienia systemowe będą dostępne wkrótce
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
                      Konfiguruj globalne ustawienia bezpieczeństwa
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
                    <h2 className="text-lg font-medium text-gray-900">Powiadomienia systemowe</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Zarządzaj powiadomieniami dla całego systemu
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