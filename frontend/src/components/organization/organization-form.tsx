'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import { z } from 'zod'
import { api } from '@/lib/api'
import { Organization, OrganizationCreate, OrganizationUpdate } from '@/types'
import { useOrganizationStore } from '@/stores'

const organizationSchema = z.object({
  name: z.string().min(2, 'Nazwa musi mieć co najmniej 2 znaki'),
  website: z.string().url('Niepoprawny URL').optional().or(z.literal('')),
  industry: z.string().optional(),
  size: z.string().optional(),
  description: z.string().optional(),
})

type OrganizationFormData = z.infer<typeof organizationSchema>

interface OrganizationFormProps {
  organization?: Organization
  onSuccess?: () => void
}

export function OrganizationForm({ organization, onSuccess }: OrganizationFormProps) {
  const queryClient = useQueryClient()
  const { addOrganization, updateOrganization } = useOrganizationStore()
  const isEditing = Boolean(organization)
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<OrganizationFormData>({
    resolver: zodResolver(organizationSchema),
    defaultValues: {
      name: organization?.name || '',
      website: organization?.website || '',
      industry: organization?.industry || '',
      size: organization?.size || '',
      description: organization?.description || '',
    }
  })

  const mutation = useMutation({
    mutationFn: async (data: OrganizationFormData) => {
      // Usuwamy puste stringi
      const cleanData = {
        name: data.name,
        ...(data.website && { website: data.website }),
        ...(data.industry && { industry: data.industry }),
        ...(data.size && { size: data.size }),
        ...(data.description && { description: data.description }),
      }
      
      if (isEditing && organization) {
        return api.organizations.update(organization.id, cleanData as OrganizationUpdate)
      } else {
        return api.organizations.create(cleanData as OrganizationCreate)
      }
    },
    onSuccess: (updatedOrganization) => {
      if (isEditing) {
        updateOrganization(updatedOrganization.id, updatedOrganization)
      } else {
        addOrganization(updatedOrganization)
      }
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      reset()
      onSuccess?.()
    },
    onError: (error) => {
      console.error(`Błąd podczas ${isEditing ? 'edycji' : 'tworzenia'} organizacji:`, error)
    }
  })

  const onSubmit = (data: OrganizationFormData) => {
    mutation.mutate(data)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
    >
      <h3 className="text-lg font-medium text-gray-900 mb-6">
        {isEditing ? 'Edytuj organizację' : 'Dodaj nową organizację'}
      </h3>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Nazwa - wymagane */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Nazwa organizacji *
          </label>
          <input
            {...register('name')}
            type="text"
            id="name"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Wpisz nazwę organizacji"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        {/* Adres www */}
        <div>
          <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-1">
            Adres www
          </label>
          <input
            {...register('website')}
            type="url"
            id="website"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="https://example.com"
          />
          {errors.website && (
            <p className="mt-1 text-sm text-red-600">{errors.website.message}</p>
          )}
        </div>

        {/* Branża */}
        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-1">
            Branża
          </label>
          <input
            {...register('industry')}
            type="text"
            id="industry"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="np. Technologie, Marketing, Handel"
          />
          {errors.industry && (
            <p className="mt-1 text-sm text-red-600">{errors.industry.message}</p>
          )}
        </div>

        {/* Rozmiar */}
        <div>
          <label htmlFor="size" className="block text-sm font-medium text-gray-700 mb-1">
            Rozmiar organizacji
          </label>
          <select
            {...register('size')}
            id="size"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Wybierz rozmiar</option>
            <option value="startup">Startup</option>
            <option value="small">Mała (1-10 osób)</option>
            <option value="medium">Średnia (11-50 osób)</option>
            <option value="large">Duża (51-200 osób)</option>
            <option value="enterprise">Korporacja (200+ osób)</option>
          </select>
          {errors.size && (
            <p className="mt-1 text-sm text-red-600">{errors.size.message}</p>
          )}
        </div>

        {/* Opis */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Opis
          </label>
          <textarea
            {...register('description')}
            id="description"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Opcjonalny opis organizacji..."
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
        </div>

        {/* Przyciski */}
        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting 
              ? (isEditing ? 'Zapisywanie...' : 'Tworzenie...')
              : (isEditing ? 'Zapisz zmiany' : 'Dodaj organizację')
            }
          </button>
        </div>
      </form>
    </motion.div>
  )
}
