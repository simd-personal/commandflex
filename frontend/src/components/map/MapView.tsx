'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'

const DragDropDispatch = dynamic(() => import('./DragDropDispatch'), { ssr: false })
const UnitTrailReplay = dynamic(() => import('./UnitTrailReplay'), { ssr: false })
const TrailReplayControls = dynamic(() => import('./UnitTrailReplay').then(mod => mod.TrailReplayControls), { ssr: false })
const MutualAidRequest = dynamic(() => import('./MutualAidRequest'), { ssr: false })
const QuickMutualAidButton = dynamic(() => import('./MutualAidRequest').then(mod => mod.QuickMutualAidButton), { ssr: false })
const LeafletMap = dynamic(() => import('./LeafletMap'), { ssr: false })

export default function MapView() {
  // All hooks at the top
  const [mounted, setMounted] = useState(false)
  const [units, setUnits] = useState<any[]>([])
  const [incidents, setIncidents] = useState<any[]>([])
  const [zones, setZones] = useState<any[]>([])
  const [selectedUnit, setSelectedUnit] = useState<any>(null)
  const [selectedIncident, setSelectedIncident] = useState<any>(null)
  const [mapLayers, setMapLayers] = useState({
    units: true,
    incidents: true,
    zones: true,
    hospitals: false,
    hydrants: false,
  })
  const [showTrailReplay, setShowTrailReplay] = useState(false)
  const [isTrailPlaying, setIsTrailPlaying] = useState(false)
  const [currentTrailTime, setCurrentTrailTime] = useState('')
  const [showMutualAid, setShowMutualAid] = useState(false)
  const [enableDragDrop, setEnableDragDrop] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  // Mock data - replace with real API calls
  useEffect(() => {
    if (!mounted) return;
    const mockUnits = [
      { id: 1, unit_number: 'P-101', unit_type: 'police', status: 'available', latitude: 40.7128, longitude: -74.0060, assigned_user: { full_name: 'Officer Smith' }, assigned_incident: null },
      { id: 2, unit_number: 'F-201', unit_type: 'fire', status: 'en_route', latitude: 40.7589, longitude: -73.9851, assigned_user: { full_name: 'Firefighter Jones' }, assigned_incident: { incident_number: 'INC-20240703-001' } },
      { id: 3, unit_number: 'E-301', unit_type: 'ems', status: 'on_scene', latitude: 40.7505, longitude: -73.9934, assigned_user: { full_name: 'EMT Davis' }, assigned_incident: { incident_number: 'INC-20240703-002' } },
    ]
    const mockIncidents = [
      { id: 1, incident_number: 'INC-20240703-001', incident_type: 'Armed Robbery', priority: 1, status: 'dispatched', address: '123 Main St', latitude: 40.7589, longitude: -73.9851 },
      { id: 2, incident_number: 'INC-20240703-002', incident_type: 'Traffic Accident', priority: 2, status: 'on_scene', address: '456 Oak Ave', latitude: 40.7505, longitude: -73.9934 },
      { id: 3, incident_number: 'INC-20240703-003', incident_type: 'Medical Emergency', priority: 3, status: 'resolved', address: '789 Pine St', latitude: 40.7527, longitude: -73.9772 },
    ]
    const mockZones = [
      { id: 1, name: 'Downtown Patrol', type: 'police', latitude: 40.7128, longitude: -74.0060, radius: 1000, color: '#3B82F6' },
      { id: 2, name: 'Fire District A', type: 'fire', latitude: 40.7589, longitude: -73.9851, radius: 1500, color: '#EF4444' },
    ]
    setUnits(mockUnits)
    setIncidents(mockIncidents)
    setZones(mockZones)
    const interval = setInterval(() => {
      setUnits(prev => prev.map(unit => ({ ...unit, latitude: unit.latitude + (Math.random() - 0.5) * 0.001, longitude: unit.longitude + (Math.random() - 0.5) * 0.001 })))
    }, 5000)
    return () => clearInterval(interval)
  }, [mounted])

  // Debug log for incidents
  console.log('incidents:', incidents)
  console.log('units:', units)
  console.log('mounted:', mounted)
  console.log('mapLayers:', mapLayers)

  if (!mounted) return <div>Loading map...</div>

  const handleUnitClick = (unit: any) => {
    setSelectedUnit(unit)
    console.log('Unit clicked:', unit)
  }

  const handleIncidentClick = (incident: any) => {
    setSelectedIncident(incident)
    console.log('Incident clicked:', incident)
  }

  const handleAssignUnit = (unitId: number, incidentId: number) => {
    console.log(`Assigning unit ${unitId} to incident ${incidentId}`)
    // TODO: Implement actual assignment logic
  }

  const handleMutualAidRequest = (agencyId: number, incidentId: number, unitType: string, quantity: number) => {
    console.log(`Requesting ${quantity} ${unitType} units from agency ${agencyId} for incident ${incidentId}`)
    // TODO: Implement actual mutual aid request
  }

  const mockAgencies = [
    {
      id: 1,
      name: 'County Sheriff',
      type: 'police' as const,
      location: { lat: 40.7589, lng: -73.9851 },
      availableUnits: 3,
      responseTime: 15,
      contactInfo: { phone: '555-0101', radio: 'Channel 1' }
    },
    {
      id: 2,
      name: 'City Fire Department',
      type: 'fire' as const,
      location: { lat: 40.7505, lng: -73.9934 },
      availableUnits: 2,
      responseTime: 8,
      contactInfo: { phone: '555-0102', radio: 'Channel 2' }
    }
  ]

  const mockTrails = [
    {
      unitId: 1,
      unitNumber: 'P-101',
      positions: [
        { lat: 40.7128, lng: -74.0060, timestamp: '2024-07-03T10:00:00Z', status: 'available' },
        { lat: 40.7130, lng: -74.0058, timestamp: '2024-07-03T10:05:00Z', status: 'available' },
        { lat: 40.7132, lng: -74.0056, timestamp: '2024-07-03T10:10:00Z', status: 'en_route' },
        { lat: 40.7135, lng: -74.0053, timestamp: '2024-07-03T10:15:00Z', status: 'on_scene' },
      ]
    }
  ]

  // Custom icons for different unit types
  const createUnitIcon = (unitType: string, status: string) => {
    const statusColors = {
      'available': '#10B981', // Green
      'en_route': '#F59E0B',  // Yellow
      'on_scene': '#EF4444',  // Red
      'offline': '#6B7280',   // Gray
    }
    
    const unitIcons = {
      'police': '🚓',
      'fire': '🚒',
      'ems': '🚑',
      'sheriff': '🚔',
    }
    
    const color = statusColors[status as keyof typeof statusColors] || '#6B7280'
    const icon = unitIcons[unitType as keyof typeof unitIcons] || '🚓'
    
    return L.divIcon({
      className: 'custom-unit-icon',
      html: `
        <div style="
          background: ${color};
          border: 3px solid white;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          color: white;
        ">
          ${icon}
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 20],
    })
  }

  // Custom incident pin icon
  const createIncidentIcon = (priority: number) => {
    const priorityColors = {
      1: '#EF4444', // Red - Emergency
      2: '#F97316', // Orange - Urgent
      3: '#EAB308', // Yellow - Routine
      4: '#6B7280', // Gray - Informational
    }
    
    const color = priorityColors[priority as keyof typeof priorityColors] || '#6B7280'
    
    return L.divIcon({
      className: 'custom-incident-icon',
      html: `
        <div style="
          background: ${color};
          border: 2px solid white;
          border-radius: 4px;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          color: white;
          font-weight: bold;
        ">
          !
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    })
  }

  // Map controls component
  function MapControls() {
    const map = useMap()
    
    useEffect(() => {
      // Add custom controls
      const zoomControl = L.control.zoom({
        position: 'bottomright'
      })
      zoomControl.addTo(map)
      
      // Add layer control
      const layerControl = L.control.layers({}, {}, {
        position: 'topright',
        collapsed: false
      })
      layerControl.addTo(map)
      
      return () => {
        map.removeControl(zoomControl)
        map.removeControl(layerControl)
      }
    }, [map])
    
    return null
  }

  // Unit tracking component
  function UnitTracking({ units, onUnitClick }: { units: any[], onUnitClick: (unit: any) => void }) {
    return (
      <>
        {units.map((unit) => (
          <Marker
            key={unit.id}
            position={[unit.latitude || 40.7128, unit.longitude || -74.0060]}
            icon={createUnitIcon(unit.unit_type || 'police', unit.status || 'available')}
            eventHandlers={{
              click: () => onUnitClick(unit),
            }}
          >
            <Popup>
              <div className="unit-popup">
                <h3 className="font-bold text-lg">{unit.unit_number}</h3>
                <p className="text-sm text-gray-600">Type: {unit.unit_type}</p>
                <p className="text-sm text-gray-600">Status: {unit.status}</p>
                {unit.assigned_user && (
                  <p className="text-sm text-gray-600">Officer: {unit.assigned_user.full_name}</p>
                )}
                {unit.assigned_incident && (
                  <p className="text-sm text-red-600">Assigned to: {unit.assigned_incident.incident_number}</p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </>
    )
  }

  // Incident pins component
  function IncidentPins({ incidents, onIncidentClick }: { incidents: any[], onIncidentClick: (incident: any) => void }) {
    return (
      <>
        {incidents.map((incident) => (
          <Marker
            key={incident.id}
            position={[incident.latitude || 40.7128, incident.longitude || -74.0060]}
            icon={createIncidentIcon(incident.priority)}
            eventHandlers={{
              click: () => onIncidentClick(incident),
            }}
          >
            <Popup>
              <div className="incident-popup">
                <h3 className="font-bold text-lg">{incident.incident_number}</h3>
                <p className="text-sm text-gray-600">Type: {incident.incident_type}</p>
                <p className="text-sm text-gray-600">Priority: {incident.priority}</p>
                <p className="text-sm text-gray-600">Status: {incident.status}</p>
                <p className="text-sm text-gray-600">Address: {incident.address}</p>
                <button 
                  className="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                  onClick={() => onIncidentClick(incident)}
                >
                  View Details
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </>
    )
  }

  // Geofencing zones component
  function GeofencingZones({ zones }: { zones: any[] }) {
    return (
      <>
        {zones.map((zone) => (
          <Circle
            key={zone.id}
            center={[zone.latitude, zone.longitude]}
            radius={zone.radius}
            pathOptions={{
              color: zone.color || '#3B82F6',
              fillColor: zone.color || '#3B82F6',
              fillOpacity: 0.1,
              weight: 2
            }}
          >
            <Popup>
              <div className="zone-popup">
                <h3 className="font-bold text-lg">{zone.name}</h3>
                <p className="text-sm text-gray-600">Type: {zone.type}</p>
                <p className="text-sm text-gray-600">Radius: {zone.radius}m</p>
              </div>
            </Popup>
          </Circle>
        ))}
      </>
    )
  }

  // Map layers component
  function MapLayers() {
    const map = useMap()
    
    useEffect(() => {
      // Add hospital layer
      const hospitalLayer = L.layerGroup([
        L.marker([40.7589, -73.9851]).bindPopup('Hospital A'),
        L.marker([40.7505, -73.9934]).bindPopup('Hospital B'),
      ])
      
      // Add fire hydrant layer
      const hydrantLayer = L.layerGroup([
        L.marker([40.7527, -73.9772]).bindPopup('Fire Hydrant'),
        L.marker([40.7484, -73.9857]).bindPopup('Fire Hydrant'),
      ])
      
      // Add to layer control
      const layerControl = L.control.layers({}, {
        'Hospitals': hospitalLayer,
        'Fire Hydrants': hydrantLayer,
      }, {
        position: 'topright',
        collapsed: false
      })
      
      layerControl.addTo(map)
      
      return () => {
        map.removeControl(layerControl)
      }
    }, [map])
    
    return null
  }

  return (
    <div className="bg-secondary-bg rounded-lg p-6 military-border h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-text-primary">
          Live Dispatch Map
        </h2>
        <div className="flex gap-2">
          <button 
            onClick={() => setEnableDragDrop(!enableDragDrop)}
            className={`px-3 py-1 rounded text-sm ${
              enableDragDrop ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'
            }`}
          >
            {enableDragDrop ? 'Disable' : 'Enable'} Drag & Drop
          </button>
          <button className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">
            Full Screen
          </button>
          <button className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600">
            Refresh
          </button>
        </div>
      </div>
      
      {/* Map Legend */}
      <div className="mb-4 p-3 bg-primary-bg rounded border">
        <h3 className="font-semibold mb-2">Legend</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium mb-1">Unit Status</h4>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span>Available</span>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span>En Route</span>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span>On Scene</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-500"></div>
              <span>Offline</span>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-1">Incident Priority</h4>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded bg-red-500"></div>
              <span>Priority 1 (Emergency)</span>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded bg-orange-500"></div>
              <span>Priority 2 (Urgent)</span>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded bg-yellow-500"></div>
              <span>Priority 3 (Routine)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-gray-500"></div>
              <span>Priority 4 (Info)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Map */}
      <div className="h-96 rounded-lg overflow-hidden border">
        <LeafletMap incidents={incidents} />
      </div>

      {/* Advanced Features Controls */}
      <div className="mt-4 space-y-4">
        {/* Quick Actions */}
        <div className="flex gap-2 flex-wrap">
          <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Assign Nearest Unit
          </button>
          <QuickMutualAidButton onQuickRequest={() => setShowMutualAid(!showMutualAid)} />
          <button 
            onClick={() => setShowTrailReplay(!showTrailReplay)}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
          >
            {showTrailReplay ? 'Hide' : 'Show'} Unit Trails
          </button>
          <button className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600">
            Incident Playback
          </button>
        </div>

        {/* Trail Replay Controls */}
        {showTrailReplay && TrailReplayControls && (
          <TrailReplayControls
            isPlaying={isTrailPlaying}
            onPlayPause={() => setIsTrailPlaying(!isTrailPlaying)}
            onReset={() => setIsTrailPlaying(false)}
            onSpeedChange={(speed: number) => console.log('Speed changed:', speed)}
            currentTime={currentTrailTime || '00:00'}
            totalTime="01:00"
          />
        )}
      </div>

      {/* Selected Unit/Incident Info */}
      {(selectedUnit || selectedIncident) && (
        <div className="mt-4 p-4 bg-primary-bg rounded border">
          <h3 className="font-semibold mb-2">
            {selectedUnit ? 'Selected Unit' : 'Selected Incident'}
          </h3>
          <pre className="text-sm text-text-secondary">
            {JSON.stringify(selectedUnit || selectedIncident, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
} 