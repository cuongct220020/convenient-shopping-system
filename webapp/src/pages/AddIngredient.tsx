import { useNavigate } from 'react-router-dom'
import { IngredientForm } from '../components/IngredientForm'

const AddIngredient = () => {
  const navigate = useNavigate()

  const handleContinue = () => {
    navigate('/ingredient-list')
  }

  const handleDraft = () => {
    navigate('/ingredient-list')
  }

  return (
    <div
      className="flex items-center justify-center bg-gray-700 p-4"
      style={{ width: '1440px', height: '1024px' }}
    >
      <IngredientForm onSubmit={handleContinue} onCancel={handleDraft} />
    </div>
  )
}

export default AddIngredient