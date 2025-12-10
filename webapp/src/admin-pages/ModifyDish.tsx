import { useNavigate, useLocation } from 'react-router-dom'
import { DishForm } from '../components/DishForm'
import DishList from './DishList'

const ModifyDish = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const item = location.state?.item

  const handleContinue = (dishData: any) => {
    console.log('Updating dish:', dishData)
    navigate('/admin/dish-list')
  }

  const handleDraft = () => {
    navigate('/admin/dish-list')
  }

  if (!item) {
    return <div>Loading...</div>
  }

  // Parse the dish data to match DishForm expected format
  const parsedDishData = {
    dishName: item.name || '',
    category: item.category || '',
    difficulty: item.difficulty || '',
    image: item.image || null,
    servings: item.servings || 0,
    cookTime: item.cookTime || '',
    prepTime: item.prepTime || '',
    ingredients: item.ingredients || [],
    instructions: item.instructions || []
  }

  return (
    <div className="relative h-full min-h-screen w-full overflow-hidden bg-gray-50">
      {/* Background Layer: DishList blurred */}
      <div className="absolute inset-0 z-0 flex flex-col blur-sm pointer-events-none">
        <DishList />
      </div>

      {/* Overlay Layer: Semi-transparent to make form pop */}
      <div className="absolute inset-0 z-10 bg-black/30 pointer-events-none" />

      {/* Foreground Layer: The Form */}
      <div className="relative z-20 flex min-h-screen items-center justify-center p-4">
        <DishForm
          initialData={parsedDishData}
          onSubmit={handleContinue}
          onCancel={handleDraft}
        />
      </div>
    </div>
  )
}

export default ModifyDish