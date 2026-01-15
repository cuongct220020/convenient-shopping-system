import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Loader2 } from 'lucide-react'
import { recipeService, type Recipe } from '../../../services/recipe'

// Default recipe image
const DEFAULT_RECIPE_IMAGE = new URL('../../../assets/ingredient.png', import.meta.url).href

interface RecipeCardProps {
  recipe: Recipe
  onClick: () => void
}

function RecipeCard({ recipe, onClick }: RecipeCardProps) {
  return (
    <div
      className="cursor-pointer rounded-xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md"
      onClick={onClick}
    >
      <div className="aspect-square overflow-hidden rounded-t-xl">
        <img
          src={recipe.image_url || DEFAULT_RECIPE_IMAGE}
          alt={recipe.component_name}
          className="h-full w-full object-cover"
        />
      </div>
      <div className="p-3">
        <h3 className="line-clamp-2 text-sm font-bold text-gray-900">
          {recipe.component_name}
        </h3>
        <p className="mt-1 text-xs text-gray-500">
          {recipe.default_servings} phần
        </p>
      </div>
    </div>
  )
}

export function Recipes() {
  const navigate = useNavigate()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [nextCursor, setNextCursor] = useState<number | null>(null)
  const [hasMore, setHasMore] = useState(false)

  const fetchRecipes = async (keyword: string, cursor?: number) => {
    setIsLoading(true)
    setError(null)

    const trimmed = keyword.trim()
    const result = trimmed
      ? await recipeService.searchRecipes(trimmed, cursor, 10)
      : await recipeService.getRecipes(cursor, 10)

    result.match(
      (response) => {
        if (cursor) {
          // Append to existing recipes for pagination
          setRecipes((prev) => [...prev, ...response.data])
        } else {
          // Replace recipes for new search
          setRecipes(response.data)
        }
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

  // Initial load
  useEffect(() => {
    fetchRecipes('')
  }, [])

  // Handle search with debounce
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.trim()) {
        fetchRecipes(searchQuery.trim())
      } else {
        fetchRecipes('')
      }
    }, 500)

    return () => clearTimeout(timeoutId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery])

  const handleLoadMore = () => {
    if (nextCursor && !isLoading) {
      fetchRecipes(searchQuery, nextCursor)
    }
  }

  const handleRecipeClick = (recipeId: number) => {
    navigate(`/main/recipe-view/recipe/${recipeId}`)
  }

  return (
    <div className="flex min-h-screen flex-col p-4">
      <h1 className="mb-4 text-2xl font-bold text-[#C3485C]">Công thức nấu ăn</h1>

      {/* Search Bar */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 size-5 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Tìm kiếm công thức..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 focus:border-[#C3485C] focus:outline-none"
        />
      </div>

      {/* Recipes Grid */}
      {error ? (
        <div className="flex flex-1 items-center justify-center py-8">
          <p className="text-red-500">{error}</p>
        </div>
      ) : recipes.length === 0 && !isLoading ? (
        <div className="flex flex-1 items-center justify-center py-8">
          <p className="text-gray-500">Không tìm thấy công thức nào</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4">
            {recipes.map((recipe) => (
              <RecipeCard
                key={recipe.component_id}
                recipe={recipe}
                onClick={() => handleRecipeClick(recipe.component_id)}
              />
            ))}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div className="mt-4 flex justify-center">
              <button
                onClick={handleLoadMore}
                disabled={isLoading}
                className="rounded-lg bg-[#C3485C] px-4 py-2 text-white disabled:opacity-50"
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
        </>
      )}

      {isLoading && recipes.length === 0 && (
        <div className="flex flex-1 items-center justify-center py-8">
          <Loader2 className="size-8 animate-spin text-[#C3485C]" />
        </div>
      )}
    </div>
  )
}

