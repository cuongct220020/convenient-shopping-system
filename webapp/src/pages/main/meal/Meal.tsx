import { Button } from '../../../components/Button'
import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { NotificationList } from '../../../components/NotificationList'
import { Calendar, Trash, Settings, ChevronDown, ChevronUp, X, Loader2, Search, Save, RotateCcw, Check } from 'lucide-react'
import { DayPicker, getDefaultClassNames } from 'react-day-picker'
import 'react-day-picker/style.css'
import { Time } from '../../../utils/time'
import BreakfastImage from '../../../assets/breakfast.png'
import LunchImage from '../../../assets/lunch.png'
import DinnerImage from '../../../assets/dinner.png'
import { useNavigate, useParams, useLocation, useSearchParams } from 'react-router-dom'
import { groupService } from '../../../services/group'
import { GroupHeader } from '../../../components/GroupHeader'
import { i18n } from '../../../utils/i18n/i18n'
import { mealTypeStr } from '../../../utils/constants'
import {
  mealService,
  type MealMissingResponse,
  type MealRecipe,
  type MealResponse,
  type MealType3,
  type DailyMealAction,
  type DailyMealsCommand
} from '../../../services/meal'
import { recipeService, type FlattenedIngredientsResponse } from '../../../services/recipe'

// Helper function to get display name from user
function getDisplayName(user: { first_name?: string | null; last_name?: string | null; username?: string } | null): string {
  if (!user) return 'Người dùng'
  if (user.first_name && user.last_name) {
    return `${user.last_name} ${user.first_name}`
  }
  if (user.first_name) return user.first_name
  if (user.last_name) return user.last_name
  return user.username || 'Người dùng'
}

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

type MealTabType = 'members' | 'shopping-plan' | 'storage' | 'meal'

const MEAL_TYPES_3: MealType3[] = ['breakfast', 'lunch', 'dinner']
const MEAL_IMAGES: Record<MealType3, string> = {
  breakfast: BreakfastImage,
  lunch: LunchImage,
  dinner: DinnerImage
}

function toISODateLocal(d: Date): string {
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

// LocalStorage utilities for draft payload
type DraftMealPayload = {
  date: string
  groupId: string
  meals: {
    breakfast?: { action: 'delete' | 'upsert'; recipes?: MealRecipe[] }
    lunch?: { action: 'delete' | 'upsert'; recipes?: MealRecipe[] }
    dinner?: { action: 'delete' | 'upsert'; recipes?: MealRecipe[] }
  }
}

function getDraftKey(groupId: string, date: string): string {
  return `meal_draft_${groupId}_${date}`
}

function saveDraftPayload(groupId: string, date: string, payload: DraftMealPayload): void {
  try {
    const key = getDraftKey(groupId, date)
    localStorage.setItem(key, JSON.stringify(payload))
  } catch (err) {
    console.error('Failed to save draft payload:', err)
  }
}

function loadDraftPayload(groupId: string, date: string): DraftMealPayload | null {
  try {
    const key = getDraftKey(groupId, date)
    const data = localStorage.getItem(key)
    if (!data) return null
    return JSON.parse(data) as DraftMealPayload
  } catch (err) {
    console.error('Failed to load draft payload:', err)
    return null
  }
}

function clearDraftPayload(groupId: string, date: string): void {
  try {
    const key = getDraftKey(groupId, date)
    localStorage.removeItem(key)
  } catch (err) {
    console.error('Failed to clear draft payload:', err)
  }
}

function isMealResponse(x: MealResponse | MealMissingResponse): x is MealResponse {
  return (x as MealResponse).meal_id !== undefined
}

type MealSlot = {
  mealType: MealType3
  mealId?: number
  mealStatus?: string
  recipes: MealRecipe[]
  action: DailyMealAction
  dirty: boolean
}

function emptyMealSlot(mealType: MealType3): MealSlot {
  return { mealType, recipes: [], action: 'skip', dirty: false }
}

function normalizeDailyMeals(items: Array<MealResponse | MealMissingResponse>): Record<MealType3, MealSlot> {
  const out: Record<MealType3, MealSlot> = {
    breakfast: emptyMealSlot('breakfast'),
    lunch: emptyMealSlot('lunch'),
    dinner: emptyMealSlot('dinner')
  }

  for (const item of items) {
    const t = item.meal_type
    if (!MEAL_TYPES_3.includes(t)) continue

    if (isMealResponse(item)) {
      out[t] = {
        mealType: t,
        mealId: item.meal_id,
        mealStatus: item.meal_status,
        recipes: item.recipe_list ?? [],
        action: 'skip',
        dirty: false
      }
    } else {
      out[t] = {
        mealType: t,
        recipes: [],
        action: 'skip',
        dirty: false
      }
    }
  }

  return out
}

export function Meal() {
  const { id: groupId } = useParams<{ id: string }>()
  const location = useLocation()
  const [searchParams, setSearchParams] = useSearchParams()
  const [showNoti, setShowNoti] = useState(false)
  const [date, setDate] = useState(new Date(Date.now()))
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [activeTab, setActiveTab] = useState<MealTabType>('meal')
  const prevDateRef = useRef<Date>(new Date(Date.now()))
  const prevActiveTabRef = useRef<MealTabType>('meal')

  const [dailyMeals, setDailyMeals] = useState<Record<MealType3, MealSlot>>({
    breakfast: emptyMealSlot('breakfast'),
    lunch: emptyMealSlot('lunch'),
    dinner: emptyMealSlot('dinner')
  })

  // Store original state for undo functionality
  const [originalDailyMeals, setOriginalDailyMeals] = useState<Record<MealType3, MealSlot> | null>(null)

  const setMealSlot = useCallback(
    (mealType: MealType3, updater: (prev: MealSlot) => MealSlot) => {
      setDailyMeals((prev) => ({
        ...prev,
        [mealType]: updater(prev[mealType])
      }))
    },
    []
  )

  const [expandedMealType, setExpandedMealType] = useState<MealType3 | null>(null)
  const [mealsLoading, setMealsLoading] = useState(false)
  const [mealsError, setMealsError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [transitioningMealType, setTransitioningMealType] = useState<MealType3 | null>(null)

  const [pendingAdd, setPendingAdd] = useState<null | {
    date: string
    mealType: MealType3
    items: Array<{
      recipe: { id: number; name: string; default_servings?: number }
      servings: number
    }>
  }>(null)

  const [flattenedModal, setFlattenedModal] = useState<{
    open: boolean
    title: string
    loading: boolean
    error: string | null
    data: FlattenedIngredientsResponse | null
  }>({
    open: false,
    title: '',
    loading: false,
    error: null,
    data: null
  })

  const [groupData, setGroupData] = useState<{
    id: string
    name: string
    avatarUrl: string | null
    memberCount: number
    adminName: string
  } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  // Initialize date from query param (?date=YYYY-MM-DD) if provided
  useEffect(() => {
    const d = searchParams.get('date')
    if (!d) {
      // If no date in URL, set current date in URL
      const currentDate = toISODateLocal(new Date())
      setSearchParams({ date: currentDate }, { replace: true })
      return
    }
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d)
    if (!m) return
    const yyyy = Number(m[1])
    const mm = Number(m[2])
    const dd = Number(m[3])
    const dt = new Date(yyyy, mm - 1, dd)
    if (!isNaN(dt.getTime()) && !Time.isSameDay(dt, date)) {
      setDate(dt)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  // Fetch group data - use state from navigation if available
  useEffect(() => {
    const fetchGroupData = async () => {
      if (!groupId) return

      // Check if groupData was passed via navigation state
      const stateGroupData = (location.state as { groupData?: typeof groupData })?.groupData
      if (stateGroupData) {
        setGroupData(stateGroupData)
        setIsLoading(false)
        return
      }

      // Otherwise, fetch from API
      setIsLoading(true)
      const membersResult = await groupService.getGroupMembers(groupId)

      membersResult.match(
        (response) => {
          const group = response.data
          const memberships = group.members || group.group_memberships || []

          setGroupData({
            id: group.id,
            name: group.group_name,
            avatarUrl: group.group_avatar_url,
            memberCount: memberships.length,
            adminName: getDisplayName(group.creator)
          })
        },
        (err) => {
          console.error('Failed to fetch group:', err)
        }
      )

      setIsLoading(false)
    }

    fetchGroupData()
  }, [groupId, location.state])

  // Accept add-to-meal result from SelectRecipe page
  useEffect(() => {
    const st = location.state as any
    if (!st?.addToMeal) return

    const payload = st.addToMeal as {
      date: string
      mealType: MealType3
      items: Array<{
        recipe: { id: number; name: string; default_servings?: number }
        servings: number
      }>
    }

    // If date matches current date and meals are already loaded, apply immediately
    const mealDate = toISODateLocal(date)
    if (mealDate === payload.date && !mealsLoading) {
      setMealSlot(payload.mealType, (prev) => {
        const byId = new Map<number, MealRecipe>(prev.recipes.map((r) => [r.recipe_id, r]))

        for (const it of payload.items) {
          const safeServings = Math.max(1, Math.floor(it.servings || it.recipe.default_servings || 1))
          const existing = byId.get(it.recipe.id)
          if (existing) {
            byId.set(it.recipe.id, { ...existing, servings: safeServings })
          } else {
            byId.set(it.recipe.id, {
              recipe_id: it.recipe.id,
              recipe_name: it.recipe.name,
              servings: safeServings
            })
          }
        }

        const nextRecipes = Array.from(byId.values())

        return {
          ...prev,
          recipes: nextRecipes,
          action: 'upsert',
          dirty: true
        }
      })
      setExpandedMealType(payload.mealType)
    } else {
      // Otherwise, set as pending to apply after meals load
      setPendingAdd(payload)
      // If date is different, change date first
      if (mealDate !== payload.date) {
        const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(payload.date)
        if (m) setDate(new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])))
      }
    }

    // Clear one-time state to prevent re-applying when navigating back/forward
    navigate(location.pathname + location.search, {
      replace: true,
      state: st?.groupData ? { groupData: st.groupData } : null
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, date, mealsLoading, setMealSlot])

  // Apply draft payload when returning from SelectRecipe (without addToMeal)
  useEffect(() => {
    if (!groupId || activeTab !== 'meal' || mealsLoading) return
    const st = location.state as any
    // Only apply if returning from SelectRecipe (has groupData but no addToMeal)
    if (st?.groupData && !st?.addToMeal) {
      const mealDate = toISODateLocal(date)
      const draft = loadDraftPayload(groupId, mealDate)
      if (draft) {
        setDailyMeals((prev) => {
          const updated: Record<MealType3, MealSlot> = { ...prev }
          for (const mealType of MEAL_TYPES_3) {
            const draftMeal = draft.meals[mealType]
            if (!draftMeal) continue

            if (draftMeal.action === 'delete') {
              updated[mealType] = {
                ...prev[mealType],
                recipes: [],
                action: 'delete',
                dirty: true
              }
            } else if (draftMeal.action === 'upsert' && draftMeal.recipes) {
              updated[mealType] = {
                ...prev[mealType],
                recipes: draftMeal.recipes,
                action: 'upsert',
                dirty: true
              }
            }
          }
          return updated
        })
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, groupId, date, activeTab, mealsLoading])

  // Fetch daily meals for selected date (breakfast/lunch/dinner)
  useEffect(() => {
    if (!groupId || activeTab !== 'meal') return

    const fetchMeals = async () => {
      setMealsLoading(true)
      setMealsError(null)
      const mealDate = toISODateLocal(date)

      const result = await mealService.getDailyMeals({ mealDate, groupId })
      result.match(
        (items) => {
          const normalized = normalizeDailyMeals(items)
          setOriginalDailyMeals(normalized) // Store original state

          // Apply draft payload if exists
          const draft = loadDraftPayload(groupId, mealDate)
          if (draft) {
            const updated: Record<MealType3, MealSlot> = { ...normalized }
            for (const mealType of MEAL_TYPES_3) {
              const draftMeal = draft.meals[mealType]
              if (!draftMeal) continue

              if (draftMeal.action === 'delete') {
                updated[mealType] = {
                  ...normalized[mealType],
                  recipes: [],
                  action: 'delete',
                  dirty: true
                }
              } else if (draftMeal.action === 'upsert' && draftMeal.recipes) {
                updated[mealType] = {
                  ...normalized[mealType],
                  recipes: draftMeal.recipes,
                  action: 'upsert',
                  dirty: true
                }
              }
            }
            setDailyMeals(updated)
          } else {
            setDailyMeals(normalized)
          }

          setMealsLoading(false)
        },
        (err) => {
          console.error('Failed to fetch meals:', err)
          setMealsError('Không thể tải bữa ăn trong ngày')
          setMealsLoading(false)
        }
      )
    }

    fetchMeals()
  }, [groupId, date, activeTab])

  // Apply pending recipe add after daily meals are loaded (avoid overwriting by fetch)
  useEffect(() => {
    if (!pendingAdd) return
    if (mealsLoading) return
    if (toISODateLocal(date) !== pendingAdd.date) {
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(pendingAdd.date)
      if (m) setDate(new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])))
      return
    }

    setMealSlot(pendingAdd.mealType, (prev) => {
      const byId = new Map<number, MealRecipe>(prev.recipes.map((r) => [r.recipe_id, r]))

      for (const it of pendingAdd.items) {
        const safeServings = Math.max(1, Math.floor(it.servings || it.recipe.default_servings || 1))
        const existing = byId.get(it.recipe.id)
        if (existing) {
          byId.set(it.recipe.id, { ...existing, servings: safeServings })
        } else {
          byId.set(it.recipe.id, {
            recipe_id: it.recipe.id,
            recipe_name: it.recipe.name,
            servings: safeServings
          })
        }
      }

      const nextRecipes = Array.from(byId.values())

      return {
        ...prev,
        recipes: nextRecipes,
        action: 'upsert',
        dirty: true
      }
    })

    setExpandedMealType(pendingAdd.mealType)
    setPendingAdd(null)
  }, [pendingAdd, mealsLoading, date, setMealSlot])

  const handleBack = useCallback(() => {
    if (!groupId || !groupData) return
    navigate(`/main/family-group/${groupId}`, {
      state: {
        groupData: {
          id: groupData.id,
          name: groupData.name,
          avatarUrl: groupData.avatarUrl,
          memberCount: groupData.memberCount,
          adminName: groupData.adminName
        },
        activeTab: 'members' // Default to members tab when going back
      }
    })
  }, [navigate, groupId, groupData])

  const settingsButton = useMemo(
    () => (
      <button
        onClick={(e) => {
          e.stopPropagation()
          // TODO: Add settings functionality if needed
        }}
        className="p-2"
      >
        <Settings size={24} className="text-gray-700" />
      </button>
    ),
    []
  )

  // Check if there are actual unsaved changes (draft payload exists and is not empty)
  // Build draft payload from current dailyMeals state
  const buildDraftPayload = useCallback(
    (meals: Record<MealType3, MealSlot>, groupId: string, date: string): DraftMealPayload | null => {
      const hasChanges = MEAL_TYPES_3.some((t) => meals[t].dirty)
      if (!hasChanges) return null

      const draft: DraftMealPayload = {
        date,
        groupId,
        meals: {}
      }

      for (const mealType of MEAL_TYPES_3) {
        const slot = meals[mealType]
        if (!slot.dirty) continue

        if (slot.action === 'delete' || slot.recipes.length === 0) {
          // If meal doesn't exist on server (no mealId), skip adding to draft payload
          // because there's nothing to delete on the server - treat as no change needed
          if (!slot.mealId) {
            // Don't add to draft payload - meal doesn't exist, so no change needed
            continue
          } else {
            draft.meals[mealType] = { action: 'delete' }
          }
        } else {
          draft.meals[mealType] = { action: 'upsert', recipes: slot.recipes }
        }
      }

      return Object.keys(draft.meals).length > 0 ? draft : null
    },
    []
  )

  // Check if there are actual unsaved changes (draft payload exists and is not empty)
  const hasUnsavedChanges = useMemo(() => {
    if (!groupId || activeTab !== 'meal') return false
    const mealDate = toISODateLocal(date)
    const draft = buildDraftPayload(dailyMeals, groupId, mealDate)
    return draft !== null && Object.keys(draft.meals).length > 0
  }, [dailyMeals, groupId, date, activeTab, buildDraftPayload])

  const onDeleteMeal = useCallback(
    (mealType: MealType3) => {
      const slot = dailyMeals[mealType]
      if (slot.mealStatus === 'expired' || slot.mealStatus === 'done') return
      setMealSlot(mealType, (prev) => ({
        ...prev,
        recipes: [],
        action: 'delete',
        dirty: true
      }))
    },
    [dailyMeals, setMealSlot]
  )

  const onRemoveRecipe = useCallback(
    (mealType: MealType3, recipeId: number) => {
      const slot = dailyMeals[mealType]
      if (slot.mealStatus === 'expired' || slot.mealStatus === 'done') return
      setMealSlot(mealType, (prev) => {
        const nextRecipes = prev.recipes.filter((r) => r.recipe_id !== recipeId)
        return {
          ...prev,
          recipes: nextRecipes,
          action: nextRecipes.length === 0 ? 'delete' : 'upsert',
          dirty: true
        }
      })
    },
    [dailyMeals, setMealSlot]
  )

  const onUpdateServings = useCallback(
    (mealType: MealType3, recipeId: number, servings: number) => {
      const slot = dailyMeals[mealType]
      if (slot.mealStatus === 'expired' || slot.mealStatus === 'done') return
      const safe = Number.isFinite(servings) ? Math.max(1, Math.floor(servings)) : 1
      setMealSlot(mealType, (prev) => ({
        ...prev,
        recipes: prev.recipes.map((r) => (r.recipe_id === recipeId ? { ...r, servings: safe } : r)),
        action: 'upsert',
        dirty: true
      }))
    },
    [dailyMeals, setMealSlot]
  )

  const onFinishMeal = useCallback(
    async (mealType: MealType3) => {
      if (!groupId) return
      const slot = dailyMeals[mealType]
      if (!slot.mealId) return
      if (slot.dirty) return
      if (slot.mealStatus === 'done' || slot.mealStatus === 'expired') return

      setTransitioningMealType(mealType)
      const result = await mealService.finishMeal({ mealId: slot.mealId, groupId })

      result.match(
        (resp) => {
          setMealSlot(mealType, (prev) => ({
            ...prev,
            mealId: resp.meal_id,
            mealStatus: resp.meal_status,
            dirty: false
          }))
          setTransitioningMealType(null)
        },
        (err) => {
          console.error('Failed to finish meal:', err)
          setMealsError('Không thể hoàn thành bữa ăn')
          setTransitioningMealType(null)
        }
      )
    },
    [groupId, dailyMeals, setMealSlot]
  )

  const onCancelOrReopen = useCallback(
    async (mealType: MealType3) => {
      if (!groupId) return
      const slot = dailyMeals[mealType]
      if (!slot.mealId) return
      if (slot.dirty) return

      setTransitioningMealType(mealType)
      const isCancelled = slot.mealStatus === 'cancelled'

      const result = isCancelled
        ? await mealService.reopenMeal({ mealId: slot.mealId, groupId })
        : await mealService.cancelMeal({ mealId: slot.mealId, groupId })

      result.match(
        (resp) => {
          setMealSlot(mealType, (prev) => ({
            ...prev,
            mealId: resp.meal_id,
            mealStatus: resp.meal_status,
            dirty: false
          }))
          setTransitioningMealType(null)
        },
        (err) => {
          console.error('Failed to transition meal:', err)
          setMealsError('Không thể cập nhật trạng thái bữa ăn')
          setTransitioningMealType(null)
        }
      )
    },
    [groupId, dailyMeals, setMealSlot]
  )

  const onUndoChanges = useCallback(() => {
    if (!originalDailyMeals || !groupId) return
    const mealDate = toISODateLocal(date)
    clearDraftPayload(groupId, mealDate)
    setDailyMeals(originalDailyMeals)
  }, [originalDailyMeals, groupId, date])

  const openFlattened = useCallback(
    async (recipe: MealRecipe) => {
      if (!groupId) return
      setFlattenedModal({
        open: true,
        title: recipe.recipe_name,
        loading: true,
        error: null,
        data: null
      })

      const result = await recipeService.getFlattened(
        [{ recipe_id: recipe.recipe_id, quantity: recipe.servings }],
        { checkExistence: true, groupId }
      )

      result.match(
        (resp) => {
          setFlattenedModal((s) => ({ ...s, loading: false, data: resp }))
        },
        (err) => {
          console.error('Failed to get flattened:', err)
          setFlattenedModal((s) => ({ ...s, loading: false, error: 'Không thể tải danh sách nguyên liệu' }))
        }
      )
    },
    [groupId]
  )

  // Save draft payload to localStorage whenever dailyMeals change
  useEffect(() => {
    if (!groupId || activeTab !== 'meal') return
    const mealDate = toISODateLocal(date)
    const draft = buildDraftPayload(dailyMeals, groupId, mealDate)
    if (draft) {
      saveDraftPayload(groupId, mealDate, draft)
    } else {
      clearDraftPayload(groupId, mealDate)
    }
  }, [dailyMeals, groupId, date, activeTab, buildDraftPayload])

  // Clear draft payload and reset meals when date changes
  useEffect(() => {
    if (!groupId || activeTab !== 'meal') {
      prevDateRef.current = date
      return
    }
    
    // If date changed, clear draft payload of the previous date and reset meals
    const prevDateStr = toISODateLocal(prevDateRef.current)
    const currentDateStr = toISODateLocal(date)
    
    if (prevDateStr !== currentDateStr) {
      // Clear draft payload of the previous date
      clearDraftPayload(groupId, prevDateStr)
      
      // Reset dailyMeals to empty state immediately when date changes
      // This ensures old data is cleared before new data is fetched
      setDailyMeals({
        breakfast: emptyMealSlot('breakfast'),
        lunch: emptyMealSlot('lunch'),
        dinner: emptyMealSlot('dinner')
      })
      setOriginalDailyMeals(null)
    }
    
    prevDateRef.current = date
  }, [date, groupId, activeTab])

  // Clear draft payload when switching to a different tab
  useEffect(() => {
    if (!groupId) {
      prevActiveTabRef.current = activeTab
      return
    }
    
    // If switching away from meal tab, clear draft payload
    if (prevActiveTabRef.current === 'meal' && activeTab !== 'meal') {
      const mealDate = toISODateLocal(date)
      clearDraftPayload(groupId, mealDate)
    }
    
    prevActiveTabRef.current = activeTab
  }, [activeTab, groupId, date])

  // Clear draft payload when navigating away (component unmount or route change)
  useEffect(() => {
    return () => {
      // Cleanup: clear draft payload when component unmounts
      if (groupId && activeTab === 'meal') {
        const mealDate = toISODateLocal(date)
        clearDraftPayload(groupId, mealDate)
      }
    }
  }, [groupId, activeTab, date])


  const buildMealCommand = useCallback((slot: MealSlot) => {
    if (slot.dirty) {
      if (slot.action === 'delete' || slot.recipes.length === 0) {
        // If meal doesn't exist on server (no mealId), skip instead of delete
        if (!slot.mealId) {
          return { action: 'skip' as const }
        }
        return { action: 'delete' as const }
      }
      return { action: 'upsert' as const, recipe_list: slot.recipes }
    }
    return { action: 'skip' as const }
  }, [])

  const onSaveDay = useCallback(async () => {
    if (!groupId) return
    setIsSaving(true)
    setMealsError(null)

    const cmd: DailyMealsCommand = {
      date: toISODateLocal(date),
      group_id: groupId,
      breakfast: buildMealCommand(dailyMeals.breakfast),
      lunch: buildMealCommand(dailyMeals.lunch),
      dinner: buildMealCommand(dailyMeals.dinner)
    }

    const result = await mealService.commandDailyMeals({ groupId, command: cmd })
    result.match(
      (items) => {
        const normalized = normalizeDailyMeals(items)
        setDailyMeals(normalized)
        setOriginalDailyMeals(normalized) // Update original state after save
        const mealDate = toISODateLocal(date)
        clearDraftPayload(groupId, mealDate) // Clear draft after successful save
        setIsSaving(false)
      },
      (err) => {
        console.error('Failed to save meals:', err)
        setMealsError(err.type === 'unauthorized' ? 'Bạn không có quyền lưu bữa ăn (cần Head Chef)' : 'Lưu bữa ăn thất bại')
        setIsSaving(false)
      }
    )
  }, [groupId, date, dailyMeals, buildMealCommand])

  if (isLoading || !groupData) {
    return (
      <div className="flex flex-col items-center justify-center px-6 pt-20 text-center">
        <div className="size-12 animate-spin rounded-full border-b-2 border-[#C3485C]"></div>
        <p className="mt-4 text-gray-600">Đang tải...</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col bg-white">
      {/* Header with Group Info */}
      <GroupHeader
        groupName={groupData.name}
        avatarUrl={groupData.avatarUrl}
        isCompact={true}
        onBack={handleBack}
        settingsButton={settingsButton}
      />

      <div className="px-4 pb-4">

        {/* Tabs */}
        <div className="mt-8 flex border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'members'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500'
            }`}
            onClick={() => {
              if (activeTab !== 'members') {
                navigate(`/main/family-group/${groupId}`, {
                  state: {
                    groupData: groupData ? {
                      id: groupData.id,
                      name: groupData.name,
                      avatarUrl: groupData.avatarUrl,
                      memberCount: groupData.memberCount,
                      adminName: groupData.adminName
                    } : undefined,
                    activeTab: 'members'
                  }
                })
              }
            }}
          >
            Thành viên
          </button>
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'shopping-plan'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500'
            }`}
            onClick={() => {
              if (activeTab !== 'shopping-plan') {
                navigate(`/main/family-group/${groupId}`, {
                  state: {
                    groupData: groupData ? {
                      id: groupData.id,
                      name: groupData.name,
                      avatarUrl: groupData.avatarUrl,
                      memberCount: groupData.memberCount,
                      adminName: groupData.adminName
                    } : undefined,
                    activeTab: 'shopping-plan'
                  }
                })
              }
            }}
          >
            Kế hoạch mua sắm
          </button>
        </div>

        {/* Quick Access Buttons */}
        <div className="mt-4 flex border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'storage'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500 hover:text-gray-900'
            }`}
            onClick={() => {
              if (activeTab !== 'storage') {
                navigate(`/main/family-group/${groupId}/storage`, {
                  state: {
                    groupData: groupData ? {
                      id: groupData.id,
                      name: groupData.name,
                      avatarUrl: groupData.avatarUrl,
                      memberCount: groupData.memberCount,
                      adminName: groupData.adminName
                    } : undefined
                  }
                })
              }
            }}
          >
            Quản lý kho thực phẩm
          </button>
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'meal'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('meal')}
          >
            Quản lý bữa ăn
          </button>
        </div>

        {/* Meal Content */}
        {activeTab === 'meal' && (
          <div className="mt-4">
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
                    onSelect={(selectedDate) => {
                      if (!selectedDate) return
                      const newDateStr = toISODateLocal(selectedDate)
                      navigate(`${location.pathname}?date=${encodeURIComponent(newDateStr)}`, {
                        state: groupData ? {
                          groupData: {
                            id: groupData.id,
                            name: groupData.name,
                            avatarUrl: groupData.avatarUrl,
                            memberCount: groupData.memberCount,
                            adminName: groupData.adminName
                          }
                        } : null
                      })
                    }}
                    required
                    classNames={{
                      root: `${calendarClassNames.root} shadow-lg p-2`
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
                    onClick={() => {
                      const newDateStr = toISODateLocal(d)
                      navigate(`${location.pathname}?date=${encodeURIComponent(newDateStr)}`, {
                        state: groupData ? {
                          groupData: {
                            id: groupData.id,
                            name: groupData.name,
                            avatarUrl: groupData.avatarUrl,
                            memberCount: groupData.memberCount,
                            adminName: groupData.adminName
                          }
                        } : null
                      })
                    }}
                  />
                )
              })}
            </div>

            {/* Status and action buttons */}
            <div className="mt-3 flex flex-col gap-3">
              {mealsLoading && (
                <div className="flex items-center justify-center gap-3 rounded-xl bg-gray-50 px-4 py-3">
                  <div className="text-sm text-gray-700">
                    <span className="flex items-center gap-2">
                      <Loader2 className="size-4 animate-spin" />
                      Đang tải bữa ăn...
                    </span>
                  </div>
                </div>
              )}
              {mealsError && (
                <div className="flex items-center justify-center gap-3 rounded-xl bg-gray-50 px-4 py-3">
                  <div className="text-sm text-red-500">{mealsError}</div>
                </div>
              )}
              {hasUnsavedChanges && (
                <div className="flex items-center justify-center gap-3">
                  <Button
                    icon={Save}
                    size="fit"
                    variant={!isSaving ? 'primary' : 'disabled'}
                    onClick={() => void onSaveDay()}
                  >
                    {isSaving ? 'Đang lưu...' : 'Lưu ngay'}
                  </Button>
                  <Button
                    icon={RotateCcw}
                    size="fit"
                    variant={!isSaving ? 'secondary' : 'disabled'}
                    onClick={onUndoChanges}
                  >
                    Hoàn tác
                  </Button>
                </div>
              )}
            </div>

            {/* Meals list (fixed 3 meals/day) */}
            <div className="flex flex-col items-center gap-3 py-2">
              {(() => {
                // Build draft payload from current state to check for actual changes
                const mealDate = toISODateLocal(date)
                const draft = groupId ? buildDraftPayload(dailyMeals, groupId, mealDate) : null
                
                return MEAL_TYPES_3.map((mealType) => {
                  const slot = dailyMeals[mealType]
                  const isExpanded = expandedMealType === mealType
                  const isEmpty = slot.recipes.length === 0 && slot.action !== 'upsert'
                  const isLocked = slot.mealStatus === 'expired' || slot.mealStatus === 'done'
                  
                  // Check if this meal has actual unsaved changes in draft payload
                  // Only show "Chưa lưu" if meal is dirty AND has actual changes to save
                  const hasActualChanges = draft?.meals[mealType] !== undefined
                
                // Determine meal card color based on status
                let bg = 'bg-gray-200' // Default: no meal (gray)
                let borderColor = 'border-gray-300'
                
                if (slot.mealId) {
                  if (slot.mealStatus === 'done') {
                    bg = 'bg-green-100' // Completed (green)
                    borderColor = 'border-green-400'
                  } else if (slot.mealStatus === 'expired') {
                    bg = 'bg-red-100' // Expired (red)
                    borderColor = 'border-red-400'
                  } else if (slot.mealStatus === 'created' || slot.mealStatus === 'cancelled') {
                    bg = 'bg-yellow-100' // Has meal but not completed (yellow)
                    borderColor = 'border-yellow-400'
                  }
                } else if (slot.action === 'upsert' && slot.recipes.length > 0) {
                  bg = 'bg-yellow-100' // New meal being added (yellow)
                  borderColor = 'border-yellow-400'
                }
                
                // Special border for meals with actual unsaved changes
                const borderStyle = hasActualChanges ? `border-2 ${borderColor}` : 'border border-gray-200'

                return (
                  <div key={mealType} className={`mx-auto w-full max-w-sm rounded-xl ${borderStyle} ${hasActualChanges ? 'shadow-md' : ''}`}>
                    <button
                      className={`flex w-full items-stretch gap-3 rounded-xl ${bg} px-4 py-3 text-left`}
                      onClick={() => setExpandedMealType((p) => (p === mealType ? null : mealType))}
                    >
                      <img src={MEAL_IMAGES[mealType]} alt="Meal" className="size-16 shrink-0" />

                      <div className="flex min-w-0 flex-1 flex-col justify-between">
                        <div className="flex items-center justify-between gap-2">
                          <p className="line-clamp-2 font-bold text-gray-800">{i18n.t(mealTypeStr(mealType as any))}</p>
                          <div className="flex items-center gap-1">
                            {hasActualChanges && (
                              <span className="rounded-full bg-white/60 px-2 py-0.5 text-xs font-semibold text-gray-700">
                                Chưa lưu
                              </span>
                            )}
                            {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                          </div>
                        </div>

                        <div className="mt-1 text-sm text-gray-700">
                          {isEmpty ? (
                            <p className="text-gray-600">Chưa có món ăn</p>
                          ) : (
                            <p className="line-clamp-2">
                              {slot.recipes.map((r) => r.recipe_name).join(', ')}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-col items-end justify-center gap-2">
                        <Button
                          icon={Check}
                          variant={
                            !slot.mealId ||
                            slot.dirty ||
                            transitioningMealType === mealType ||
                            slot.mealStatus === 'done' ||
                            slot.mealStatus === 'expired'
                              ? 'disabled'
                              : 'primary'
                          }
                          size="fit"
                          className={
                            !slot.mealId ||
                            slot.dirty ||
                            transitioningMealType === mealType ||
                            slot.mealStatus === 'done' ||
                            slot.mealStatus === 'expired'
                              ? ''
                              : '!bg-green-500 !text-white hover:!bg-green-600 !shadow-md !shadow-green-200'
                          }
                          onClick={(e) => {
                            e.stopPropagation()
                            void onFinishMeal(mealType)
                          }}
                        />
                        <Button
                          icon={Trash}
                          variant={isLocked || (isEmpty && !slot.mealId) ? 'disabled' : 'danger'}
                          size="fit"
                          onClick={(e) => {
                            e.stopPropagation()
                            if (!isLocked) {
                              onDeleteMeal(mealType)
                            }
                          }}
                        />
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="mt-2 rounded-xl border border-gray-200 bg-white p-3">
                        {slot.recipes.length === 0 ? (
                          <p className="text-sm text-gray-600">Chưa có công thức trong bữa này.</p>
                        ) : (
                          <div className="flex flex-col gap-2">
                            {slot.recipes.map((r) => (
                              <div
                                key={r.recipe_id}
                                className="flex items-center justify-between gap-2 rounded-lg bg-gray-50 px-3 py-2"
                              >
                                <button
                                  className="min-w-0 flex-1 line-clamp-2 text-left text-sm font-semibold text-gray-900 underline decoration-[#C3485C] decoration-2 underline-offset-2"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    void openFlattened(r)
                                  }}
                                  title="Xem nguyên liệu (flattened)"
                                >
                                  {r.recipe_name}
                                </button>

                                <div className="flex items-center gap-2">
                                  <label className="text-xs text-gray-600">Số khẩu phần</label>
                                  <input
                                    type="number"
                                    min={1}
                                    value={r.servings}
                                    onChange={(e) => onUpdateServings(mealType, r.recipe_id, Number(e.target.value))}
                                    disabled={isLocked}
                                    className={`w-20 rounded-lg border border-gray-200 bg-white px-2 py-1 text-sm ${isLocked ? 'cursor-not-allowed opacity-60' : ''}`}
                                    onClick={(e) => e.stopPropagation()}
                                  />
                                  <Button
                                    icon={X}
                                    size="fit"
                                    variant={isLocked ? 'disabled' : 'icon'}
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      if (!isLocked) {
                                        onRemoveRecipe(mealType, r.recipe_id)
                                      }
                                    }}
                                  />
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="mt-3 flex gap-2">
                          <Button
                            icon={Search}
                            size="fit"
                            variant={isLocked ? 'disabled' : 'primary'}
                            onClick={() => {
                              if (isLocked) return
                              if (!groupId) return
                              const mealDate = toISODateLocal(date)
                              const slot = dailyMeals[mealType]
                              navigate(
                                `/main/family-group/${groupId}/meal/select-recipe?meal_type=${mealType}&date=${encodeURIComponent(mealDate)}`,
                                {
                                  state: {
                                    existingRecipes: slot.recipes.map((r) => ({
                                      recipe_id: r.recipe_id,
                                      recipe_name: r.recipe_name,
                                      servings: r.servings
                                    })),
                                    groupData: groupData ? {
                                      id: groupData.id,
                                      name: groupData.name,
                                      avatarUrl: groupData.avatarUrl,
                                      memberCount: groupData.memberCount,
                                      adminName: groupData.adminName
                                    } : undefined
                                  }
                                }
                              )
                            }}
                          >
                            Thêm công thức
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })
              })()}
            </div>
          </div>
        )}
      </div>

      {showNoti && <NotificationPopup onClose={() => setShowNoti(false)} />}

      {/* Flattened ingredients modal */}
      {flattenedModal.open && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <p className="text-lg font-bold text-gray-900">Nguyên liệu: {flattenedModal.title}</p>
              <button
                className="rounded-lg p-2 hover:bg-gray-100"
                onClick={() => setFlattenedModal((s) => ({ ...s, open: false }))}
              >
                <X />
              </button>
            </div>

            {flattenedModal.loading ? (
              <div className="flex items-center justify-center py-10">
                <Loader2 className="size-7 animate-spin text-[#C3485C]" />
              </div>
            ) : flattenedModal.error ? (
              <p className="py-8 text-center text-sm text-red-500">{flattenedModal.error}</p>
            ) : (
              <div className="mt-3 max-h-96 overflow-auto">
                {flattenedModal.data?.ingredients?.length ? (
                  <div className="flex flex-col gap-2">
                    {flattenedModal.data.ingredients.map((it, idx) => {
                      const unit =
                        it.ingredient.type === 'countable_ingredient'
                          ? String(it.ingredient.c_measurement_unit ?? '')
                          : String(it.ingredient.uc_measurement_unit ?? '')
                      const unitStr = unit ? ` ${unit}` : ''
                      const availabilityIcon =
                        it.available === true ? (
                          <Check className="size-5 text-green-600" />
                        ) : it.available === false ? (
                          <X className="size-5 text-red-600" />
                        ) : null

                      return (
                        <div
                          key={`${it.ingredient.component_id}-${idx}`}
                          className="flex items-center justify-between rounded-xl bg-gray-50 px-3 py-2"
                        >
                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-gray-900">{it.ingredient.component_name}</p>
                            <p className="text-xs text-gray-600">
                              {it.quantity}
                              {unitStr}
                            </p>
                          </div>
                          {availabilityIcon}
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <p className="py-6 text-center text-sm text-gray-600">Không có nguyên liệu</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
