'use client'

import { User } from '@/types'
import { 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon 
} from '@heroicons/react/24/outline'

interface HeaderProps {
  user: User | null
  onLogout: () => void
}

export default function Header({ user, onLogout }: HeaderProps) {
  return (
    <header className="bg-secondary-bg border-b border-accent border-opacity-30 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Current time and status */}
        <div className="flex items-center space-x-6">
          <div className="text-sm text-text-secondary">
            <div className="font-mono">
              {new Date().toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
              })}
            </div>
            <div className="text-xs">
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-status-resolved rounded-full animate-pulse"></div>
            <span className="text-sm text-status-resolved">System Active</span>
          </div>
        </div>

        {/* Right side - User info and logout */}
        <div className="flex items-center space-x-4">
          {user && (
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <div className="text-sm font-medium text-text-primary">
                  {user.full_name}
                </div>
                <div className="text-xs text-text-secondary capitalize">
                  {user.role}
                </div>
              </div>
              <UserCircleIcon className="h-8 w-8 text-accent" />
            </div>
          )}
          
          <button
            onClick={onLogout}
            className="flex items-center space-x-2 px-3 py-2 text-text-secondary hover:text-accent hover:bg-primary-bg rounded-md transition-colors duration-200"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5" />
            <span className="text-sm">Logout</span>
          </button>
        </div>
      </div>
    </header>
  )
} 