import { Calendar, Check, Info, Plus, Trash } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { FormEvent, useState } from 'react'
import { MealType, MealTypes, mealTypeStr } from '../../../utils/constants'
import { DropdownInputField } from '../../../components/DropDownInputField'
import { i18n } from '../../../utils/i18n/i18n'
import { DayPicker, getDefaultClassNames } from 'react-day-picker'
import { Time } from '../../../utils/time'
import Food from '../../../assets/hamburger.png'
import { useNavigate } from 'react-router-dom'

type MealDetailProps = {
  date: Date
}
export function MealDetail() {
  const date = new Date() // Real code should retrieve this some other way
  const mealType: MealType = 'breakfast'
  const navigate = useNavigate()

  return (
    <div className="flex flex-col px-3 py-4">
      <div className="flex w-full flex-row">
        <BackButton to="../" text="Quay lại"></BackButton>
      </div>

      {/* Header */}
      <p className="text-black-600 whitespace-nowrap pb-4 text-xl font-bold">
        Chi tiết bữa ăn
      </p>
      <div className="flex justify-between">
        <p>{Time.DD_MM_YYYY(date)}</p>
        <p>{i18n.t(mealTypeStr(mealType))}</p>
      </div>

      <div className="flex flex-col gap-3 items-center py-4">
        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
          <div className="aspect-square h-28 overflow-hidden rounded-lg">
            <img src={Food} alt="Meal" className="size-full object-cover" />
          </div>
          <div className="flex flex-col pl-2 gap-2 justify-center">
            <p className="font-bold">Hamburger</p>
            <p>
              <span className="font-bold">Calo:</span> 1000
            </p>
            <p className="text-green-500">Đủ nguyên liệu</p>
          </div>
          <div className="flex flex-1 flex-col items-end justify-center gap-2">
            <Button
              icon={Info}
              variant="icon"
              size="fit"
              onClick={() => navigate('detail')}
            />
            <Button icon={Trash} variant="danger" size="fit" />
          </div>
        </div>

        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
          <div className="aspect-square h-28 overflow-hidden rounded-lg">
            <img src={Food} alt="Meal" className="size-full object-cover" />
          </div>
          <div className="flex flex-col pl-2 gap-2 justify-center">
            <p className="font-bold">Thịt bò rán</p>
            <p>
              <span className="font-bold">Calo:</span> 250
            </p>
            <p className="text-red-500">Thiếu nguyên liệu</p>
          </div>
          <div className="flex flex-1 flex-col items-end justify-center gap-2">
            <Button
              icon={Info}
              variant="icon"
              size="fit"
              onClick={() => navigate('detail')}
            />
            <Button icon={Trash} variant="danger" size="fit" />
          </div>
        </div>

        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-gray-200 px-6 py-3">
          <div className="aspect-square h-28 overflow-hidden rounded-lg">
            <img src={Food} alt="Meal" className="size-full object-cover" />
          </div>
          <div className="flex flex-col pl-2 gap-2 justify-center">
            <p className="font-bold">Nem chua luộc bí</p>
            <p>Món ăn sẵn</p>
          </div>
          <div className="flex flex-1 flex-col items-end justify-center gap-2">
            {/* <Button
              icon={Info}
              variant="icon"
              size="fit"
              onClick={() => navigate('detail')}
            /> */}
            <Button icon={Trash} variant="danger" size="fit" />
          </div>
        </div>
        <Button
          icon={Plus}
          variant="icon"
          size="fit"
          onClick={() => navigate('add')}
        />
      </div>
    </div>
  )
}
