'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useOrganizationStore, useAuthStore } from '@/stores'
import { Organization } from '@/types'

export function OrganizationSwitcher() {
  const [isOpen, setIsOpen] = useState(false)
  const { currentOrganization, organizations, setCurrentOrganization } = useOrganizationStore()
  const { user } = useAuthStore()

  const handleOrganizationSelect = (org: Organization) => {
    setCurrentOrganization(org)
    setIsOpen(false)
  }

  if (!currentOrganization) {
    return null
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-white font-medium text-sm">
            {currentOrganization.name.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="text-left">
          <div className="font-medium text-gray-900 text-sm">
            {currentOrganization.name}
          </div>
          <div className="text-xs text-gray-500">
            {currentOrganization.owner_id === user?.id ? 'Właściciel' : 'Członek'}
          </div>
        </div>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
          >
            <div className="p-2">
              <div className="px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                Twoje organizacje
              </div>
              <div className="space-y-1">
                {organizations.map((org) => (
                  <button
                    key={org.id}
                    onClick={() => handleOrganizationSelect(org)}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      currentOrganization.id === org.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-medium text-xs">
                          {org.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-sm">{org.name}</div>
                        <div className="text-xs text-gray-500">
                          {org.owner_id === user?.id ? 'Właściciel' : 'Członek'}
                        </div>
                      </div>
                      {currentOrganization.id === org.id && (
                        <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}
