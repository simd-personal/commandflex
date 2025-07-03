'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import LoginForm from '@/components/auth/LoginForm'
import Dashboard from '@/components/dashboard/Dashboard'

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)
  const { user, isAuthenticated } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('token')
    if (token) {
      // Validate token and set user
      // This would typically involve an API call to verify the token
      setIsLoading(false)
    } else {
      setIsLoading(false)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-primary-bg flex items-center justify-center">
        <div className="text-center">
          <div className="text-accent text-2xl font-mono mb-4">
            CommandFlex
          </div>
          <div className="text-text-secondary loading-dots">
            Initializing
          </div>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginForm />
  }

  return <Dashboard />
} 