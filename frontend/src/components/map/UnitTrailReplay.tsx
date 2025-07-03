'use client'

import { useState, useEffect, useRef } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'

interface UnitTrail {
  unitId: number
  unitNumber: string
  positions: Array<{
    lat: number
    lng: number
    timestamp: string
    status: string
  }>
}

interface UnitTrailReplayProps {
  trails: UnitTrail[]
  isPlaying: boolean
  onTimeUpdate: (timestamp: string) => void
}

export default function UnitTrailReplay({ trails, isPlaying, onTimeUpdate }: UnitTrailReplayProps) {
  const map = useMap()
  const [currentTimeIndex, setCurrentTimeIndex] = useState(0)
  const [trailMarkers, setTrailMarkers] = useState<L.Marker[]>([])
  const [trailLines, setTrailLines] = useState<L.Polyline[]>([])
  const [breadcrumbs, setBreadcrumbs] = useState<L.Circle[]>([])
  const animationRef = useRef<number>()

  // Get all unique timestamps from all trails
  const getAllTimestamps = () => {
    const timestamps = new Set<string>()
    trails.forEach(trail => {
      trail.positions.forEach(pos => timestamps.add(pos.timestamp))
    })
    return Array.from(timestamps).sort()
  }

  const timestamps = getAllTimestamps()

  // Create breadcrumb for a position
  const createBreadcrumb = (lat: number, lng: number, status: string, timestamp: string) => {
    const statusColors = {
      'available': '#10B981',
      'en_route': '#F59E0B',
      'on_scene': '#EF4444',
      'offline': '#6B7280',
    }
    
    const color = statusColors[status as keyof typeof statusColors] || '#6B7280'
    
    return L.circle([lat, lng], {
      radius: 3,
      fillColor: color,
      color: 'white',
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8,
    }).bindPopup(`
      <div>
        <strong>Time:</strong> ${new Date(timestamp).toLocaleTimeString()}<br>
        <strong>Status:</strong> ${status}<br>
        <strong>Location:</strong> ${lat.toFixed(6)}, ${lng.toFixed(6)}
      </div>
    `)
  }

  // Update trail display for current time
  const updateTrailDisplay = (timeIndex: number) => {
    // Clear previous markers and lines
    trailMarkers.forEach(marker => map.removeLayer(marker))
    trailLines.forEach(line => map.removeLayer(line))
    breadcrumbs.forEach(crumb => map.removeLayer(crumb))

    const currentTimestamp = timestamps[timeIndex]
    const newTrailMarkers: L.Marker[] = []
    const newTrailLines: L.Polyline[] = []
    const newBreadcrumbs: L.Circle[] = []

    trails.forEach(trail => {
      // Find current position for this unit
      const currentPos = trail.positions.find(pos => pos.timestamp === currentTimestamp)
      if (currentPos) {
        // Create current position marker
        const marker = L.marker([currentPos.lat, currentPos.lng], {
          icon: L.divIcon({
            className: 'trail-unit-marker',
            html: `
              <div style="
                background: #3B82F6;
                border: 3px solid white;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                color: white;
              ">
                🚓
              </div>
            `,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
          })
        }).bindPopup(`
          <div>
            <strong>${trail.unitNumber}</strong><br>
            <strong>Time:</strong> ${new Date(currentTimestamp).toLocaleTimeString()}<br>
            <strong>Status:</strong> ${currentPos.status}
          </div>
        `)

        marker.addTo(map)
        newTrailMarkers.push(marker)

        // Create trail line from start to current position
        const positionsUpToNow = trail.positions
          .filter(pos => pos.timestamp <= currentTimestamp)
          .map(pos => [pos.lat, pos.lng])

        if (positionsUpToNow.length > 1) {
          const line = L.polyline(positionsUpToNow as [number, number][], {
            color: '#3B82F6',
            weight: 3,
            opacity: 0.7,
            dashArray: '5, 5',
          })

          line.addTo(map)
          newTrailLines.push(line)
        }

        // Add breadcrumbs for all positions up to current time
        trail.positions
          .filter(pos => pos.timestamp <= currentTimestamp)
          .forEach(pos => {
            const breadcrumb = createBreadcrumb(pos.lat, pos.lng, pos.status, pos.timestamp)
            breadcrumb.addTo(map)
            newBreadcrumbs.push(breadcrumb)
          })
      }
    })

    setTrailMarkers(newTrailMarkers)
    setTrailLines(newTrailLines)
    setBreadcrumbs(newBreadcrumbs)
    onTimeUpdate(currentTimestamp)
  }

  // Animation loop
  useEffect(() => {
    if (isPlaying && timestamps.length > 0) {
      const animate = () => {
        setCurrentTimeIndex(prev => {
          const next = (prev + 1) % timestamps.length
          updateTrailDisplay(next)
          return next
        })
        animationRef.current = requestAnimationFrame(animate)
      }
      animationRef.current = requestAnimationFrame(animate)
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isPlaying, timestamps])

  // Initial display
  useEffect(() => {
    if (timestamps.length > 0) {
      updateTrailDisplay(currentTimeIndex)
    }
  }, [trails])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      trailMarkers.forEach(marker => map.removeLayer(marker))
      trailLines.forEach(line => map.removeLayer(line))
      breadcrumbs.forEach(crumb => map.removeLayer(crumb))
    }
  }, [])

  return null
}

// Control panel component for trail replay
export function TrailReplayControls({ 
  isPlaying, 
  onPlayPause, 
  onReset, 
  onSpeedChange, 
  currentTime, 
  totalTime 
}: {
  isPlaying: boolean
  onPlayPause: () => void
  onReset: () => void
  onSpeedChange: (speed: number) => void
  currentTime: string
  totalTime: string
}) {
  return (
    <div className="trail-replay-controls bg-secondary-bg p-4 rounded-lg border border-accent-color">
      <h3 className="text-lg font-semibold mb-3">Unit Trail Replay</h3>
      
      <div className="flex items-center gap-4 mb-3">
        <button
          onClick={onPlayPause}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {isPlaying ? '⏸️ Pause' : '▶️ Play'}
        </button>
        
        <button
          onClick={onReset}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          🔄 Reset
        </button>
        
        <select
          onChange={(e) => onSpeedChange(Number(e.target.value))}
          className="px-3 py-2 bg-primary-bg border border-accent-color rounded text-text-primary"
        >
          <option value={1}>1x Speed</option>
          <option value={2}>2x Speed</option>
          <option value={5}>5x Speed</option>
          <option value={10}>10x Speed</option>
        </select>
      </div>
      
      <div className="text-sm text-text-secondary">
        <div>Current Time: {currentTime}</div>
        <div>Total Duration: {totalTime}</div>
      </div>
    </div>
  )
} 