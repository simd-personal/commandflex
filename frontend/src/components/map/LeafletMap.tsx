"use client"
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

export default function LeafletMap({ incidents }) {
  return (
    <MapContainer center={[40.7128, -74.0060]} zoom={13} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {incidents.length > 0 && (
        <Marker position={[incidents[0].latitude, incidents[0].longitude]}>
          <Popup>Test Incident: {incidents[0].incident_number}</Popup>
        </Marker>
      )}
    </MapContainer>
  )
} 