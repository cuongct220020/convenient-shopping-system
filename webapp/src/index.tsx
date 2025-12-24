import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import { i18n } from './utils/i18n/i18n'

async function enableMocking() {
  if (import.meta.env.PROD) {
    return
  }
  const { worker } = await import('./mock/browser')
  return worker.start()
}

async function main(): Promise<void> {
  i18n.init('vi')
  await enableMocking()
}

const container = document.getElementById('root') as HTMLElement
const root = createRoot(container)

main().then(() => {
  root.render(
    <StrictMode>
      <App />
    </StrictMode>
  )
})
