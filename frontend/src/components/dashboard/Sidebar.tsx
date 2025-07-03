'use client'

import { 
  ExclamationTriangleIcon, 
  TruckIcon, 
  MapIcon, 
  DocumentTextIcon 
} from '@heroicons/react/24/outline'

interface SidebarProps {
  currentView: string
  onViewChange: (view: 'incidents' | 'units' | 'map' | 'logs') => void
}

export default function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const navigation = [
    {
      name: 'Incidents',
      view: 'incidents' as const,
      icon: ExclamationTriangleIcon,
      description: 'Emergency incidents'
    },
    {
      name: 'Units',
      view: 'units' as const,
      icon: TruckIcon,
      description: 'Response units'
    },
    {
      name: 'Map',
      view: 'map' as const,
      icon: MapIcon,
      description: 'Geospatial view'
    },
    {
      name: 'Logs',
      view: 'logs' as const,
      icon: DocumentTextIcon,
      description: 'Activity logs'
    }
  ]

  return (
    <div className="w-64 bg-secondary-bg border-r border-accent border-opacity-30 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-accent border-opacity-30">
        <h1 className="text-xl font-bold text-accent font-mono">
          CommandFlex
        </h1>
        <p className="text-xs text-text-secondary mt-1">
          Dispatch Control
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = currentView === item.view
          
          return (
            <button
              key={item.name}
              onClick={() => onViewChange(item.view)}
              className={`w-full flex items-center px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                isActive
                  ? 'bg-accent text-primary-bg military-glow'
                  : 'text-text-secondary hover:bg-primary-bg hover:text-accent'
              }`}
            >
              <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
              <div>
                <div className="font-medium">{item.name}</div>
                <div className="text-xs opacity-75">{item.description}</div>
              </div>
            </button>
          )
        })}
      </nav>

      {/* Status Indicator */}
      <div className="p-4 border-t border-accent border-opacity-30">
        <div className="flex items-center justify-between text-sm">
          <span className="text-text-secondary">System Status</span>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-status-resolved rounded-full mr-2"></div>
            <span className="text-status-resolved">Online</span>
          </div>
        </div>
      </div>
    </div>
  )
} 