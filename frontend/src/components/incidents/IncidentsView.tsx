'use client'

import { useEffect, useState } from 'react'
import { incidentsAPI } from '@/lib/api'
import IncidentDetailsModal from './IncidentDetailsModal'

interface IncidentListItem {
  id: number
  type: string
  priority: number
  location: string
  status: string
  created_at: string
  updated_at: string
}

export default function IncidentsView() {
  const [incidents, setIncidents] = useState<IncidentListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedIncident, setSelectedIncident] = useState<IncidentListItem | null>(null)

  useEffect(() => {
    setLoading(true)
    incidentsAPI.getAll()
      .then((data) => {
        setIncidents(data)
        setError(null)
      })
      .catch((err) => {
        setError('Failed to load incidents')
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="bg-secondary-bg rounded-lg p-6 military-border">
      <h2 className="text-2xl font-semibold text-text-primary mb-4">
        Incidents
      </h2>
      {loading ? (
        <div className="text-text-secondary">Loading incidents...</div>
      ) : error ? (
        <div className="text-status-error">{error}</div>
      ) : incidents.length === 0 ? (
        <div className="text-text-secondary">No incidents found.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-accent">
            <thead>
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Type</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Priority</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Status</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Location</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Created At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-accent">
              {incidents.map((incident) => (
                <tr
                  key={incident.id}
                  className="hover:bg-primary-bg transition-colors cursor-pointer"
                  onClick={() => setSelectedIncident(incident)}
                >
                  <td className="px-4 py-2 capitalize">{incident.type}</td>
                  <td className="px-4 py-2">{incident.priority}</td>
                  <td className="px-4 py-2 capitalize">{incident.status}</td>
                  <td className="px-4 py-2">{incident.location}</td>
                  <td className="px-4 py-2 font-mono text-xs">{new Date(incident.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {/* Incident Details Modal Placeholder */}
      {selectedIncident && (
        <IncidentDetailsModal
          incidentId={selectedIncident.id}
          onClose={() => setSelectedIncident(null)}
        />
      )}
    </div>
  )
} 