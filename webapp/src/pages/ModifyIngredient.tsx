import { useNavigate, useLocation } from 'react-router-dom'
import { IngredientForm } from '../components/IngredientForm'

const ModifyIngredient = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const item = location.state?.item

  const handleSave = () => {
    // Here you would typically save the changes
    navigate('/ingredient-list')
  }

  const handleCancel = () => {
    navigate('/view-ingredient', { state: { item } })
  }

  if (!item) {
    return <div>Loading...</div>
  }

  return (
    <div
      className="flex items-center justify-center bg-gray-700 p-4"
      style={{ width: '1440px', height: '1024px' }}
    >
      <IngredientForm
        initialData={item}
        onSubmit={handleSave}
        onCancel={handleCancel}
        submitLabel="Lưu"
      />
    </div>
  )
}

export default ModifyIngredient
