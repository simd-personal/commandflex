import { useEffect, useState } from 'react'
import { incidentsAPI, unitsAPI } from '@/lib/api'

interface IncidentDetailsModalProps {
  incidentId: number
  onClose: () => void
}

export default function IncidentDetailsModal({ incidentId, onClose }: IncidentDetailsModalProps) {
  const [incident, setIncident] = useState<any>(null)
  const [timeline, setTimeline] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [showAssign, setShowAssign] = useState(false)
  const [availableUnits, setAvailableUnits] = useState<any[]>([])
  const [selectedUnit, setSelectedUnit] = useState<number | null>(null)
  const [assignNotes, setAssignNotes] = useState('')
  const [assignLoading, setAssignLoading] = useState(false)
  const [assignError, setAssignError] = useState<string | null>(null)

  const [showResolve, setShowResolve] = useState(false)
  const [resolveSummary, setResolveSummary] = useState('')
  const [resolveLoading, setResolveLoading] = useState(false)
  const [resolveError, setResolveError] = useState<string | null>(null)

  const [noteText, setNoteText] = useState('')
  const [noteLoading, setNoteLoading] = useState(false)
  const [noteError, setNoteError] = useState<string | null>(null)

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

  useEffect(() => {
    if (showAssign) {
      unitsAPI.getAvailable().then(setAvailableUnits).catch(() => setAvailableUnits([]))
    }
  }, [showAssign])

  const handleAssignUnit = async () => {
    if (!selectedUnit) return
    setAssignLoading(true)
    setAssignError(null)
    try {
      await incidentsAPI.assignUnit(incidentId, selectedUnit, assignNotes)
      setShowAssign(false)
      setSelectedUnit(null)
      setAssignNotes('')
      const [incidentData, timelineData] = await Promise.all([
        incidentsAPI.getById(incidentId),
        incidentsAPI.getTimeline(incidentId)
      ])
      setIncident(incidentData)
      setTimeline(timelineData)
    } catch (e) {
      setAssignError('Failed to assign unit')
    } finally {
      setAssignLoading(false)
    }
  }

  const handleResolve = async () => {
    if (!resolveSummary) return
    setResolveLoading(true)
    setResolveError(null)
    try {
      await incidentsAPI.resolve(incidentId, resolveSummary)
      setShowResolve(false)
      setResolveSummary('')
      const [incidentData, timelineData] = await Promise.all([
        incidentsAPI.getById(incidentId),
        incidentsAPI.getTimeline(incidentId)
      ])
      setIncident(incidentData)
      setTimeline(timelineData)
    } catch (e) {
      setResolveError('Failed to resolve incident')
    } finally {
      setResolveLoading(false)
    }
  }

  const handleAddNote = async () => {
    if (!noteText) return
    setNoteLoading(true)
    setNoteError(null)
    try {
      await incidentsAPI.addNote(incidentId, noteText)
      setNoteText('')
      const timelineData = await incidentsAPI.getTimeline(incidentId)
      setTimeline(timelineData)
    } catch (e) {
      setNoteError('Failed to add note')
    } finally {
      setNoteLoading(false)
    }
  }

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
            <div className="flex gap-4 mt-4">
              <button className="bg-accent text-primary-bg px-4 py-2 rounded" onClick={() => setShowAssign(true)}>
                Assign Unit
              </button>
              <button className="bg-status-resolved text-primary-bg px-4 py-2 rounded" onClick={() => setShowResolve(true)}>
                Resolve Incident
              </button>
              <div className="flex-1 flex gap-2">
                <input
                  type="text"
                  className="flex-1 px-2 py-1 rounded border border-accent bg-primary-bg text-text-primary"
                  placeholder="Add note..."
                  value={noteText}
                  onChange={e => setNoteText(e.target.value)}
                  disabled={noteLoading}
                />
                <button className="bg-accent text-primary-bg px-3 py-1 rounded" onClick={handleAddNote} disabled={noteLoading}>
                  Add
                </button>
              </div>
            </div>
            {noteError && <div className="text-status-error text-xs mt-1">{noteError}</div>}
          </>
        ) : null}
      </div>

      {showAssign && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-secondary-bg rounded-lg p-6 shadow-lg w-full max-w-md relative">
            <button className="absolute top-2 right-2 text-text-secondary hover:text-accent" onClick={() => setShowAssign(false)}>&times;</button>
            <h4 className="text-lg font-semibold mb-2">Assign Unit</h4>
            <select
              className="w-full mb-2 px-2 py-1 rounded border border-accent bg-primary-bg text-text-primary"
              value={selectedUnit ?? ''}
              onChange={e => setSelectedUnit(Number(e.target.value))}
            >
              <option value="">Select a unit</option>
              {availableUnits.map((unit: any) => (
                <option key={unit.id} value={unit.id}>{unit.unit_number} ({unit.type})</option>
              ))}
            </select>
            <textarea
              className="w-full mb-2 px-2 py-1 rounded border border-accent bg-primary-bg text-text-primary"
              placeholder="Dispatch notes (optional)"
              value={assignNotes}
              onChange={e => setAssignNotes(e.target.value)}
            />
            <button className="bg-accent text-primary-bg px-4 py-2 rounded w-full" onClick={handleAssignUnit} disabled={assignLoading}>
              {assignLoading ? 'Assigning...' : 'Assign'}
            </button>
            {assignError && <div className="text-status-error text-xs mt-1">{assignError}</div>}
          </div>
        </div>
      )}

      {showResolve && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-secondary-bg rounded-lg p-6 shadow-lg w-full max-w-md relative">
            <button className="absolute top-2 right-2 text-text-secondary hover:text-accent" onClick={() => setShowResolve(false)}>&times;</button>
            <h4 className="text-lg font-semibold mb-2">Resolve Incident</h4>
            <textarea
              className="w-full mb-2 px-2 py-1 rounded border border-accent bg-primary-bg text-text-primary"
              placeholder="Resolution summary"
              value={resolveSummary}
              onChange={e => setResolveSummary(e.target.value)}
            />
            <button className="bg-status-resolved text-primary-bg px-4 py-2 rounded w-full" onClick={handleResolve} disabled={resolveLoading}>
              {resolveLoading ? 'Resolving...' : 'Resolve'}
            </button>
            {resolveError && <div className="text-status-error text-xs mt-1">{resolveError}</div>}
          </div>
        </div>
      )}
    </div>
  )
} 