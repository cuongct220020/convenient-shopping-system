import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Clock, Users, ChefHat } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { LoadingSpinner } from '../../../components/LoadingSpinner'
import { recipeService, type RecipeDetailedResponse } from '../../../services/recipe'

// Default recipe image
const DEFAULT_RECIPE_IMAGE = new URL('../../../assets/ingredient.png', import.meta.url).href

export function RecipeDetail() {
  const { id } = useParams<{ id: string }>()
  const [recipe, setRecipe] = useState<RecipeDetailedResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const formatQty = (qty: number) => {
    if (Number.isInteger(qty)) return String(qty)
    // keep a compact representation for floats
    return String(Number(qty.toFixed(2))).replace(/\.0+$/, '')
  }

  useEffect(() => {
    if (!id) {
      setError('Không tìm thấy công thức')
      setIsLoading(false)
      return
    }

    const fetchRecipe = async () => {
      setIsLoading(true)
      setError(null)

      const result = await recipeService.getRecipeDetailed(Number(id))

      result.match(
        (response) => {
          setRecipe(response)
          setIsLoading(false)
        },
        (err) => {
          console.error('Failed to fetch recipe:', err)
          setError('Không thể tải công thức')
          setIsLoading(false)
        }
      )
    }

    fetchRecipe()
  }, [id])

  if (isLoading) {
    return (
      <div className="flex min-h-screen flex-col p-4">
        <BackButton to="/main/recipe-view" text="Quay lại" className="mb-4" />
        <div className="flex flex-1 items-center justify-center py-16">
          <LoadingSpinner size="lg" showText text="Đang tải..." />
        </div>
      </div>
    )
  }

  if (error || !recipe) {
    return (
      <div className="flex min-h-screen flex-col p-4">
        <BackButton to="/main/recipe-view" text="Quay lại" className="mb-4" />
        <div className="flex flex-1 items-center justify-center py-16">
          <p className="text-red-500">{error || 'Không tìm thấy công thức'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col bg-gray-50 pb-4">
      <BackButton to="/main/recipe-view" text="Quay lại" className="sticky top-0 z-10 bg-gray-50 p-4 pb-2" />
      
      {/* Recipe Image */}
      <div className="px-4 pb-4">
        <div className="overflow-hidden rounded-2xl shadow-lg">
          <img
            src={recipe.image_url?.trim() || DEFAULT_RECIPE_IMAGE}
            alt={recipe.component_name}
            className="h-64 w-full object-cover"
          />
        </div>
      </div>

      <div className="flex-1 px-4">
        {/* Recipe Title */}
        <h1 className="mb-4 text-3xl font-bold text-gray-900">{recipe.component_name}</h1>

        {/* Recipe Info Cards */}
        <div className="mb-6 grid grid-cols-3 gap-3">
          {recipe.prep_time && (
            <div className="flex flex-col items-center rounded-xl bg-white p-3 shadow-sm">
              <Clock className="mb-1 size-5 text-[#C3485C]" />
              <span className="text-xs text-gray-500">Chuẩn bị</span>
              <span className="text-sm font-semibold text-gray-900">{recipe.prep_time} phút</span>
            </div>
          )}
          {recipe.cook_time && (
            <div className="flex flex-col items-center rounded-xl bg-white p-3 shadow-sm">
              <ChefHat className="mb-1 size-5 text-[#C3485C]" />
              <span className="text-xs text-gray-500">Nấu</span>
              <span className="text-sm font-semibold text-gray-900">{recipe.cook_time} phút</span>
            </div>
          )}
          <div className="flex flex-col items-center rounded-xl bg-white p-3 shadow-sm">
            <Users className="mb-1 size-5 text-[#C3485C]" />
            <span className="text-xs text-gray-500">Khẩu phần</span>
            <span className="text-sm font-semibold text-gray-900">{recipe.default_servings}</span>
          </div>
        </div>

        {/* Ingredients */}
        {recipe.component_list && recipe.component_list.length > 0 && (
          <div className="mb-6 rounded-2xl bg-white p-4 shadow-sm">
            <h2 className="mb-4 text-xl font-bold text-gray-900">Nguyên liệu</h2>
            <ul className="space-y-3">
              {recipe.component_list.map((item, index) => {
                const isRecipe = item.component.type === 'recipe'
                const unit =
                  item.component.type === 'countable_ingredient'
                    ? String((item.component as any).c_measurement_unit ?? '')
                    : item.component.type === 'uncountable_ingredient'
                      ? String((item.component as any).uc_measurement_unit ?? '')
                      : ''
                const unitStr = unit ? unit.toLowerCase() : ''
                const qtyStr = unitStr
                  ? `${formatQty(item.quantity)} ${unitStr}`
                  : formatQty(item.quantity)
                
                return (
                  <li key={index} className="flex items-center justify-between border-b border-gray-100 pb-3 last:border-b-0 last:pb-0">
                    <div className="flex-1 text-sm text-gray-800">
                      {isRecipe ? (
                        <Link
                          to={`/main/recipe-view/recipe/${item.component.component_id}`}
                          className="font-semibold text-gray-900 underline decoration-[#C3485C] decoration-2 underline-offset-2 transition-colors hover:text-[#C3485C]"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {item.component.component_name}
                        </Link>
                      ) : (
                        <span className="font-semibold text-gray-900">
                          {item.component.component_name}
                        </span>
                      )}
                      <span className="text-gray-600">: </span>
                      <span className="font-semibold text-[#C3485C]">{qtyStr}</span>
                    </div>
                  </li>
                )
              })}
            </ul>
          </div>
        )}

        {/* Instructions */}
        {recipe.instructions && recipe.instructions.length > 0 && (
          <div className="mb-6 rounded-2xl bg-white p-4 shadow-sm">
            <h2 className="mb-4 text-xl font-bold text-gray-900">Hướng dẫn nấu</h2>
            <ol className="space-y-4">
              {recipe.instructions.map((instruction, index) => (
                <li key={index} className="flex gap-3">
                  <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-[#C3485C] text-sm font-bold text-white">
                    {index + 1}
                  </span>
                  <p className="flex-1 text-gray-700 leading-relaxed">{instruction}</p>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Keywords */}
        {recipe.keywords && recipe.keywords.length > 0 && (
          <div className="rounded-2xl bg-white p-4 shadow-sm">
            <h2 className="mb-3 text-xl font-bold text-gray-900">Từ khóa</h2>
            <div className="flex flex-wrap gap-2">
              {recipe.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="rounded-full bg-gray-100 px-4 py-1.5 text-sm text-gray-700"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
