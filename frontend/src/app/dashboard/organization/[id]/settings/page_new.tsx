'use client'

import React from 'react'
import { useParams } from 'next/navigation'

export default function OrganizationSettingsPage() {
  const params = useParams()
  const organizationId = params?.id ? parseInt(params.id as string) : null

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="p-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p>Organization ID: {organizationId}</p>
        <p className="mt-4 text-gray-600">Settings functionality will be restored soon.</p>
      </div>
    </div>
  )
}
