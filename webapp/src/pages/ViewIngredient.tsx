import { Check, Edit, Trash2 } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Button } from '../components/Button'
import { IngredientForm } from '../components/IngredientForm'

const ViewIngredient = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const item = location.state?.item

  const handleBack = () => {
    navigate('/ingredient-list')
  }

  const handleEdit = () => {
    navigate('/modify-ingredient', { state: { item } })
  }

  const handleDelete = () => {
    navigate('/ingredient-list')
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
    <div
      className="flex items-center justify-center bg-gray-700 p-4"
      style={{ width: '1440px', height: '1024px' }}
    >
      <IngredientForm
        initialData={item}
        readOnly={true}
        actions={customActions}
      />
    </div>
  )
}

export default ViewIngredient