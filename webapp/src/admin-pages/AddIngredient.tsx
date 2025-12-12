import { useNavigate } from 'react-router-dom'
import { IngredientForm } from '../components/IngredientForm'
import IngredientDashboard from './IngredientMenu'

const AddIngredient = () => {
  const navigate = useNavigate()

  const handleContinue = () => {
    navigate('/admin/ingredient-list')
  }

  const handleDraft = () => {
    navigate('/admin/ingredient-list')
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
        <IngredientForm onSubmit={handleContinue} onCancel={handleDraft} />
      </div>
    </div>
  )
}

export default AddIngredient
