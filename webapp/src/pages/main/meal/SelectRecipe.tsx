import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams, useLocation } from 'react-router-dom'
import { ArrowLeft, ChefHat, Clock, Loader2, Search, Users } from 'lucide-react'
import { recipeService, type Recipe } from '../../../services/recipe'
import type { MealType3 } from '../../../services/meal'
import { i18n } from '../../../utils/i18n/i18n'
import { mealTypeStr } from '../../../utils/constants'
import { groupService } from '../../../services/group'

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

const DEFAULT_RECIPE_IMAGE = new URL('../../../assets/ingredient.png', import.meta.url).href

function safeMealType3(x: string | null): MealType3 | null {
  if (x === 'breakfast' || x === 'lunch' || x === 'dinner') return x
  return null
}

export function SelectRecipe() {
  const { id: groupId } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const location = useLocation()

  const mealType = useMemo(() => safeMealType3(searchParams.get('meal_type')), [searchParams])
  const date = useMemo(() => searchParams.get('date') ?? '', [searchParams])

  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [nextCursor, setNextCursor] = useState<number | null>(null)
  const [hasMore, setHasMore] = useState(false)

  // Recommended recipes
  const [recommendedRecipeIds, setRecommendedRecipeIds] = useState<Set<number>>(new Set())
  const [recommendedRecipes, setRecommendedRecipes] = useState<Recipe[]>([])
  const [isLoadingRecommended, setIsLoadingRecommended] = useState(false)

  // Group data state
  const [groupData, setGroupData] = useState<{
    id: string
    name: string
    avatarUrl: string | null
    memberCount: number
    adminName: string
  } | null>(null)
  const [isLoadingGroup, setIsLoadingGroup] = useState(true)

  // Initialize selectedMap with existing recipes from meal
  const [selectedMap, setSelectedMap] = useState<
    Record<
      number,
      {
        recipe: Recipe
        servings: number
      }
    >
  >(() => {
    const state = location.state as { existingRecipes?: Array<{ recipe_id: number; recipe_name: string; servings: number }> } | null
    if (!state?.existingRecipes) return {}
    
    // Create initial map from existing recipes
    // We'll populate the recipe object when recipes are loaded
    const initialMap: Record<number, { recipe: Recipe; servings: number }> = {}
    for (const existing of state.existingRecipes) {
      // We'll need to find the recipe object later when recipes are loaded
      // For now, store the servings
      initialMap[existing.recipe_id] = {
        recipe: {
          component_id: existing.recipe_id,
          component_name: existing.recipe_name,
          default_servings: existing.servings
        } as Recipe,
        servings: existing.servings
      }
    }
    return initialMap
  })

  const selectedCount = Object.keys(selectedMap).length
  const canSubmit = Boolean(groupId && mealType && date && selectedCount > 0)

  const fetchRecipes = async (keyword: string, cursor?: number) => {
    setIsLoading(true)
    setError(null)

    const trimmed = keyword.trim()
    const result = trimmed
      ? await recipeService.searchRecipes(trimmed, cursor, 10)
      : await recipeService.getRecipes(cursor, 10)
    result.match(
      (response) => {
        // Filter out recommended recipes to avoid duplication
        const filtered = response.data.filter((r) => !recommendedRecipeIds.has(r.component_id))
        if (cursor) setRecipes((prev) => [...prev, ...filtered])
        else setRecipes(filtered)
        setNextCursor(response.next_cursor)
        setHasMore(response.next_cursor !== null)
        setIsLoading(false)
      },
      (err) => {
        console.error('Failed to fetch recipes:', err)
        setError('Không thể tải công thức')
        setIsLoading(false)
      }
    )
  }

  // Fetch recommended recipes
  const fetchRecommendedRecipes = async () => {
    if (!groupId) return

    setIsLoadingRecommended(true)
    const result = await recipeService.getRecommendedRecipes(groupId)

    result.match(
      (recipes) => {
        if (recipes.length === 0) {
          setIsLoadingRecommended(false)
          return
        }

        const recipeIds = recipes.map((r) => r.component_id)
        setRecommendedRecipeIds(new Set(recipeIds))
        setRecommendedRecipes(recipes)
        setIsLoadingRecommended(false)
      },
      (err) => {
        console.error('Failed to fetch recommended recipes:', err)
        setIsLoadingRecommended(false)
      }
    )
  }

  // Load group data
  useEffect(() => {
    if (!groupId) {
      setIsLoadingGroup(false)
      return
    }

    const loadGroupData = async () => {
      setIsLoadingGroup(true)
      
      // Check if groupData was passed via navigation state
      const stateGroupData = (location.state as { groupData?: typeof groupData })?.groupData
      if (stateGroupData) {
        setGroupData(stateGroupData)
        setIsLoadingGroup(false)
        return
      }

      // Otherwise, fetch from API
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
          setIsLoadingGroup(false)
        },
        (err) => {
          console.error('Failed to load group data:', err)
          setIsLoadingGroup(false)
        }
      )
    }

    void loadGroupData()
  }, [groupId, location.state])

  // Fetch recommended recipes first
  useEffect(() => {
    void fetchRecommendedRecipes()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupId])

  // Fetch regular recipes after recommended recipes are loaded
  useEffect(() => {
    if (!isLoadingRecommended && searchQuery.trim() === '') {
      fetchRecipes('')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoadingRecommended])

  // Update selectedMap with full recipe objects when recipes are loaded
  useEffect(() => {
    const state = location.state as { existingRecipes?: Array<{ recipe_id: number; recipe_name: string; servings: number }> } | null
    if (!state?.existingRecipes || recipes.length === 0) return

    setSelectedMap((prev) => {
      const updated = { ...prev }
      let hasChanges = false

      for (const existing of state.existingRecipes || []) {
        const recipe = recipes.find((r) => r.component_id === existing.recipe_id)
        if (recipe) {
          // Update with full recipe object if not already updated or if recipe data changed
          const current = updated[existing.recipe_id]
          if (!current || current.recipe.component_id !== recipe.component_id || !current.recipe.image_url) {
            updated[existing.recipe_id] = {
              recipe,
              servings: existing.servings
            }
            hasChanges = true
          } else if (current.servings !== existing.servings) {
            // Update servings if changed
            updated[existing.recipe_id] = {
              ...current,
              servings: existing.servings
            }
            hasChanges = true
          }
        }
      }

      return hasChanges ? updated : prev
    })
  }, [recipes, location.state])

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.trim()) {
        fetchRecipes(searchQuery.trim())
      } else if (!isLoadingRecommended) {
        // Only fetch regular recipes if recommended recipes are already loaded
        fetchRecipes('')
      }
    }, 500)
    return () => clearTimeout(timeoutId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery, isLoadingRecommended])

  const handleLoadMore = () => {
    if (nextCursor && !isLoading) fetchRecipes(searchQuery, nextCursor)
  }

  const onConfirm = () => {
    if (!groupId || !mealType || !date) return
    if (selectedCount === 0) return
    navigate(`/main/family-group/${groupId}/meal?date=${encodeURIComponent(date)}`, {
      state: {
        addToMeal: {
          date,
          mealType,
          items: Object.values(selectedMap).map((it) => ({
            recipe: {
              id: it.recipe.component_id,
              name: it.recipe.component_name,
              default_servings: it.recipe.default_servings
            },
            servings: it.servings
          }))
        },
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

  const handleBack = () => {
    if (!groupId || !date) return
    navigate(`/main/family-group/${groupId}/meal?date=${encodeURIComponent(date)}`, {
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
  }

  if (!groupId || !mealType || !date) {
    return (
      <div className="flex min-h-screen flex-col p-4">
        <button
          className="mb-4 flex items-center gap-2 text-sm font-bold text-[#C3485C]"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={18} />
          Quay lại
        </button>
        <p className="text-red-500">Thiếu tham số (groupId/meal_type/date)</p>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col p-4 pb-24">
      <div className="mb-3 flex items-center justify-between">
        <button
          className="flex items-center gap-2 text-sm font-bold text-[#C3485C]"
          onClick={handleBack}
        >
          <ArrowLeft size={18} />
          Quay lại
        </button>
        <p className="text-xs font-semibold text-gray-600">
          {date} • {i18n.t(mealTypeStr(mealType as any))}
        </p>
      </div>

      <h1 className="mb-3 text-xl font-bold text-gray-900">Chọn công thức</h1>

      {/* Search */}
      <div className="relative mb-3">
        <Search className="absolute left-3 top-1/2 size-5 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Tìm kiếm công thức..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full rounded-xl border border-gray-300 py-2 pl-10 pr-4 focus:border-[#C3485C] focus:outline-none"
        />
      </div>

      {/* Recommended Recipes Section */}
      {!searchQuery.trim() && recommendedRecipes.length > 0 && (
        <div className="mb-4 rounded-2xl border-2 border-[#C3485C] bg-gradient-to-br from-[#FFF6F0] to-[#FFE8D6] p-2 shadow-md">
          <h2 className="mb-2 text-base font-bold text-[#C3485C]">🍽️ Đề xuất cho nhóm bạn</h2>
          <div className="flex flex-col gap-2">
            {recommendedRecipes.map((r) => {
              const isSelected = selectedMap[r.component_id] !== undefined
              const prep = r.prep_time ? `${r.prep_time}p` : null
              const cook = r.cook_time ? `${r.cook_time}p` : null
              const level = r.level ? String(r.level) : null

              return (
                <div
                  key={r.component_id}
                  className={[
                    'rounded-xl border bg-white p-3 shadow-sm transition',
                    isSelected ? 'border-[#C3485C] ring-2 ring-[#C3485C]' : 'border-gray-200'
                  ].join(' ')}
                  onClick={() =>
                    setSelectedMap((prev) => {
                      if (prev[r.component_id]) {
                        const next = { ...prev }
                        delete next[r.component_id]
                        return next
                      }
                      return {
                        ...prev,
                        [r.component_id]: {
                          recipe: r,
                          servings: Math.max(1, r.default_servings || 1)
                        }
                      }
                    })
                  }
                >
                  <div className="flex gap-3">
                    <img
                      src={r.image_url || DEFAULT_RECIPE_IMAGE}
                      alt={r.component_name}
                      className="size-14 shrink-0 rounded-xl object-cover"
                    />

                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <Link
                          to={`/main/recipe-view/recipe/${r.component_id}`}
                          className="line-clamp-2 text-sm font-bold text-gray-900 underline decoration-[#C3485C] decoration-2 underline-offset-2"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {r.component_name}
                        </Link>
                        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-semibold text-gray-700">
                          Khẩu phần: {r.default_servings}
                        </span>
                      </div>

                      <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-700">
                        {prep && (
                          <span className="flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1">
                            <Clock className="size-3" />
                            Prep {prep}
                          </span>
                        )}
                        {cook && (
                          <span className="flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1">
                            <ChefHat className="size-3" />
                            Cook {cook}
                          </span>
                        )}
                        {level && (
                          <span className="rounded-full bg-gray-50 px-2 py-1">
                            Level {level}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {isSelected && (
                    <div className="mt-3 rounded-xl bg-[#FFF6F0] p-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold text-gray-900">Đã chọn</p>
                        <div className="flex items-center gap-2">
                          <Users className="size-4 text-[#C3485C]" />
                          <input
                            type="number"
                            min={1}
                            value={selectedMap[r.component_id]?.servings ?? 1}
                            onChange={(e) =>
                              setSelectedMap((prev) => {
                                const cur = prev[r.component_id]
                                if (!cur) return prev
                                return {
                                  ...prev,
                                  [r.component_id]: {
                                    ...cur,
                                    servings: Math.max(1, Math.floor(Number(e.target.value) || 1))
                                  }
                                }
                              })
                            }
                            onClick={(e) => e.stopPropagation()}
                            className="w-24 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm"
                          />
                          <span className="text-sm text-gray-700">servings</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {error ? (
        <div className="flex flex-1 items-center justify-center py-8">
          <p className="text-red-500">{error}</p>
        </div>
      ) : recipes.length === 0 && !isLoading ? (
        <div className="flex flex-1 items-center justify-center py-8">
          <p className="text-gray-500">Không tìm thấy công thức nào</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {recipes.map((r) => {
            const isSelected = selectedMap[r.component_id] !== undefined
            const prep = r.prep_time ? `${r.prep_time}p` : null
            const cook = r.cook_time ? `${r.cook_time}p` : null
            const level = r.level ? String(r.level) : null

            return (
              <div
                key={r.component_id}
                className={[
                  'rounded-2xl border bg-white p-3 shadow-sm transition',
                  isSelected ? 'border-[#C3485C] ring-1 ring-[#C3485C]' : 'border-gray-200'
                ].join(' ')}
                onClick={() =>
                  setSelectedMap((prev) => {
                    // toggle select
                    if (prev[r.component_id]) {
                      const next = { ...prev }
                      delete next[r.component_id]
                      return next
                    }
                    return {
                      ...prev,
                      [r.component_id]: {
                        recipe: r,
                        servings: Math.max(1, r.default_servings || 1)
                      }
                    }
                  })
                }
              >
                <div className="flex gap-3">
                  <img
                    src={r.image_url || DEFAULT_RECIPE_IMAGE}
                    alt={r.component_name}
                    className="size-14 shrink-0 rounded-xl object-cover"
                  />

                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <Link
                        to={`/main/recipe-view/recipe/${r.component_id}`}
                        className="line-clamp-2 text-sm font-bold text-gray-900 underline decoration-[#C3485C] decoration-2 underline-offset-2"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {r.component_name}
                      </Link>
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-semibold text-gray-700">
                        Khẩu phần: {r.default_servings}
                      </span>
                    </div>

                    <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-700">
                      {prep && (
                        <span className="flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1">
                          <Clock className="size-3" />
                          Prep {prep}
                        </span>
                      )}
                      {cook && (
                        <span className="flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1">
                          <ChefHat className="size-3" />
                          Cook {cook}
                        </span>
                      )}
                      {level && (
                        <span className="rounded-full bg-gray-50 px-2 py-1">
                          Level {level}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {isSelected && (
                  <div className="mt-3 rounded-xl bg-[#FFF6F0] p-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-gray-900">Đã chọn</p>
                      <div className="flex items-center gap-2">
                        <Users className="size-4 text-[#C3485C]" />
                        <input
                          type="number"
                          min={1}
                          value={selectedMap[r.component_id]?.servings ?? 1}
                          onChange={(e) =>
                            setSelectedMap((prev) => {
                              const cur = prev[r.component_id]
                              if (!cur) return prev
                              return {
                                ...prev,
                                [r.component_id]: {
                                  ...cur,
                                  servings: Math.max(1, Math.floor(Number(e.target.value) || 1))
                                }
                              }
                            })
                          }
                          onClick={(e) => e.stopPropagation()}
                          className="w-24 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm"
                        />
                        <span className="text-sm text-gray-700">servings</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}

          {hasMore && (
            <div className="mt-2 flex justify-center">
              <button
                onClick={handleLoadMore}
                disabled={isLoading}
                className="rounded-xl bg-[#C3485C] px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="size-4 animate-spin" />
                    Đang tải...
                  </span>
                ) : (
                  'Tải thêm'
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {isLoading && recipes.length === 0 && (
        <div className="flex flex-1 items-center justify-center py-8">
          <Loader2 className="size-8 animate-spin text-[#C3485C]" />
        </div>
      )}

      {/* Bottom sticky action */}
      <div className="fixed bottom-16 left-0 right-0 mx-auto w-full max-w-sm px-4">
        <button
          disabled={!canSubmit}
          onClick={onConfirm}
          className={[
            'w-full rounded-2xl px-4 py-3 text-center text-sm font-bold shadow-md',
            canSubmit
              ? 'bg-[#C3485C] text-[#F8EFCE]'
              : 'bg-gray-300 text-gray-600'
          ].join(' ')}
        >
          Thêm vào bữa ({selectedCount})
        </button>
      </div>
    </div>
  )
}


