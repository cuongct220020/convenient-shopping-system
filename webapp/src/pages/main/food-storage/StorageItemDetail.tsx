import { Check, Pencil, Trash } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { useState } from 'react'
import { InputField } from '../../../components/InputField'
import { Time } from '../../../utils/time'
import { DropdownInputField } from '../../../components/DropDownInputField'

function ReadonlyTextField({ title, value }: { title: string; value: string }) {
  return (
    <div>
      <p className="pb-1 font-bold">{title}</p>
      <p>{value}</p>
    </div>
  )
}

type MaybeEditingTextFieldProps = {
  isEditing: boolean
  title: string
  placeholder: string
  value: string
}
function MaybeEditingTextField({
  isEditing,
  title,
  value,
  placeholder
}: MaybeEditingTextFieldProps) {
  if (isEditing) {
    return <InputField label={title} placeholder={placeholder} value={value} />
  }
  return <ReadonlyTextField title={title} value={value} />
}

type MaybeEditingDropdownProps = {
  categories: {
    value: string
    label: string
  }[]
  title: string
  value: string
  isEditing: boolean
}
function MaybeEditingDropdown({
  categories,
  isEditing,
  title,
  value
}: MaybeEditingDropdownProps) {
  if (isEditing) {
    return (
      <DropdownInputField label={title} value={value} options={categories} />
    )
  }
  const searchedValue =
    categories.find((e) => e.value === value)?.label ?? value
  return <ReadonlyTextField title={title} value={searchedValue} />
}

export function StorageItemDetail() {
  const [editing, setEditing] = useState(false)

  const exampleInfo = {
    name: 'Sữa tươi',
    amount: '100ml',
    expirationDate: new Date(2040, 4, 13),
    category: 'butter',
    conservationMethod:
      'Bảo quản tốt nhất với muối tinh. Bỏ vào một chai muốn và cất trong tủ lạnh 5 tiếng mỗi ngày để đạt chất lượng tốt nhất.'
  }

  const onEditingDone = () => {
    setEditing(false)
    console.log('Editing done')
  }

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
      <BackButton
        to="/main/food/storage/items"
        text="Quay lại"
        className="mb-4"
      />{' '}
      <div className="flex items-center justify-center pb-8">
        {editing ? (
          <div className="mr-2 flex-1">
            <InputField
              placeholder="Nhập tên thực phẩm"
              value={exampleInfo.name}
            />
          </div>
        ) : (
          <h1 className="flex-1 text-2xl font-bold">{exampleInfo.name}</h1>
        )}
        <div className="flex gap-2">
          {editing ? (
            <Button
              icon={Check}
              type="button"
              variant="primary"
              onClick={onEditingDone}
            />
          ) : (
            <>
              <Button icon={Trash} type="button" variant="secondary" />
              <Button
                icon={Pencil}
                type="button"
                variant="primary"
                onClick={() => setEditing(true)}
              />
            </>
          )}
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-3">
        <MaybeEditingTextField
          isEditing={editing}
          title="Số lượng"
          placeholder="100g"
          value={exampleInfo.amount}
        />
        <MaybeEditingTextField
          isEditing={editing}
          title="Ngày hết hạn"
          placeholder="20/15/2025"
          value={Time.DD_MM_YYYY(exampleInfo.expirationDate)}
        />
        <MaybeEditingDropdown
          isEditing={editing}
          title="Phân loại"
          categories={exampleItemCategories}
          value={exampleInfo.category}
        />
        <MaybeEditingTextField
          isEditing={editing}
          title="Cách bảo quản đề xuất"
          placeholder="Hướng dẫn cách bảo quản thực phẩm ở đây"
          value={exampleInfo.conservationMethod}
        />
      </div>
    </div>
  )
}
