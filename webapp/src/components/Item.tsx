import React from 'react'

interface ItemProps {
  name: string
  category: string
  image: string
  onClick?: () => void
}

interface UserItemProps {
  name: string
  username: string
  email: string
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

const UserItem: React.FC<UserItemProps> = ({ name, username, email, image, onClick }) => {
  return (
    <div
      className="cursor-pointer overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md"
      onClick={onClick}
    >
      {/* Image Area */}
      <div className="relative h-32 w-full overflow-hidden bg-gray-100 flex items-center justify-center">
        <img
          src={image}
          alt={name}
          className="w-full h-full object-cover rounded-t-xl"
        />
      </div>

      {/* Content Area */}
      <div className="p-3">
        <h3 className="truncate text-sm font-bold text-gray-900">{name}</h3>
        <p className="truncate text-xs text-gray-600">@{username}</p>
        <p className="truncate text-xs text-gray-500">{email}</p>
      </div>
    </div>
  )
}

export { UserItem }
export default Item
