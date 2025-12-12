import { Check, Edit, Trash2 } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Button } from '../components/Button'
import { IngredientForm } from '../components/IngredientForm'
import IngredientDashboard from './IngredientMenu'

const ViewIngredient = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const item = location.state?.item

  const handleBack = () => {
    navigate('/admin/ingredient-list')
  }

  const handleEdit = () => {
    navigate('/admin/modify-ingredient', { state: { item } })
  }

  const handleDelete = () => {
    navigate('/admin/ingredient-list')
  }

  if (!item) {
    return <div>Loading...</div>
  }

  const customActions = (
    <>
      <Button
        variant="primary"
        size="fit"
        icon={Check}
        onClick={handleBack}
        className="mx-0"
      >
        Quay lại
      </Button>
      <Button
        variant="secondary"
        size="fit"
        icon={Edit}
        className="mx-0"
        onClick={handleEdit}
      >
        Chỉnh sửa
      </Button>
      <Button
        variant="secondary"
        size="fit"
        icon={Trash2}
        className="mx-0"
        onClick={handleDelete}
      >
        Xóa
      </Button>
    </>
  )

  return (
    <div className="relative h-full min-h-screen w-full overflow-hidden bg-gray-50">
      {/* Background Layer: IngredientDashboard blurred */}
      <div className="absolute inset-0 z-0 flex flex-col blur-sm pointer-events-none">
        <IngredientDashboard />
      </div>

      {/* Overlay Layer: Semi-transparent to make form pop */}
      <div className="absolute inset-0 z-10 bg-black/30 pointer-events-none" />

      {/* Foreground Layer: The Form */}
      <div className="relative z-20 flex min-h-screen items-center justify-center p-4">
        <IngredientForm
          initialData={item}
          readOnly={true}
          actions={customActions}
        />
      </div>
    </div>
  )
}

export default ViewIngredient
