'use client'

import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import Sidebar from './Sidebar'
import Header from './Header'
import IncidentsView from '../incidents/IncidentsView'
import UnitsView from '../units/UnitsView'
import dynamic from 'next/dynamic'
import LogsView from '../logs/LogsView'

type ViewType = 'incidents' | 'units' | 'map' | 'logs'

const MapView = dynamic(() => import('../map/MapView'), { ssr: false })

export default function Dashboard() {
  const [currentView, setCurrentView] = useState<ViewType>('incidents')
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    localStorage.removeItem('token')
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'incidents':
        return <IncidentsView />
      case 'units':
        return <UnitsView />
      case 'map':
        return <MapView />
      case 'logs':
        return <LogsView />
      default:
        return <IncidentsView />
    }
  }

  return (
    <div className="min-h-screen bg-primary-bg flex">
      {/* Sidebar */}
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header user={user} onLogout={handleLogout} />
        
        {/* Content Area */}
        <main className="flex-1 p-6 overflow-auto">
          {renderCurrentView()}
        </main>
      </div>
    </div>
  )
} 