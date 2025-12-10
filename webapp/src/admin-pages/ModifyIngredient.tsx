import { useNavigate, useLocation } from 'react-router-dom'
import { IngredientForm } from '../components/IngredientForm'
import IngredientDashboard from './IngredientList'

const ModifyIngredient = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const item = location.state?.item

  const handleSave = () => {
    // Here you would typically save the changes
    navigate('/admin/ingredient-list')
  }

  const handleCancel = () => {
    navigate('/admin/view-ingredient', { state: { item } })
  }

  if (!item) {
    return <div>Loading...</div>
  }

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
          onSubmit={handleSave}
          onCancel={handleCancel}
          submitLabel="Lưu"
        />
      </div>
    </div>
  )
}

export default ModifyIngredient