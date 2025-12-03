import React from 'react'

interface ItemProps {
  name: string
  category: string
  image: string
  onClick?: () => void
}

const Item: React.FC<ItemProps> = ({ name, category, image, onClick }) => {
  return (
    <div
      className="cursor-pointer overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md"
      onClick={onClick}
    >
      {/* Image Area */}
      <div className="relative h-32 w-full overflow-hidden bg-gray-100">
        <img src={image} alt={name} className="size-full object-cover" />
      </div>

      {/* Content Area */}
      <div className="p-3">
        <div className="flex items-center justify-between">
          <h3 className="truncate text-sm font-bold text-gray-900">{name}</h3>
          <span className="truncate text-xs text-gray-500">{category}</span>
        </div>
      </div>
    </div>
  )
}

export default Item
