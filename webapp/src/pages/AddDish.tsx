import { useNavigate } from 'react-router-dom'
import { DishForm } from '../components/DishForm'
import DishList from './DishList'

const AddDish = () => {
  const navigate = useNavigate()

  const handleContinue = (dishData: any) => {
    console.log('Saving dish:', dishData)
    navigate('/dish-list')
  }

  const handleDraft = () => {
    navigate('/dish-list')
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
        <DishForm onSubmit={handleContinue} onCancel={handleDraft} />
      </div>
    </div>
  )
}

export default AddDish