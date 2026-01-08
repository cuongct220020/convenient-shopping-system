import { Button } from '../../../components/Button'
import { useState } from 'react'
import { NotificationList } from '../../../components/NotificationList'
import { Bell, Calendar, Info, Plus, Trash } from 'lucide-react'
import { DayPicker, getDefaultClassNames } from 'react-day-picker'
import 'react-day-picker/style.css'
import { Time } from '../../../utils/time'
import MealImage from '../../../assets/meal.png'
import { useNavigate } from 'react-router-dom'

function dayName(index: number) {
  return index === 6 ? 'CN' : `Thứ ${index + 2}`
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
        'flex w-16 flex-col items-center rounded-xl transition',
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
  const navigate = useNavigate()
  return (
    <div className="flex flex-col px-3 py-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <p className="whitespace-nowrap text-xl font-bold text-red-600">
          Kế hoạch bữa ăn
        </p>
        <Button
          icon={Bell}
          variant="danger"
          size="fit"
          onClick={() => setShowNoti(true)}
        />
      </div>
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
      <div className="flex flex-col gap-2 py-4 items-center">
        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
          <img src={MealImage} alt="Meal" className="aspect-square" />
          <div className="flex flex-col justify-between pl-2">
            <p className="font-bold">Bữa sáng</p>
            <div className="flex w-full flex-1 flex-col justify-start text-sm">
              <p>Bánh bao</p>
              <p>Lạp xưởng</p>
              <p>...</p>
            </div>
            <p>
              <span className="font-bold">Calo:</span> 1000
            </p>
          </div>
          <div className="flex flex-1 flex-col items-end justify-center gap-2">
            <Button icon={Trash} variant="primary" size="fit" />
            <Button
              icon={Info}
              variant="secondary"
              size="fit"
              onClick={() => navigate('detail')}
            />
          </div>
        </div>

        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
          <img src={MealImage} alt="Meal" className="aspect-square" />
          <div className="flex flex-col justify-between pl-2">
            <p className="font-bold">Bữa trưa</p>
            <div className="flex w-full flex-1 flex-col justify-start text-sm">
              <p>Bánh bao</p>
              <p>Lạp xưởng</p>
              <p>...</p>
            </div>
            <p>
              <span className="font-bold">Calo:</span> 1000
            </p>
          </div>
          <div className="flex flex-1 flex-col items-end justify-center gap-2">
            <Button icon={Trash} variant="primary" size="fit" />
            <Button
              icon={Info}
              variant="secondary"
              size="fit"
              onClick={() => navigate('detail')}
            />
          </div>
        </div>
        <div className="mx-auto flex w-full max-w-sm rounded-xl bg-gray-200 px-6 py-3">
          <img src={MealImage} alt="Meal" className="aspect-square" />
          <div className="flex flex-col justify-between pl-2">
            <p className="font-bold">Bữa tối</p>
            <div className="flex w-full flex-1 flex-col justify-start text-sm">
              <p>Chưa có món ăn</p>
            </div>
            <p>
              <span className="font-bold">Calo:</span> 1000
            </p>
          </div>
          <div className="flex flex-1 flex-col items-end justify-center gap-2">
            <Button icon={Trash} variant="primary" size="fit" />
            <Button
              icon={Info}
              variant="secondary"
              size="fit"
              onClick={() => navigate('detail')}
            />
          </div>
        </div>
        <Button
          icon={Plus}
          variant="icon"
          size="fit"
          onClick={() => navigate('add')}
        />
      </div>

      {showNoti && <NotificationPopup onClose={() => setShowNoti(false)} />}
    </div>
  )
}
