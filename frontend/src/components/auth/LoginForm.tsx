'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { authAPI } from '@/lib/api'
import { LoginFormData } from '@/types'

export default function LoginForm() {
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuthStore()
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>()

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    try {
      const response = await authAPI.login(data.username, data.password)
      
      // Store token and user data
      localStorage.setItem('token', response.access_token)
      login(response.access_token, response.user)
      
      toast.success('Login successful!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-primary-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-accent font-mono mb-2">
            CommandFlex
          </h1>
          <p className="text-text-secondary">
            Emergency Dispatch Management System
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-secondary-bg rounded-lg p-8 military-border">
          <h2 className="text-2xl font-semibold text-text-primary mb-6 text-center">
            Access Control
          </h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-text-secondary mb-2">
                Username
              </label>
              <input
                {...register('username', { required: 'Username is required' })}
                type="text"
                id="username"
                className="w-full px-4 py-3 bg-primary-bg border border-accent rounded-md text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                placeholder="Enter username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-status-error">{errors.username.message}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-text-secondary mb-2">
                Password
              </label>
              <input
                {...register('password', { required: 'Password is required' })}
                type="password"
                id="password"
                className="w-full px-4 py-3 bg-primary-bg border border-accent rounded-md text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                placeholder="Enter password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-status-error">{errors.password.message}</p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-accent text-primary-bg font-semibold py-3 px-4 rounded-md hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-secondary-bg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Authenticating...
                </span>
              ) : (
                'Authenticate'
              )}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-primary-bg rounded-md border border-accent border-opacity-30">
            <h3 className="text-sm font-medium text-accent mb-2">Demo Credentials</h3>
            <div className="text-xs text-text-secondary space-y-1">
              <p><strong>Dispatcher:</strong> dispatcher / password123</p>
              <p><strong>Responder:</strong> responder / password123</p>
              <p><strong>Supervisor:</strong> supervisor / password123</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-xs text-text-secondary">
            Secure access to emergency response management
          </p>
        </div>
      </div>
    </div>
  )
} 