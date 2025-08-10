'use client'

import { useParams } from 'next/navigation'
import { useOrganizationStore } from '@/stores'
import { ApiStatus } from '@/components/dashboard/api-status'

export default function OrganizationApiStatusPage() {
  const params = useParams()
  const { currentOrganization } = useOrganizationStore()
  const organizationId = params?.id as string

  // Jeśli nie ma wybranej organizacji, pokaż informację
  if (!currentOrganization) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="max-w-md w-full text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Brak wybranej organizacji
          </h1>
          <p className="text-gray-600">
            Wybierz organizację z menu nawigacji, aby uzyskać dostęp do statusu API.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Status API dla Organizacji: {currentOrganization.name}
          </h1>
          <p className="text-gray-600 mt-2">
            ID organizacji: {organizationId}
          </p>
        </div>
        
        <ApiStatus />
      </div>
    </div>
  )
} 