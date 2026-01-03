import { Button } from '../../../components/Button'
import { useState } from 'react'
import { NotificationList } from '../../../components/NotificationList'
import { Time } from '../../../utils/time'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.min.css'
import { Bell, Calendar } from 'lucide-react'

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

export function Meal() {
  const [showNoti, setShowNoti] = useState(false)
  const today = new Date(Date.now())
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

      <div className="flex">
        <DatePicker
          selected={today}
          onChange={() => {}}
          showIcon
          dropdownMode="select"
        />
      </div>

      {showNoti && <NotificationPopup onClose={() => setShowNoti(false)} />}
    </div>
  )
}
