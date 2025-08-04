# Modern React Web UI Implementation Plan

## Project Overview

This document outlines the implementation plan for a modern React web interface for the GA Modbus Python Application using the shadcn/ui component library. The web UI will provide a modern, responsive interface for battery management system monitoring, session management, and data visualization.

## Current Application Analysis

### Core Features Identified
- **Real-time Battery Monitoring**: 8-cell LiFePO4 battery pack monitoring via Modbus RTU
- **Data Logging**: CSV-based data logging with timestamped files
- **Session Management**: File-based session tracking with metadata
- **Cell Runaway Detection**: Real-time monitoring for cell voltage anomalies
- **Balance Detection**: Cell balancing activity monitoring
- **CSV Visualization**: Data plotting and analytics
- **Auto-logging**: Intelligent logging based on current thresholds
- **Settings Management**: Configuration for thresholds, ports, and intervals

### Technical Stack (Current)
- **Backend**: Python 3.x with PyQt6 GUI
- **Communication**: Modbus RTU over serial (pymodbus)
- **Data Storage**: CSV files + JSON metadata
- **Visualization**: matplotlib for plotting

## React Web UI Architecture

### Technology Stack
- **Frontend Framework**: React 18 with TypeScript
- **UI Library**: shadcn/ui (Radix UI primitives + Tailwind CSS)
- **State Management**: Zustand or Redux Toolkit
- **Real-time Communication**: WebSockets + Socket.IO
- **Charts/Visualization**: Recharts or Chart.js
- **Build Tool**: Vite
- **Testing**: Vitest + React Testing Library
- **API Communication**: Axios or Fetch API

### Backend API Requirements
- **FastAPI** or **Flask** Python backend
- **WebSocket support** for real-time data streaming
- **REST API** for session management and configuration
- **File serving** for CSV downloads and data export

## Implementation Phases

### Phase 1: Project Setup & Core Infrastructure (1-2 weeks)

#### 1.1 Project Initialization
```bash
# Create React project with Vite
npm create vite@latest ga-bms-web-ui -- --template react-ts
cd ga-bms-web-ui

# Install core dependencies
npm install

# Install shadcn/ui
npx shadcn@latest init

# Install additional dependencies
npm install zustand socket.io-client recharts axios date-fns lucide-react
npm install -D @types/node
```

#### 1.2 shadcn/ui Component Setup
```bash
# Install essential shadcn components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add table
npx shadcn@latest add tabs
npx shadcn@latest add input
npx shadcn@latest add select
npx shadcn@latest add dialog
npx shadcn@latest add toast
npx shadcn@latest add badge
npx shadcn@latest add progress
npx shadcn@latest add alert
npx shadcn@latest add switch
npx shadcn@latest add slider
npx shadcn@latest add chart
```

#### 1.3 Project Structure
```
src/
├── components/
│   ├── ui/           # shadcn/ui components
│   ├── layout/       # Layout components
│   ├── monitoring/   # Real-time monitoring components
│   ├── sessions/     # Session management components
│   ├── analytics/    # Data visualization components
│   └── settings/     # Configuration components
├── stores/           # Zustand stores
├── services/         # API services
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
├── hooks/            # Custom React hooks
└── pages/            # Page components
```

### Phase 2: Backend API Development (2-3 weeks)

#### 2.1 FastAPI Backend Setup
```python
# requirements.txt additions
fastapi
uvicorn
websockets
python-socketio
pydantic
```

#### 2.2 API Endpoints
```python
# Core API endpoints
GET /api/status                    # System status
POST /api/connection              # Connect/disconnect Modbus
GET /api/data/realtime           # Current battery data
WebSocket /ws/realtime           # Real-time data stream

# Session management
GET /api/sessions                # List sessions
POST /api/sessions               # Create session
GET /api/sessions/{id}           # Session details
PUT /api/sessions/{id}           # Update session
DELETE /api/sessions/{id}        # Delete session

# Data and analytics
GET /api/sessions/{id}/csv       # Session CSV data
GET /api/sessions/{id}/analytics # Session analytics
GET /api/runaway-events          # Cell runaway events

# Configuration
GET /api/settings                # Get settings
PUT /api/settings                # Update settings
GET /api/ports                   # Available serial ports
```

#### 2.3 WebSocket Implementation
```python
# Real-time data broadcasting
class DataBroadcaster:
    async def broadcast_battery_data(self, data):
        # Broadcast to all connected clients
        await self.emit('battery_data', data)
    
    async def broadcast_runaway_event(self, event):
        # Alert clients of runaway events
        await self.emit('runaway_alert', event)
```

### Phase 3: Core UI Components (3-4 weeks)

#### 3.1 Layout Components
```tsx
// Main layout with sidebar navigation
const Layout = () => (
  <div className="flex h-screen bg-background">
    <Sidebar />
    <main className="flex-1 overflow-hidden">
      <Header />
      <div className="p-6">
        <Outlet />
      </div>
    </main>
  </div>
)

// Navigation sidebar
const Sidebar = () => (
  <div className="w-64 bg-card border-r">
    <nav className="p-4">
      <NavItem icon={Activity} to="/monitoring">Real-time</NavItem>
      <NavItem icon={Database} to="/sessions">Sessions</NavItem>
      <NavItem icon={BarChart3} to="/analytics">Analytics</NavItem>
      <NavItem icon={Settings} to="/settings">Settings</NavItem>
    </nav>
  </div>
)
```

#### 3.2 Real-time Monitoring Dashboard
```tsx
const MonitoringDashboard = () => {
  const { batteryData, isConnected } = useBatteryData()
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      <ConnectionStatus status={isConnected} />
      <CellVoltagesCard data={batteryData.cellVoltages} />
      <PackVoltageCard voltage={batteryData.packVoltage} />
      <CurrentCard current={batteryData.current} />
      <SOCCard soc={batteryData.soc} />
      <TemperatureCard temps={batteryData.temperatures} />
      <CellDeltaCard delta={batteryData.cellDelta} />
      <RunawayAlertsCard events={batteryData.runawayEvents} />
    </div>
  )
}

// Cell voltages component with color coding
const CellVoltagesCard = ({ data }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Battery className="h-5 w-5" />
        Cell Voltages
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div className="grid grid-cols-2 gap-2">
        {data.map((voltage, index) => (
          <div
            key={index}
            className={cn(
              "p-2 rounded text-center font-mono",
              getCellStatusColor(voltage)
            )}
          >
            <div className="text-xs text-muted-foreground">Cell {index + 1}</div>
            <div className="font-bold">{voltage.toFixed(3)}V</div>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
)
```

#### 3.3 Real-time Charts
```tsx
const RealTimeChart = ({ data, dataKey, title, color = "#8884d8" }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(value) => format(new Date(value), 'HH:mm:ss')}
          />
          <YAxis />
          <Tooltip 
            labelFormatter={(value) => format(new Date(value), 'HH:mm:ss')}
          />
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={color} 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </CardContent>
  </Card>
)
```

### Phase 4: Session Management (2-3 weeks)

#### 4.1 Session List View
```tsx
const SessionsPage = () => {
  const { sessions, loading } = useSessions()
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Sessions</h1>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Session
        </Button>
      </div>
      
      <SessionFilters />
      <SessionTable sessions={sessions} loading={loading} />
      <CreateSessionDialog />
    </div>
  )
}

const SessionTable = ({ sessions, loading }) => (
  <Card>
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Session ID</TableHead>
          <TableHead>Battery</TableHead>
          <TableHead>RMA Number</TableHead>
          <TableHead>Serial Number</TableHead>
          <TableHead>Event Type</TableHead>
          <TableHead>Duration</TableHead>
          <TableHead>Runaway Events</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {sessions.map((session) => (
          <SessionRow key={session.id} session={session} />
        ))}
      </TableBody>
    </Table>
  </Card>
)
```

#### 4.2 Session Details View
```tsx
const SessionDetails = ({ sessionId }) => {
  const { session, csvData, analytics } = useSession(sessionId)
  
  return (
    <Tabs defaultValue="overview" className="space-y-6">
      <TabsList>
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="data">Data</TabsTrigger>
        <TabsTrigger value="charts">Charts</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
      </TabsList>
      
      <TabsContent value="overview">
        <SessionOverview session={session} />
      </TabsContent>
      
      <TabsContent value="data">
        <CSVDataTable data={csvData} />
      </TabsContent>
      
      <TabsContent value="charts">
        <SessionCharts data={csvData} />
      </TabsContent>
      
      <TabsContent value="analytics">
        <SessionAnalytics analytics={analytics} />
      </TabsContent>
    </Tabs>
  )
}
```

### Phase 5: Analytics & Visualization (2-3 weeks)

#### 5.1 Analytics Dashboard
```tsx
const AnalyticsDashboard = () => {
  const { analytics, dateRange, setDateRange } = useAnalytics()
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Analytics</h1>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Sessions"
          value={analytics.totalSessions}
          icon={<Database />}
        />
        <StatCard
          title="Runaway Events"
          value={analytics.runawayEvents}
          icon={<AlertTriangle />}
          variant="destructive"
        />
        <StatCard
          title="Avg Session Duration"
          value={formatDuration(analytics.avgDuration)}
          icon={<Clock />}
        />
        <StatCard
          title="Total Logging Time"
          value={formatDuration(analytics.totalTime)}
          icon={<Timer />}
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CellHealthChart data={analytics.cellHealth} />
        <RunawayTimelineChart data={analytics.runawayTimeline} />
        <SessionTypeChart data={analytics.sessionTypes} />
        <VoltageDistributionChart data={analytics.voltageDistribution} />
      </div>
    </div>
  )
}
```

#### 5.2 Advanced Charts
```tsx
const CellHealthChart = ({ data }) => (
  <Card>
    <CardHeader>
      <CardTitle>Cell Health Scores</CardTitle>
    </CardHeader>
    <CardContent>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="cell" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Bar dataKey="healthScore" fill="#8884d8">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getHealthColor(entry.healthScore)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </CardContent>
  </Card>
)
```

### Phase 6: Settings & Configuration (1-2 weeks)

#### 6.1 Settings Page
```tsx
const SettingsPage = () => {
  const { settings, updateSettings } = useSettings()
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      
      <Tabs defaultValue="connection" className="space-y-6">
        <TabsList>
          <TabsTrigger value="connection">Connection</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="display">Display</TabsTrigger>
        </TabsList>
        
        <TabsContent value="connection">
          <ConnectionSettings settings={settings} onUpdate={updateSettings} />
        </TabsContent>
        
        <TabsContent value="monitoring">
          <MonitoringSettings settings={settings} onUpdate={updateSettings} />
        </TabsContent>
        
        <TabsContent value="alerts">
          <AlertSettings settings={settings} onUpdate={updateSettings} />
        </TabsContent>
        
        <TabsContent value="display">
          <DisplaySettings settings={settings} onUpdate={updateSettings} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### Phase 7: Real-time Features & Polish (2-3 weeks)

#### 7.1 WebSocket Integration
```tsx
// Custom hook for real-time data
const useBatteryData = () => {
  const [data, setData] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  
  useEffect(() => {
    const socket = io('/ws/realtime')
    
    socket.on('connect', () => setIsConnected(true))
    socket.on('disconnect', () => setIsConnected(false))
    socket.on('battery_data', (newData) => setData(newData))
    socket.on('runaway_alert', (alert) => {
      toast({
        title: "Cell Runaway Alert",
        description: `Cell ${alert.cell} voltage anomaly detected`,
        variant: "destructive"
      })
    })
    
    return () => socket.disconnect()
  }, [])
  
  return { data, isConnected }
}
```

#### 7.2 Toast Notifications
```tsx
const useRunawayAlerts = () => {
  const { toast } = useToast()
  
  useEffect(() => {
    const socket = io()
    
    socket.on('runaway_alert', (event) => {
      toast({
        title: `${event.severity} Alert`,
        description: `Cell ${event.cell}: ${event.deviation}mV deviation`,
        variant: event.severity === 'Critical' ? 'destructive' : 'default'
      })
    })
    
    return () => socket.disconnect()
  }, [toast])
}
```

## State Management

### Zustand Store Structure
```tsx
// Battery data store
const useBatteryStore = create((set, get) => ({
  data: null,
  isConnected: false,
  connectionSettings: {},
  updateData: (newData) => set({ data: newData }),
  setConnectionStatus: (status) => set({ isConnected: status }),
  connect: async (settings) => {
    // API call to connect
  },
  disconnect: async () => {
    // API call to disconnect
  }
}))

// Session store
const useSessionStore = create((set, get) => ({
  sessions: [],
  currentSession: null,
  filters: {},
  fetchSessions: async () => {
    // API call to fetch sessions
  },
  createSession: async (data) => {
    // API call to create session
  }
}))

// Settings store
const useSettingsStore = create((set, get) => ({
  settings: {},
  fetchSettings: async () => {
    // API call to fetch settings
  },
  updateSettings: async (updates) => {
    // API call to update settings
  }
}))
```

## Responsive Design

### Mobile-First Approach
- **Breakpoints**: Mobile (< 768px), Tablet (768px - 1024px), Desktop (> 1024px)
- **Grid System**: CSS Grid and Flexbox with Tailwind CSS
- **Touch-Friendly**: Larger touch targets, swipe gestures
- **Progressive Enhancement**: Core functionality works without JavaScript

### Component Responsive Patterns
```tsx
// Responsive dashboard grid
const MonitoringDashboard = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
    {/* Cards automatically adjust */}
  </div>
)

// Responsive table with horizontal scroll
const SessionTable = () => (
  <div className="overflow-x-auto">
    <Table className="min-w-full">
      {/* Table content */}
    </Table>
  </div>
)
```

## Testing Strategy

### Unit Testing
```tsx
// Component testing with React Testing Library
describe('CellVoltagesCard', () => {
  test('displays cell voltages correctly', () => {
    const mockData = [3.2, 3.3, 3.1, 3.4, 3.2, 3.3, 3.1, 3.2]
    render(<CellVoltagesCard data={mockData} />)
    
    expect(screen.getByText('Cell 1')).toBeInTheDocument()
    expect(screen.getByText('3.200V')).toBeInTheDocument()
  })
  
  test('applies correct color coding for voltage levels', () => {
    // Test color coding logic
  })
})
```

### Integration Testing
```tsx
// API integration tests
describe('Battery Data API', () => {
  test('fetches real-time data correctly', async () => {
    // Mock API responses
    // Test WebSocket connections
    // Test error handling
  })
})
```

### E2E Testing
```tsx
// Playwright/Cypress tests
describe('Battery Monitoring Workflow', () => {
  test('user can connect, monitor, and create session', () => {
    // Full user workflow testing
  })
})
```

## Deployment Strategy

### Development Environment
```bash
# Frontend development server
npm run dev

# Backend development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Build
```bash
# Build frontend
npm run build

# Serve with Nginx or Apache
# API served with Gunicorn + Uvicorn workers
```

### Docker Deployment
```dockerfile
# Multi-stage Dockerfile
FROM node:18 AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY --from=frontend-builder /app/dist ./static
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security Considerations

### Authentication & Authorization
- **JWT-based authentication** for API access
- **Role-based access control** (Admin, Operator, Viewer)
- **Session timeout** and refresh token rotation

### API Security
- **CORS configuration** for cross-origin requests
- **Rate limiting** to prevent abuse
- **Input validation** with Pydantic models
- **HTTPS only** in production

### Data Security
- **Encrypted data storage** for sensitive configuration
- **Audit logging** for configuration changes
- **Secure WebSocket connections** (WSS)

## Performance Optimization

### Frontend Optimization
- **Code splitting** for route-based chunks
- **Lazy loading** for heavy components
- **Memoization** for expensive calculations
- **Virtual scrolling** for large data tables

### Backend Optimization
- **Database indexing** for session queries
- **Caching** for frequently accessed data
- **Connection pooling** for Modbus connections
- **Compression** for API responses

## Migration Strategy

### From PyQt6 to Web UI
1. **Parallel Development**: Develop web UI alongside existing PyQt6 app
2. **Feature Parity**: Ensure all critical features are implemented
3. **Data Compatibility**: Maintain compatibility with existing CSV/JSON data
4. **User Training**: Provide documentation and training materials
5. **Gradual Rollout**: Optional migration with fallback to PyQt6 app

### Data Migration
- **CSV file compatibility**: Maintain existing CSV format
- **Session metadata**: Convert QSettings sessions to JSON format
- **Configuration migration**: Migrate config.toml to database/API

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1. Setup & Infrastructure | 1-2 weeks | Project setup, shadcn/ui integration |
| 2. Backend API | 2-3 weeks | FastAPI backend, WebSocket support |
| 3. Core UI Components | 3-4 weeks | Real-time monitoring dashboard |
| 4. Session Management | 2-3 weeks | Session CRUD, data viewing |
| 5. Analytics & Visualization | 2-3 weeks | Charts, analytics dashboard |
| 6. Settings & Configuration | 1-2 weeks | Settings management |
| 7. Polish & Real-time Features | 2-3 weeks | WebSocket integration, notifications |

**Total Estimated Duration**: 13-20 weeks (3-5 months)

## Success Criteria

### Functional Requirements
- ✅ Real-time battery monitoring with sub-second updates
- ✅ Complete session management (CRUD operations)
- ✅ CSV data visualization and export
- ✅ Cell runaway detection and alerts
- ✅ Settings management and persistence
- ✅ Responsive design for mobile/tablet access

### Performance Requirements
- ✅ < 100ms WebSocket message latency
- ✅ < 2s initial page load time
- ✅ Support for 100+ concurrent users
- ✅ 24/7 uptime for monitoring operations

### User Experience Requirements
- ✅ Intuitive navigation and workflow
- ✅ Professional, modern UI design
- ✅ Consistent component behavior
- ✅ Clear error messages and feedback
- ✅ Accessibility compliance (WCAG 2.1)

This implementation plan provides a comprehensive roadmap for creating a modern, professional React web UI for the GA Modbus Python Application using shadcn/ui components. The plan focuses on maintaining feature parity with the existing PyQt6 application while providing enhanced user experience and modern web capabilities.