import { Info, Plus, Trash } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { MealType, mealTypeStr } from '../../../utils/constants'
import { i18n } from '../../../utils/i18n/i18n'
import { Time } from '../../../utils/time'
import Food from '../../../assets/hamburger.png'
import { useNavigate, useParams } from 'react-router-dom'

export function MealDetail() {
  const { id: groupId } = useParams<{ id: string }>()
  const date = new Date() // Real code should retrieve this some other way
  const mealType: MealType = 'breakfast'
  const navigate = useNavigate()

  return (
    <div className="flex flex-col px-3 py-4">
      <div className="flex w-full flex-row">
        <BackButton
          to={`/main/family-group/${groupId}/meal`}
          text="Quay lại"
        ></BackButton>
      </div>

      {/* Header */}
      <p className="whitespace-nowrap pb-4 text-xl font-bold text-gray-600">
        Chi tiết bữa ăn
      </p>
      <div className="flex justify-between">
        <p>{Time.DD_MM_YYYY(date)}</p>
        <p>{i18n.t(mealTypeStr(mealType))}</p>
      </div>

      <div className="flex flex-col items-center gap-3 py-4">
        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
          <div className="aspect-square h-28 overflow-hidden rounded-lg">
            <img src={Food} alt="Meal" className="size-full object-cover" />
          </div>
          <div className="flex flex-col justify-center gap-2 pl-2">
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
              onClick={() =>
                navigate(`/main/family-group/${groupId}/meal/detail`)
              }
            />
            <Button icon={Trash} variant="danger" size="fit" />
          </div>
        </div>

        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
          <div className="aspect-square h-28 overflow-hidden rounded-lg">
            <img src={Food} alt="Meal" className="size-full object-cover" />
          </div>
          <div className="flex flex-col justify-center gap-2 pl-2">
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
              onClick={() =>
                navigate(`/main/family-group/${groupId}/meal/detail`)
              }
            />
            <Button icon={Trash} variant="danger" size="fit" />
          </div>
        </div>

        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-gray-200 px-6 py-3">
          <div className="aspect-square h-28 overflow-hidden rounded-lg">
            <img src={Food} alt="Meal" className="size-full object-cover" />
          </div>
          <div className="flex flex-col justify-center gap-2 pl-2">
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
          onClick={() => navigate(`/main/family-group/${groupId}/meal/add`)}
        />
      </div>
    </div>
  )
}
