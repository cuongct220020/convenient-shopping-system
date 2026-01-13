import { RouterProvider } from 'react-router-dom'
import { router } from './routes/indexX'

export default function App() {
  return <RouterProvider router={router} />
}
