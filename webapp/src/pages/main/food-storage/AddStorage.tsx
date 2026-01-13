import { Check, Loader2 } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { InputField } from '../../../components/InputField'
import { FormEvent, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FoodStorageCategories,
  FoodStorageCategory,
  foodStorageCategoryStr
} from '../../../utils/constants'
import { DropdownInputField } from '../../../components/DropDownInputField'
import { i18n } from '../../../utils/i18n/i18n'
import { err, ok, Result } from 'neverthrow'
import { i18nKeys } from '../../../utils/i18n/keys'
import { storageService } from '../../../services/storage'
import { groupService } from '../../../services/group'

function validateName(name: string): Result<void, i18nKeys> {
  if (!name.trim()) return err('empty_storage_name')
  if (name.trim().length < 3) {
    return err('invalid_storage_name')
  }
  return ok()
}

export function AddStorage() {
  const navigate = useNavigate()
  const [nameTouched, setNameTouched] = useState(false)
  const [name, setName] = useState('')
  const [nameError, setNameError] = useState<Result<void, i18nKeys>>(ok())
  const [category, setCategory] = useState<FoodStorageCategory>('fridge')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [groupId, setGroupId] = useState<string | null>(null)

  // Get current user's default group on mount
  useEffect(() => {
    groupService.getGroups().match(
      (response) => {
        // Get the first group from user's groups
        if (response.data.groups && response.data.groups.length > 0) {
          setGroupId(response.data.groups[0].id)
        }
      },
      (err) => {
        console.error('Failed to get groups:', err)
      }
    )
  }, [])

  const onNameBlur = () => {
    setNameTouched(true)
    setNameError(validateName(name))
  }

  const onNameChanged = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value)
    if (nameTouched) {
      setNameError(validateName(e.target.value))
    }
  }

  const onCategoryChanged = (e: string) => {
    if (!(FoodStorageCategories as ReadonlyArray<string>).includes(e)) return
    setCategory(e as FoodStorageCategory)
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()

    const nameErr = validateName(name)
    setNameTouched(true)
    setNameError(nameErr)
    if (nameErr.isErr()) return

    if (!groupId) {
      console.error('No group ID available')
      return
    }

    setIsSubmitting(true)

    storageService
      .createStorage(name.trim(), category, groupId)
      .match(
        () => {
          setIsSubmitting(false)
          navigate('../')
        },
        (err) => {
          console.error('Failed to create storage:', err)
          setIsSubmitting(false)
          // TODO: Show error message to user
        }
      )
  }

  return (
    <div className="flex min-h-screen flex-col items-center bg-white p-4 pb-24">
      <div className="flex w-full flex-row">
        <BackButton to="../" text="Quay lại"></BackButton>
      </div>
      <p className="pb-4 text-center text-xl font-bold text-red-600">
        Thêm kho thực phẩm mới
      </p>
      <form className="flex w-full max-w-sm flex-col gap-6" onSubmit={onSubmit}>
        <InputField
          label="Tên kho"
          placeholder="Tủ lạnh 4 cánh"
          onBlur={onNameBlur}
          onChange={onNameChanged}
          error={nameError.isErr() ? i18n.t(nameError.error) : null}
        ></InputField>
        <DropdownInputField
          label="Loại kho"
          placeholder="Chọn loại kho"
          options={FoodStorageCategories.map((e) => ({
            value: e,
            label: i18n.t(foodStorageCategoryStr(e))
          }))}
          value={category}
          onChange={onCategoryChanged}
        />
        <Button
          icon={isSubmitting ? Loader2 : Check}
          size="fit"
          variant={isSubmitting ? 'disabled' : 'primary'}
          type="submit"
        >
          {isSubmitting ? 'Đang thêm...' : 'Thêm'}
        </Button>
      </form>
    </div>
  )
}
