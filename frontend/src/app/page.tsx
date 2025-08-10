'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { DashboardContent } from '@/components/layout/dashboard-content'

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    const initializeApp = async () => {
      // Check if we're on the client side
      if (typeof window === 'undefined') {
        return
      }
      
      const token = localStorage.getItem('auth_token')
      console.log('Initialization - token found:', !!token)
      
      if (!token) {
        console.log('No token found, redirecting to login')
        router.push('/auth/login')
        return
      }

      setIsLoading(false)
    }

    initializeApp()
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return <DashboardContent />
}
