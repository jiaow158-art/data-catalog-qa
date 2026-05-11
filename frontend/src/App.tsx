import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppLayout from './components/Layout'

import DatabasesPage from './pages/DatabasesPage'
import TablesPage from './pages/TablesPage'
import TableDetailPage from './pages/TableDetailPage'
import ColumnDetailPage from './pages/ColumnDetailPage'
import ChatPage from './pages/ChatPage'
import ImportPage from './pages/ImportPage'
import SchedulesPage from './pages/SchedulesPage'
import LineagePage from './pages/LineagePage'
import ReportsPage from './pages/ReportsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>

          <Route path="/" element={<DatabasesPage />} />
          <Route path="/tables" element={<TablesPage />} />
          <Route path="/tables/:id" element={<TableDetailPage />} />
          <Route path="/columns/:id" element={<ColumnDetailPage />} />
          <Route path="/schedules" element={<SchedulesPage />} />
          <Route path="/lineage" element={<LineagePage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/import" element={<ImportPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
