import { Check } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { InputField } from '../../../components/InputField'
import { DropdownInputField } from '../../../components/DropDownInputField'

export function AddStorageItem() {
  const exampleItemCategories = [
    {
      value: 'ingredients',
      label: 'Gia vị'
    },
    {
      value: 'vegetables',
      label: 'Rau củ'
    },
    {
      value: 'butter',
      label: 'Bơ'
    }
  ]

  return (
    <div className="flex flex-col p-4">
      <BackButton to="../" text="Quay lại" className="mb-4" />{' '}
      <form className="flex flex-1 flex-col gap-3">
        <InputField
          label="Tên thực phẩm"
          placeholder="Nhập tên thực phẩm"
          value="Sữa dê"
        />
        <InputField label="Số lượng" placeholder="100g" value="200g" />
        <InputField
          label="Ngày hết hạn"
          placeholder="20/15/2025"
          value="23/12/2024"
        />
        <DropdownInputField
          label="Phân loại"
          options={exampleItemCategories}
          value={'butter'}
        />
        <InputField
          label="Cách bảo quản đề xuất"
          placeholder="Hướng dẫn cách bảo quản thực phẩm ở đây"
          value={'Tự viết đi haha'}
        />
        <Button icon={Check} type="submit" size="fit" onClick={() => {}}>
          Thêm
        </Button>
      </form>
    </div>
  )
}
