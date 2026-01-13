import { Button } from '../../../components/Button'
import { useState, useEffect } from 'react'
import { NotificationList } from '../../../components/NotificationList'
import { Calendar, Info, Trash } from 'lucide-react'
import { DayPicker, getDefaultClassNames } from 'react-day-picker'
import 'react-day-picker/style.css'
import { Time } from '../../../utils/time'
import MealImage from '../../../assets/meal.png'
import { useNavigate, useParams } from 'react-router-dom'
import { mealService } from '../../../services/meal'
import { LoadingOverlay } from '../../../components/Loading'
import type { Meal } from '../../../services/schema/mealSchema'

function dayName(index: number) {
  return index === 6 ? 'CN' : `Thứ ${index + 2}`
}

function mealTypeLabel(mealType: string): string {
  const labels: Record<string, string> = {
    breakfast: 'Bữa sáng',
    lunch: 'Bữa trưa',
    dinner: 'Bữa tối'
  }
  return labels[mealType] || mealType
}

type DateThumbnailProps = {
  dayLabel: string
  date: number
  isToday?: boolean
  isSelected?: boolean
  onClick?: () => void
}

function DateThumbnail({
  dayLabel,
  date,
  isToday,
  isSelected,
  onClick
}: DateThumbnailProps) {
  return (
    <button
      onClick={onClick}
      className={[
        'flex w-11 flex-col items-center rounded-xl transition',
        'p-2 gap-1',
        isSelected && 'bg-red-500 shadow-sm'
      ].join(' ')}
    >
      <span
        className={[
          'text-sm font-medium leading-none text-nowrap',
          isSelected ? 'text-white' : 'invisible'
        ].join(' ')}
      >
        {dayLabel}
      </span>

      <div
        className={[
          'flex h-8 w-8 items-center justify-center rounded-full',
          'text-lg font-semibold',
          isToday || isSelected
            ? 'bg-yellow-100 text-red-500'
            : 'bg-gray-100 text-black'
        ].join(' ')}
      >
        {date}
      </div>
    </button>
  )
}

const calendarClassNames = getDefaultClassNames()
type NotificationPopupProps = {
  onClose?: () => unknown
}
function NotificationPopup({ onClose }: NotificationPopupProps) {
  const [noti, setNoti] = useState([
    {
      title: 'notif 1',
      timestamp: '2h truoc',
      content: 'lorem ipsum 12312313213 sdfljsldf',
      id: 1
    },
    {
      title: 'fff notif 1',
      timestamp: 'f2h truoc',
      content: 'lorem ipsum 12312313213 sdfljsldf',
      id: 2
    },
    {
      title: 'notif f 1',
      timestamp: '2h tfdruoc',
      content: 'lorem ipsum 12312313213 sdfljsldf',
      id: 3
    }
  ])
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <NotificationList
        notifications={noti}
        onClose={onClose}
        onDelete={(id) => setNoti((prev) => prev.filter((e) => e.id !== id))}
      />
    </div>
  )
}

function getWeekDates(d: Date) {
  // mon -> sun: 0 -> 6
  const day = (d.getDay() + 6) % 7
  const monday = new Date(d)
  monday.setHours(0, 0, 0, 0)
  monday.setDate(d.getDate() - day)
  const week: Date[] = []
  for (let i = 0; i < 7; i++) {
    const dt = new Date(monday)
    dt.setDate(monday.getDate() + i)
    week.push(dt)
  }
  return week
}

export function Meal() {
  const [showNoti, setShowNoti] = useState(false)
  const [date, setDate] = useState(new Date(Date.now()))
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [meals, setMeals] = useState<Meal[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { id: groupId } = useParams<{ id: string }>()
  useEffect(() => {
    setLoading(true)
    mealService.getMealsByGroupAndDate(groupId!, date).then((result) => {
      result.match(
        (mealsData) => {
          setMeals(mealsData)
          setLoading(false)
        },
        (error) => {
          console.error('Failed to fetch meals:', error)
          setLoading(false)
        }
      )
    })
  }, [groupId, date])
  return (
    <div className="flex flex-col px-3 py-4">
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
      <div className="no-scrollbar flex gap-2 overflow-x-auto py-2">
        {getWeekDates(date).map((d, i) => {
          return (
            <DateThumbnail
              key={d.toISOString()}
              dayLabel={dayName(i)}
              date={d.getDate()}
              isSelected={Time.isSameDay(d, date)}
              isToday={Time.isSameDay(d, new Date())}
              onClick={() => setDate(d)}
            />
          )
        })}
      </div>

      <LoadingOverlay isLoading={loading}>
        <div className="mt-4 flex w-full flex-col gap-4">
          {meals.length === 0 ? (
            <p className="text-gray-500">Chưa có bữa ăn nào cho ngày này</p>
          ) : (
            meals.map((meal) => {
              const isPlanned = 'recipe_list' in meal
              return (
                <div
                  key={meal.meal_type}
                  className={`mx-auto flex w-full max-w-sm rounded-xl px-6 py-3 ${
                    isPlanned ? 'bg-yellow-100' : 'bg-gray-200'
                  }`}
                >
                  <img src={MealImage} alt="Meal" className="aspect-square" />
                  <div className="flex flex-col justify-between pl-2">
                    <p className="font-bold">{mealTypeLabel(meal.meal_type)}</p>
                    <div className="flex w-full flex-1 flex-col justify-start text-sm">
                      {'recipe_list' in meal ? (
                        meal.recipe_list.length > 0 ? (
                          meal.recipe_list.map((recipe) => (
                            <p key={recipe.recipe_id}>{recipe.recipe_name}</p>
                          ))
                        ) : (
                          <p>Chưa có công thức</p>
                        )
                      ) : (
                        <p>Chưa có món ăn</p>
                      )}
                    </div>
                    {isPlanned && (
                      <p>
                        <span className="font-bold">Calo:</span> 1000
                      </p>
                    )}
                  </div>
                  <div className="flex flex-1 flex-col items-end justify-center gap-2">
                    <Button icon={Trash} variant="primary" size="fit" />
                    <Button
                      icon={Info}
                      variant="secondary"
                      size="fit"
                      onClick={() =>
                        navigate(`/main/family-group/${groupId}/meal/detail`)
                      }
                    />
                  </div>
                </div>
              )
            })
          )}
        </div>
      </LoadingOverlay>
      {showNoti && <NotificationPopup onClose={() => setShowNoti(false)} />}
    </div>
  )
}
