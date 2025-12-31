import { Check } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { InputField } from '../../../components/InputField'
import { useState } from 'react'

export function AddStorage() {
  const [name, setName] = useState('')
  return (
    <div className="flex min-h-screen flex-col items-center bg-white p-4 pb-24">
      <div className="flex w-full flex-row">
        <BackButton to="../" text="Quay lại"></BackButton>
      </div>
      <p className="pb-4 text-center text-xl font-bold text-red-600">
        Thêm kho thực phẩm mới
      </p>
      <form className="flex w-full max-w-sm flex-col gap-6">
        <InputField label="Loại kho" placeholder="Tủ lạnh"></InputField>
        <InputField label="Tên kho" placeholder="Tủ lạnh 4 cánh"></InputField>
        <Button icon={Check} size="fit" variant="primary">
          Thêm
        </Button>
      </form>
    </div>
  )
}
