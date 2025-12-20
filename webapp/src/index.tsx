import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import { i18n } from './utils/i18n/i18n'

function main(): void {
  i18n.init('vi')
}

main()

const container = document.getElementById('root') as HTMLElement
const root = createRoot(container)

root.render(
  <StrictMode>
    <App />
  </StrictMode>
)
