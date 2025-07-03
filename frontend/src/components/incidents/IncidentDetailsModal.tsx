import { useEffect, useState } from 'react'
import { incidentsAPI } from '@/lib/api'

interface IncidentDetailsModalProps {
  incidentId: number
  onClose: () => void
}

export default function IncidentDetailsModal({ incidentId, onClose }: IncidentDetailsModalProps) {
  const [incident, setIncident] = useState<any>(null)
  const [timeline, setTimeline] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      incidentsAPI.getById(incidentId),
      incidentsAPI.getTimeline ? incidentsAPI.getTimeline(incidentId) : Promise.resolve([])
    ])
      .then(([incidentData, timelineData]) => {
        setIncident(incidentData)
        setTimeline(timelineData)
        setError(null)
      })
      .catch(() => setError('Failed to load incident details'))
      .finally(() => setLoading(false))
  }, [incidentId])

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-secondary-bg rounded-lg p-8 shadow-lg w-full max-w-2xl relative">
        <button
          className="absolute top-4 right-4 text-text-secondary hover:text-accent"
          onClick={onClose}
        >
          &times;
        </button>
        {loading ? (
          <div className="text-text-secondary">Loading incident details...</div>
        ) : error ? (
          <div className="text-status-error">{error}</div>
        ) : incident ? (
          <>
            <h3 className="text-xl font-bold mb-2 text-accent">Incident #{incident.id}</h3>
            <div className="mb-4">
              <div><b>Type:</b> {incident.type}</div>
              <div><b>Priority:</b> {incident.priority}</div>
              <div><b>Status:</b> {incident.status}</div>
              <div><b>Location:</b> {incident.location || incident.address}</div>
              <div><b>Description:</b> {incident.description}</div>
              <div><b>Caller:</b> {incident.caller_name} ({incident.caller_phone})</div>
              <div><b>Created At:</b> {new Date(incident.created_at).toLocaleString()}</div>
              <div><b>Updated At:</b> {new Date(incident.updated_at).toLocaleString()}</div>
            </div>
            <h4 className="text-lg font-semibold mb-2">Timeline</h4>
            <div className="bg-primary-bg rounded-md p-4 max-h-48 overflow-y-auto mb-4">
              {timeline.length === 0 ? (
                <div className="text-text-secondary">No timeline entries.</div>
              ) : (
                <ul className="space-y-2">
                  {timeline.map((entry) => (
                    <li key={entry.id} className="text-xs">
                      <span className="font-mono text-accent">[{new Date(entry.timestamp).toLocaleString()}]</span> <b>{entry.type}</b>: {entry.message}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            {/* Actions (Assign, Resolve, Add Note) will go here */}
          </>
        ) : null}
      </div>
    </div>
  )
} 