import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import UserRoutes from './routes/UserRoutes'
import AdminRoutes from './routes/AdminRoutes'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/admin/ingredient-list" replace />} />
        <Route path="/auth/*" element={<UserRoutes />} />
        <Route path="/admin/*" element={<AdminRoutes />} />
      </Routes>
    </Router>
  )
}
