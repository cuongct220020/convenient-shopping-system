import { Calendar, Check, Plus } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { FormEvent, useState } from 'react'
import { MealType, MealTypes, mealTypeStr } from '../../../utils/constants'
import { DropdownInputField } from '../../../components/DropDownInputField'
import { i18n } from '../../../utils/i18n/i18n'
import { DayPicker, getDefaultClassNames } from 'react-day-picker'
import { Time } from '../../../utils/time'
import { useParams } from 'react-router-dom'

const calendarClassNames = getDefaultClassNames()

export function AddMeal() {
  const { id: groupId } = useParams<{ id: string }>()
  const [date, setDate] = useState<Date>(new Date())
  const [mealType, setMealType] = useState<MealType>('breakfast')
  const [showDatePicker, setShowDatePicker] = useState(false)

  const onMealTypeChanged = (e: string) => {
    if (!(MealTypes as ReadonlyArray<string>).includes(e)) return
    setMealType(e as MealType)
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    console.log(`API will be called with`, { name, category: mealType })
  }

  return (
    <div className="flex min-h-screen flex-col items-center bg-white p-4 pb-24">
      <div className="flex w-full flex-row">
        <BackButton
          to={`/main/family-group/${groupId}/meal`}
          text="Quay lại"
        ></BackButton>
      </div>
      <p className="pb-4 text-center text-xl font-bold text-red-600">
        Thêm bữa ăn mới
      </p>
      <form className="flex w-full max-w-sm flex-col gap-6" onSubmit={onSubmit}>
        <div className="absolute z-[60] w-fit rounded-lg bg-white">
          <p className="pb-1">Chọn ngày</p>
          <div className="relative">
            <button
              className="flex w-fit gap-3 transition-all duration-200 active:scale-95"
              onClick={() => setShowDatePicker((prev) => !prev)}
            >
              <Calendar />
              <p>{Time.DD_MM_YYYY(date)}</p>
            </button>
            {showDatePicker && (
              <div className="absolute z-[60] w-fit rounded-lg bg-white">
                <DayPicker
                  animate
                  mode="single"
                  selected={date}
                  onSelect={setDate}
                  required
                  classNames={{
                    root: `${calendarClassNames.root} shadow-lg p-2` // Add a shadow to the root element
                  }}
                />
              </div>
            )}
          </div>
        </div>
        <DropdownInputField
          label="Chọn bữa"
          placeholder="Chọn bữa ăn"
          options={MealTypes.map((e) => ({
            value: e,
            label: i18n.t(mealTypeStr(e))
          }))}
          value={mealType}
          onChange={onMealTypeChanged}
          containerClassName="pt-14"
        />

        <div className="flex items-center gap-3">
          <Button icon={Plus} size="fit" variant="icon" />
          <p>Thêm món ăn sẵn</p>
        </div>
        <div className="flex items-center gap-3">
          <Button icon={Plus} size="fit" variant="icon" />
          <p>Thêm công thức nấu</p>
        </div>
        <Button icon={Check} size="fit" variant="primary" type="submit">
          Thêm
        </Button>
      </form>
    </div>
  )
}
