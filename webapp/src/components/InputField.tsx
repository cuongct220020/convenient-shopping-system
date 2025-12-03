import { InputHTMLAttributes, forwardRef } from 'react'

interface InputFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  subLabel?: string
  error?: string | null
  icon?: React.ReactNode
  containerClassName?: string
  labelClassName?: string
  inputClassName?: string
  errorClassName?: string
}

/**
 * InputField Component
 * A reusable input field with label, error handling, and icon support
 */
export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
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
      className,
      ...props
    },
    ref
  ) => {
    return (
      <div className={`space-y-2 ${containerClassName}`}>
        {label && (
          <label
            htmlFor={props.id}
            className={`block text-sm font-medium text-gray-700 ${labelClassName}`}
          >
            {label}
            {subLabel && (
              <span className="ml-1 text-xs text-gray-500">{subLabel}</span>
            )}
          </label>
        )}

        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {icon}
            </div>
          )}

          <input
            ref={ref}
            className={`
            w-full rounded-lg border border-gray-300 px-3 py-2
            focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-300
            disabled:cursor-not-allowed disabled:bg-gray-100
            ${icon ? 'pl-10' : ''}
            ${error ? 'border-red-500' : ''}
            ${inputClassName}
            ${className}
          `}
            {...props}
          />
        </div>

        {error && (
          <p className={`text-sm text-red-600 ${errorClassName}`}>{error}</p>
        )}
      </div>
    )
  }
)

InputField.displayName = 'InputField'
