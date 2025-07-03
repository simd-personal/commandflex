// User types
export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: 'dispatcher' | 'responder' | 'supervisor' | 'admin'
  is_active: boolean
  created_at: string
  updated_at?: string
}

// Incident types
export interface Incident {
  id: number
  incident_number: string
  type: 'fire' | 'medical' | 'police' | 'traffic' | 'other'
  priority: '1' | '2' | '3' | '4'
  status: 'new' | 'dispatched' | 'en_route' | 'on_scene' | 'resolved' | 'cancelled'
  address: string
  latitude?: number
  longitude?: number
  description: string
  caller_name?: string
  caller_phone?: string
  created_by: number
  created_at: string
  updated_at?: string
  resolved_at?: string
}

// Unit types
export interface Unit {
  id: number
  unit_number: string
  type: 'police' | 'fire' | 'ems' | 'special'
  status: 'available' | 'en_route' | 'on_scene' | 'cleared' | 'out_of_service'
  current_latitude?: number
  current_longitude?: number
  last_location_update?: string
  assigned_incident_id?: number
  assigned_user_id?: number
  description?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

// Dispatch types
export interface Dispatch {
  id: number
  incident_id: number
  unit_id: number
  dispatched_by: number
  status: 'dispatched' | 'en_route' | 'on_scene' | 'cleared' | 'cancelled'
  dispatch_time: string
  en_route_time?: string
  on_scene_time?: string
  cleared_time?: string
  dispatch_notes?: string
  arrival_notes?: string
  clearance_notes?: string
}

// Log types
export interface Log {
  id: number
  type: string
  message: string
  details?: Record<string, any>
  user_id?: number
  incident_id?: number
  unit_id?: number
  created_at: string
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

// Form types
export interface LoginFormData {
  username: string
  password: string
}

export interface IncidentFormData {
  type: string
  priority: string
  address: string
  description: string
  caller_name?: string
  caller_phone?: string
  latitude?: number
  longitude?: number
}

export interface UnitFormData {
  unit_number: string
  type: string
  description?: string
}

export interface DispatchFormData {
  incident_id: number
  unit_id: number
  dispatch_notes?: string
}

// WebSocket types
export interface WebSocketMessage {
  type: string
  data?: any
  message?: string
  timestamp?: string
}

export interface WebSocketConnection {
  user_id: number
  username: string
  role: string
  connected_at: string
} 