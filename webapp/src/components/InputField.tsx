import { InputHTMLAttributes, TextareaHTMLAttributes, forwardRef } from 'react'

interface InputFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string
  subLabel?: string
  error?: string | null
  icon?: React.ReactNode
  containerClassName?: string
  labelClassName?: string
  inputClassName?: string
  errorClassName?: string
  textarea?: boolean
  textareaRows?: number
}

interface TextareaFieldProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'size'> {
  label?: string
  subLabel?: string
  error?: string | null
  icon?: React.ReactNode
  containerClassName?: string
  labelClassName?: string
  inputClassName?: string
  errorClassName?: string
  textarea?: true
  textareaRows?: number
}

/**
 * InputField Component
 * A reusable input field with label, error handling, and icon support.
 * Can render as either an input or textarea based on the `textarea` prop.
 */
export const InputField = forwardRef<HTMLInputElement | HTMLTextAreaElement, InputFieldProps>(
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
      textarea = false,
      textareaRows = 3,
      className,
      ...props
    },
    ref
  ) => {
    const inputElementClass = `
      w-full rounded-lg border border-gray-300 px-3 py-2
      focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-300
      disabled:cursor-not-allowed disabled:bg-gray-100
      ${icon ? 'pl-10' : ''}
      ${error ? 'border-red-500' : ''}
      ${inputClassName}
      ${className}
    `

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
          {icon && !textarea && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {icon}
            </div>
          )}
          {icon && textarea && (
            <div className="absolute left-3 top-3 text-gray-400">
              {icon}
            </div>
          )}

          {textarea ? (
            <textarea
              ref={ref as React.RefObject<HTMLTextAreaElement>}
              rows={textareaRows}
              className={inputElementClass}
              {...(props as TextareaHTMLAttributes<HTMLTextAreaElement>)}
            />
          ) : (
            <input
              ref={ref as React.RefObject<HTMLInputElement>}
              className={inputElementClass}
              {...(props as InputHTMLAttributes<HTMLInputElement>)}
            />
          )}
        </div>

        {error && (
          <p className={`text-sm text-red-600 ${errorClassName}`}>{error}</p>
        )}
      </div>
    )
  }
)

InputField.displayName = 'InputField'
