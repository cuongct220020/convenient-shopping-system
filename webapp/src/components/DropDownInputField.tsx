import { forwardRef, useState, useRef, useEffect } from 'react'

interface DropdownOption {
  value: string
  label: string
}

interface DropdownInputFieldProps {
  label?: string
  subLabel?: string
  error?: string | null
  icon?: React.ReactNode
  containerClassName?: string
  labelClassName?: string
  inputClassName?: string
  errorClassName?: string
  options: DropdownOption[]
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  id?: string
}

/**
 * DropdownInputField Component
 * A reusable dropdown field with label, error handling, and icon support
 */
export const DropdownInputField = forwardRef<
  HTMLDivElement,
  DropdownInputFieldProps
>(
  (
    {
      label,
      subLabel,
      error,
      icon,
      containerClassName = '',
      labelClassName = '',
      inputClassName = '',
      errorClassName = '',
      options,
      value,
      onChange,
      placeholder = 'Select an option',
      disabled = false,
      id
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

    const selectedOption = options.find((opt) => opt.value === value)

    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (
          dropdownRef.current &&
          !dropdownRef.current.contains(event.target as Node)
        ) {
          setIsOpen(false)
        }
      }

      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleSelect = (optionValue: string) => {
      onChange?.(optionValue)
      setIsOpen(false)
    }

    return (
      <div ref={ref} className={`space-y-2 ${containerClassName}`}>
        {label && (
          <label
            htmlFor={id}
            className={`block text-sm font-medium text-gray-700 ${labelClassName}`}
          >
            {label}
            {subLabel && (
              <span className="ml-1 text-xs text-gray-500">{subLabel}</span>
            )}
          </label>
        )}

        <div className="relative" ref={dropdownRef}>
          {icon && (
            <div className="absolute left-3 top-1/2 z-10 -translate-y-1/2 text-gray-400">
              {icon}
            </div>
          )}

          <button
            type="button"
            id={id}
            disabled={disabled}
            onClick={() => !disabled && setIsOpen(!isOpen)}
            className={`
              w-full rounded-lg border border-gray-300 px-3 py-2
              text-left
              focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-300
              disabled:cursor-not-allowed disabled:bg-gray-100
              ${icon ? 'pl-10' : ''}
              ${error ? 'border-red-500' : ''}
              ${!selectedOption ? 'text-gray-400' : 'text-gray-900'}
              ${inputClassName}
            `}
          >
            <span className="flex items-center justify-between">
              <span className="truncate">
                {selectedOption ? selectedOption.label : placeholder}
              </span>
              <svg
                className={`size-5 text-gray-400 transition-transform ${
                  isOpen ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </span>
          </button>

          {isOpen && !disabled && (
            <div className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-300 bg-white shadow-lg">
              {options.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleSelect(option.value)}
                  className={`
                    w-full px-3 py-2 text-left hover:bg-gray-100
                    ${option.value === value ? 'bg-gray-50 font-medium' : ''}
                    first:rounded-t-lg last:rounded-b-lg
                  `}
                >
                  {option.label}
                </button>
              ))}
              {options.length === 0 && (
                <div className="px-3 py-2 text-sm text-gray-500">
                  No options available
                </div>
              )}
            </div>
          )}
        </div>

        {error && (
          <p className={`text-sm text-red-600 ${errorClassName}`}>{error}</p>
        )}
      </div>
    )
  }
)

DropdownInputField.displayName = 'DropdownInputField'
