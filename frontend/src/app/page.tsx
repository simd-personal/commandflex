'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import LoginForm from '@/components/auth/LoginForm'
import Dashboard from '@/components/dashboard/Dashboard'
import { authAPI } from '@/lib/api'

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)
  const { user, isAuthenticated, setUser, logout } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token && !user) {
      authAPI.me()
        .then((userData) => {
          setUser(userData)
        })
        .catch(() => {
          logout()
        })
        .finally(() => setIsLoading(false))
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