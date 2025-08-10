'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Save, Trash2, Users, Globe, Building2, Shield, Bell, NotebookPen } from 'lucide-react'
import { api } from '@/lib/api'
import { useOrganizationStore } from '@/stores'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { StrategyPanel } from '@/components/settings/strategy-panel'
import { Organization } from '@/types'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

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
  const organizationId = params?.id ? parseInt(params.id as string) : null

  // Test simple component first
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="p-6">
        <h1 className="text-2xl font-bold">Settings Test</h1>
        <p>Organization ID: {organizationId}</p>
      </div>
    </div>
  )
}
