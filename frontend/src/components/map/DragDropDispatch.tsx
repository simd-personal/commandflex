'use client'

import { useState, useRef, useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'

interface DragDropDispatchProps {
  units: any[]
  incidents: any[]
  onAssignUnit: (unitId: number, incidentId: number) => void
}

export default function DragDropDispatch({ units, incidents, onAssignUnit }: DragDropDispatchProps) {
  const map = useMap()
  const [draggedUnit, setDraggedUnit] = useState<any>(null)
  const [dragPreview, setDragPreview] = useState<L.Marker | null>(null)
  const [showETAs, setShowETAs] = useState(false)

  // Calculate ETA between two points
  const calculateETA = (unitLat: number, unitLng: number, incidentLat: number, incidentLng: number) => {
    const R = 6371 // Earth's radius in km
    const dLat = (incidentLat - unitLat) * Math.PI / 180
    const dLng = (incidentLng - unitLng) * Math.PI / 180
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(unitLat * Math.PI / 180) * Math.cos(incidentLat * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    const distance = R * c // Distance in km
    
    // Assume average speed of 50 km/h for police, 40 km/h for fire/EMS
    const avgSpeed = 50 // km/h
    const etaMinutes = Math.round((distance / avgSpeed) * 60)
    
    return { distance: Math.round(distance * 10) / 10, etaMinutes }
  }

  // Handle unit drag start
  const handleUnitDragStart = (unit: any, event: any) => {
    setDraggedUnit(unit)
    
    // Create drag preview marker
    const previewMarker = L.marker([event.latlng.lat, event.latlng.lng], {
      icon: L.divIcon({
        className: 'drag-preview-icon',
        html: `
          <div style="
            background: #3B82F6;
            border: 3px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            color: white;
            opacity: 0.8;
          ">
            🚓
          </div>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      })
    })
    
    previewMarker.addTo(map)
    setDragPreview(previewMarker)
    
    // Show ETAs for all incidents
    setShowETAs(true)
  }

  // Handle unit drag
  const handleUnitDrag = (event: any) => {
    if (dragPreview) {
      dragPreview.setLatLng([event.latlng.lat, event.latlng.lng])
    }
  }

  // Handle unit drag end
  const handleUnitDragEnd = (event: any) => {
    if (draggedUnit && dragPreview) {
      // Find nearest incident
      let nearestIncident: any = null
      let minDistance = Infinity
      
      incidents.forEach((incident: any) => {
        const distance = map.distance(
          [event.latlng.lat, event.latlng.lng],
          [incident.latitude, incident.longitude]
        )
        if (distance < minDistance && distance < 500) { // Within 500m
          minDistance = distance
          nearestIncident = incident
        }
      })
      
      if (nearestIncident) {
        // Show confirmation dialog
        const { distance, etaMinutes } = calculateETA(
          draggedUnit.latitude,
          draggedUnit.longitude,
          nearestIncident.latitude,
          nearestIncident.longitude
        )
        
        const confirmed = window.confirm(
          `Assign ${draggedUnit.unit_number} to ${nearestIncident.incident_number}?\n\n` +
          `Distance: ${distance} km\nETA: ${etaMinutes} minutes`
        )
        
        if (confirmed) {
          onAssignUnit(draggedUnit.id, nearestIncident.id)
        }
      }
      
      // Clean up
      map.removeLayer(dragPreview)
      setDragPreview(null)
      setDraggedUnit(null)
      setShowETAs(false)
    }
  }

  // Add drag events to unit markers
  useEffect(() => {
    const unitMarkers: L.Marker[] = []
    
    units.forEach(unit => {
      const marker = L.marker([unit.latitude, unit.longitude], {
        draggable: true,
        icon: L.divIcon({
          className: 'draggable-unit-icon',
          html: `
            <div style="
              background: #10B981;
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
              cursor: grab;
            ">
              🚓
            </div>
          `,
          iconSize: [40, 40],
          iconAnchor: [20, 20],
        })
      })
      
      marker.on('dragstart', (e) => handleUnitDragStart(unit, e))
      marker.on('drag', handleUnitDrag)
      marker.on('dragend', handleUnitDragEnd)
      
      marker.addTo(map)
      unitMarkers.push(marker)
    })
    
    return () => {
      unitMarkers.forEach(marker => {
        map.removeLayer(marker)
      })
    }
  }, [units, map])

  // Show ETA labels when dragging
  useEffect(() => {
    if (!showETAs || !draggedUnit) return
    
    const etaLabels: L.Marker[] = []
    
    incidents.forEach(incident => {
      const { distance, etaMinutes } = calculateETA(
        draggedUnit.latitude,
        draggedUnit.longitude,
        incident.latitude,
        incident.longitude
      )
      
      const label = L.marker([incident.latitude, incident.longitude], {
        icon: L.divIcon({
          className: 'eta-label',
          html: `
            <div style="
              background: rgba(0,0,0,0.8);
              color: white;
              padding: 4px 8px;
              border-radius: 4px;
              font-size: 12px;
              font-weight: bold;
              white-space: nowrap;
            ">
              ${etaMinutes}m (${distance}km)
            </div>
          `,
          iconSize: [0, 0],
          iconAnchor: [0, 0],
        })
      })
      
      label.addTo(map)
      etaLabels.push(label)
    })
    
    return () => {
      etaLabels.forEach(label => {
        map.removeLayer(label)
      })
    }
  }, [showETAs, draggedUnit, incidents, map])

  return null
} 