import { Plus } from 'lucide-react'
import { Button } from '../../../components/Button'

export function Storage() {
  return (
    <div className="flex flex-col">
      <div className="flex flex-row items-center justify-between">
        <p>Kho thực phẩm</p>
        <Button icon={Plus} type="button" size="fit" variant="primary"></Button>
      </div>
      <div className="grid">
        <p>123</p>
        <p>123</p>
        <p>123</p>
        <p>123</p>
        <p>123</p>
        <p>123</p>
        <p>123</p>
      </div>
    </div>
  )
}
