interface FormInputProps {
  label: string
  id?: string
  type?: 'text' | 'number'
  value?: string | number
  placeholder?: string
  readOnly?: boolean
  className?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  variant?: 'nutrition' | 'styled'
  containerClassName?: string
  showEmptyState?: boolean
  emptyStateText?: string
}

export const FormInput = ({
  label,
  id,
  type = 'text',
  value,
  placeholder,
  readOnly = false,
  className = '',
  onChange,
  variant = 'styled',
  containerClassName = '',
  showEmptyState = false,
  emptyStateText = 'Chưa có thông tin'
}: FormInputProps) => {
  const getDisplayValue = (val: string | number | undefined) => {
    if (readOnly && (val === undefined || val === null || val === '')) {
      return emptyStateText
    }
    return val
  }

  const getInputType = (val: string | number | undefined, defaultType: string) => {
    if (readOnly && (val === undefined || val === null || val === '')) {
      return 'text'
    }
    return defaultType
  }

  const displayValue = value === undefined || value === null ? '' : value

  // Nutrition variant styling (from NutritionInputField)
  if (variant === 'nutrition') {
    const nutritionInputClass = `w-full p-2 border-b border-gray-300 text-gray-700 ${
      readOnly ? 'bg-gray-50 focus:outline-none' : 'focus:outline-none focus:border-gray-400'
    } ${className}`

    return (
      <div className={containerClassName}>
        <label className="block text-gray-700 font-bold mb-1">
          {label}
        </label>
        <input
          type={getInputType(value, 'number')}
          placeholder={readOnly ? '' : placeholder || '0'}
          className={nutritionInputClass}
          readOnly={readOnly}
          defaultValue={getDisplayValue(value)}
          onChange={onChange}
        />
      </div>
    )
  }

  // Styled variant (from StyledInputField)
  const styledInputClass = `mt-1 block w-full border-b border-gray-300 p-2 text-lg focus:border-rose-500 focus:outline-none ${
    showEmptyState && !readOnly && !displayValue ? 'text-gray-400 font-normal italic' : ''
  } ${
    readOnly ? 'bg-gray-50' : ''
  } ${className}`

  return (
    <div className={containerClassName}>
      <label htmlFor={id} className="block text-sm font-bold text-gray-700">
        {label}
      </label>
      <input
        type={type}
        id={id}
        value={displayValue}
        placeholder={placeholder}
        onChange={onChange}
        readOnly={readOnly}
        className={styledInputClass}
      />
    </div>
  )
}