import { RouterProvider } from 'react-router-dom'
import { router } from './routes/indexX'
import { useWebSocketNotification } from './hooks/useWebSocketNotification'
import { ToastContainer } from './components/Toast'

function AppContent() {
  const { toasts, removeToast } = useWebSocketNotification()

  return (
    <>
      <RouterProvider router={router} />
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </>
  )
}

export default function App() {
  return <AppContent />
}
