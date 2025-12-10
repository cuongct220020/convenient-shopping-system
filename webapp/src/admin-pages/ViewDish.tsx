import { Check, Edit, Trash2 } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Button } from '../components/Button'
import { DishForm } from '../components/DishForm'
import DishList from './DishList'

const ViewDish = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const item = location.state?.item

  const handleBack = () => {
    navigate('/admin/dish-list')
  }

  const handleEdit = () => {
    navigate('/admin/modify-dish', { state: { item } })
  }

  const handleDelete = () => {
    navigate('/admin/dish-list')
  }

  if (!item) {
    return <div>Loading...</div>
  }

  // Parse the dish data to match DishForm expected format
  const parsedDishData = {
    dishName: item.name || 'Chưa có thông tin',
    category: item.category || 'Chưa có thông tin',
    difficulty: item.difficulty || 'Chưa có thông tin',
    image: item.image || null,
    servings: item.servings || 'Chưa có thông tin',
    cookTime: item.cookTime || 'Chưa có thông tin',
    prepTime: item.prepTime || 'Chưa có thông tin',
    ingredients: item.ingredients && item.ingredients.length > 0 ? item.ingredients : [],
    instructions: item.instructions && item.instructions.length > 0 ? item.instructions : []
  }

  const customActions = (
    <>
      <Button
        variant="primary"
        size="fit"
        icon={Check}
        onClick={handleBack}
        className="mx-0 -mr-1"
      >
        Quay lại
      </Button>
      <Button
        variant="secondary"
        size="fit"
        icon={Edit}
        className="mx-0 -mx-1"
        onClick={handleEdit}
      >
        Chỉnh sửa
      </Button>
      <Button
        variant="secondary"
        size="fit"
        icon={Trash2}
        className="mx-0 -ml-1"
        onClick={handleDelete}
      >
        Xóa
      </Button>
    </>
  )

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
          readOnly={true}
          actions={customActions}
          onSubmit={() => {}} // Empty function since form is read-only
          onCancel={handleBack}
        />
      </div>
    </div>
  )
}

export default ViewDish