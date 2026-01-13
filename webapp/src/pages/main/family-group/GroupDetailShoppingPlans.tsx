import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, CheckCircle2, Clock, Circle, X } from 'lucide-react'
import { Button } from '../../../components/Button'
import { shoppingPlanService } from '../../../services/shopping-plan'
import type { PlanResponse } from '../../../services/schema/shoppingPlanSchema'

interface GroupDetailShoppingPlansProps {
  groupId: string
  members: Array<{
    id: string
    name: string
  }>
}

const GroupDetailShoppingPlans: React.FC<GroupDetailShoppingPlansProps> = ({
  groupId,
  members
}) => {
  const navigate = useNavigate()

  // Shopping Plans Data
  const [shoppingPlans, setShoppingPlans] = useState<PlanResponse[]>([])
  const [isPlansLoading, setIsPlansLoading] = useState(false)
  const [plansError, setPlansError] = useState<string | null>(null)

  // Fetch shopping plans
  useEffect(() => {
    const fetchShoppingPlans = async () => {
      setIsPlansLoading(true)
      setPlansError(null)

      const result = await shoppingPlanService.filterPlans(groupId, {
        sortBy: 'deadline',
        order: 'asc'
      })

      result.match(
        (response) => {
          setShoppingPlans(response.data)
        },
        (error) => {
          console.error('Failed to fetch shopping plans:', error)
          setPlansError('Không thể tải kế hoạch mua sắm')
        }
      )

      setIsPlansLoading(false)
    }

    fetchShoppingPlans()
  }, [groupId])

  // Helper function to get user name by ID
  const getUserNameById = (userId: string): string => {
    const member = members.find((m) => m.id === userId)
    return member ? member.name : userId
  }

  // Helper to render plan status badge
  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'created':
        return (
          <div className="flex items-center gap-1 rounded-full border border-blue-300 bg-white px-2 py-0.5">
            <Circle size={8} fill="#3B82F6" className="text-blue-500" />
            <span className="text-[10px] font-medium text-blue-500">
              Mới tạo
            </span>
          </div>
        )
      case 'completed':
        return (
          <div className="flex items-center gap-1 rounded-full border border-green-300 bg-white px-2 py-0.5">
            <CheckCircle2 size={12} className="text-green-500" />
            <span className="text-[10px] font-medium text-green-500">
              Đã xong
            </span>
          </div>
        )
      case 'in_progress':
        return (
          <div className="flex items-center gap-1 rounded-full border border-[#C3485C] bg-white px-2 py-0.5">
            <Circle size={8} fill="#C3485C" className="text-[#C3485C]" />
            <span className="text-[10px] font-medium text-[#C3485C]">
              Đang thực hiện
            </span>
          </div>
        )
      case 'cancelled':
        return (
          <div className="flex items-center gap-1 rounded-full border border-gray-300 bg-white px-2 py-0.5">
            <X size={8} className="text-gray-500" />
            <span className="text-[10px] font-medium text-gray-500">
              Đã hủy
            </span>
          </div>
        )
      case 'expired':
        return (
          <div className="flex items-center gap-1 rounded-full border border-red-300 bg-white px-2 py-0.5">
            <Clock size={8} className="text-red-500" />
            <span className="text-[10px] font-medium text-red-500">
              Hết hạn
            </span>
          </div>
        )
      default:
        return null
    }
  }

  const handleCreatePlan = () => {
    navigate(`/main/family-group/${groupId}/add-plan`)
  }

  return (
    <div className="relative flex min-h-[400px] flex-col items-center pb-24 pt-2">
      {/* Plans List */}
      <div className="w-full">
        {isPlansLoading ? (
          <div className="flex justify-center py-8">
            <div className="size-8 animate-spin rounded-full border-b-2 border-[#C3485C]"></div>
          </div>
        ) : plansError ? (
          <div className="px-6 py-8 text-center">
            <p className="text-sm text-red-500">{plansError}</p>
          </div>
        ) : shoppingPlans.length === 0 ? (
          <div className="w-full px-6 py-8 text-center">
            <p className="text-sm leading-relaxed text-gray-800">
              Nhóm chưa có kế hoạch mua sắm nào cả. Hãy tạo kế hoạch mua sắm
              mới!
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {shoppingPlans.map((plan) => (
              <div
                key={plan.plan_id}
                className="cursor-pointer rounded-xl border border-gray-100 bg-white p-4 shadow-sm transition-all hover:shadow-md"
                onClick={() =>
                  navigate(`/main/family-group/${groupId}/plan/${plan.plan_id}`)
                }
              >
                <div className="mb-2 flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-base font-bold text-gray-900">
                      {(plan.others?.name as string) || 'Kế hoạch mua sắm'}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      {getUserNameById(plan.assigner_id)}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      {plan.shopping_list.length} nguyên liệu •
                      {new Date(plan.deadline).toLocaleDateString('vi-VN', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  {renderStatusBadge(plan.plan_status)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Floating Action Button for Create Plan */}
      <div className="mt-4">
        <Button
          variant="primary"
          size="fit"
          icon={Plus}
          onClick={handleCreatePlan}
        >
          Tạo kế hoạch mới
        </Button>
      </div>
    </div>
  )
}

export default GroupDetailShoppingPlans
