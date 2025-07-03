'use client'

import { useState, useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'

interface MutualAidAgency {
  id: number
  name: string
  type: 'police' | 'fire' | 'ems'
  location: {
    lat: number
    lng: number
  }
  availableUnits: number
  responseTime: number // minutes
  contactInfo: {
    phone: string
    radio: string
  }
}

interface MutualAidRequestProps {
  agencies: MutualAidAgency[]
  onRequestAid: (agencyId: number, incidentId: number, unitType: string, quantity: number) => void
}

export default function MutualAidRequest({ agencies, onRequestAid }: MutualAidRequestProps) {
  const map = useMap()
  const [selectedAgency, setSelectedAgency] = useState<MutualAidAgency | null>(null)
  const [showRequestModal, setShowRequestModal] = useState(false)
  const [requestForm, setRequestForm] = useState({
    unitType: 'police',
    quantity: 1,
    priority: 'normal',
    notes: '',
  })

  // Agency markers
  useEffect(() => {
    const markers: L.Marker[] = []

    agencies.forEach(agency => {
      const icon = L.divIcon({
        className: 'mutual-aid-agency-icon',
        html: `
          <div style="
            background: ${agency.type === 'police' ? '#3B82F6' : agency.type === 'fire' ? '#EF4444' : '#10B981'};
            border: 3px solid white;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            color: white;
            cursor: pointer;
          ">
            ${agency.type === 'police' ? '🚔' : agency.type === 'fire' ? '🚒' : '🚑'}
          </div>
        `,
        iconSize: [35, 35],
        iconAnchor: [17.5, 17.5],
      })

      const marker = L.marker([agency.location.lat, agency.location.lng], { icon })
        .bindPopup(`
          <div class="agency-popup">
            <h3 class="font-bold text-lg">${agency.name}</h3>
            <p class="text-sm text-gray-600">Type: ${agency.type.toUpperCase()}</p>
            <p class="text-sm text-gray-600">Available Units: ${agency.availableUnits}</p>
            <p class="text-sm text-gray-600">Response Time: ${agency.responseTime} min</p>
            <p class="text-sm text-gray-600">Phone: ${agency.contactInfo.phone}</p>
            <p class="text-sm text-gray-600">Radio: ${agency.contactInfo.radio}</p>
            <button 
              class="mt-2 px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
              onclick="window.requestMutualAid(${agency.id})"
            >
              Request Aid
            </button>
          </div>
        `)

      marker.on('click', () => {
        setSelectedAgency(agency)
        setShowRequestModal(true)
      })

      marker.addTo(map)
      markers.push(marker)
    })

    // Add global function for popup button
    ;(window as any).requestMutualAid = (agencyId: number) => {
      const agency = agencies.find(a => a.id === agencyId)
      if (agency) {
        setSelectedAgency(agency)
        setShowRequestModal(true)
      }
    }

    return () => {
      markers.forEach(marker => map.removeLayer(marker))
      delete (window as any).requestMutualAid
    }
  }, [agencies, map])

  const handleRequestSubmit = () => {
    if (selectedAgency) {
      onRequestAid(
        selectedAgency.id,
        1, // incidentId - would come from context
        requestForm.unitType,
        requestForm.quantity
      )
      setShowRequestModal(false)
      setSelectedAgency(null)
      setRequestForm({
        unitType: 'police',
        quantity: 1,
        priority: 'normal',
        notes: '',
      })
    }
  }

  return (
    <>
      {/* Mutual Aid Request Modal */}
      {showRequestModal && selectedAgency && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-secondary-bg p-6 rounded-lg border border-accent-color max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold mb-4">
              Request Mutual Aid - {selectedAgency.name}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Unit Type</label>
                <select
                  value={requestForm.unitType}
                  onChange={(e) => setRequestForm(prev => ({ ...prev, unitType: e.target.value }))}
                  className="w-full px-3 py-2 bg-primary-bg border border-accent-color rounded text-text-primary"
                >
                  <option value="police">Police Units</option>
                  <option value="fire">Fire Units</option>
                  <option value="ems">EMS Units</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Quantity</label>
                <input
                  type="number"
                  min="1"
                  max={selectedAgency.availableUnits}
                  value={requestForm.quantity}
                  onChange={(e) => setRequestForm(prev => ({ ...prev, quantity: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 bg-primary-bg border border-accent-color rounded text-text-primary"
                />
                <p className="text-xs text-text-secondary mt-1">
                  Max available: {selectedAgency.availableUnits}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <select
                  value={requestForm.priority}
                  onChange={(e) => setRequestForm(prev => ({ ...prev, priority: e.target.value }))}
                  className="w-full px-3 py-2 bg-primary-bg border border-accent-color rounded text-text-primary"
                >
                  <option value="normal">Normal</option>
                  <option value="urgent">Urgent</option>
                  <option value="emergency">Emergency</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Notes</label>
                <textarea
                  value={requestForm.notes}
                  onChange={(e) => setRequestForm(prev => ({ ...prev, notes: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 bg-primary-bg border border-accent-color rounded text-text-primary"
                  placeholder="Additional details..."
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <button
                onClick={handleRequestSubmit}
                className="flex-1 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Send Request
              </button>
              <button
                onClick={() => setShowRequestModal(false)}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
            
            <div className="mt-4 p-3 bg-primary-bg rounded border border-accent-color">
              <h4 className="font-medium mb-2">Agency Info</h4>
              <div className="text-sm text-text-secondary space-y-1">
                <div>Response Time: {selectedAgency.responseTime} minutes</div>
                <div>Phone: {selectedAgency.contactInfo.phone}</div>
                <div>Radio: {selectedAgency.contactInfo.radio}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

// Quick mutual aid button component
export function QuickMutualAidButton({ 
  onQuickRequest 
}: { 
  onQuickRequest: () => void 
}) {
  return (
    <button
      onClick={onQuickRequest}
      className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 flex items-center gap-2"
    >
      🆘 Quick Mutual Aid
    </button>
  )
} 