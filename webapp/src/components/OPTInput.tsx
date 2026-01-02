import React, { useRef, useState, useEffect } from 'react'

interface OtpInputProps {
  length?: number
  onComplete?: (otp: string) => void
  onChange?: (otp: string) => void
  error?: boolean
}

export const OPTInput = ({
  length = 6,
  onComplete = undefined,
  onChange = undefined,
  error = false
}: OtpInputProps) => {
  const [otp, setOtp] = useState<string[]>(new Array(length).fill(''))
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  useEffect(() => {
    // Focus the first input on mount
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus()
    }
  }, [])

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    index: number
  ) => {
    const value = e.target.value
    if (isNaN(Number(value))) return // Only allow numbers

    const newOtp = [...otp]
    // Take the last character entered (in case they paste or type fast)
    newOtp[index] = value.substring(value.length - 1)
    setOtp(newOtp)

    // Call onComplete if all fields are filled
    const combinedOtp = newOtp.join('')
    onChange?.(combinedOtp)
    if (combinedOtp.length === length) {
      onComplete?.(combinedOtp)
    }

    // Move to next input if value is entered and it's not the last one
    if (value && index < length - 1 && inputRefs.current[index + 1]) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>,
    index: number
  ) => {
    // Handle Backspace
    if (
      e.key === 'Backspace' &&
      !otp[index] &&
      index > 0 &&
      inputRefs.current[index - 1]
    ) {
      // If current is empty and backspace pressed, move to previous
      inputRefs.current[index - 1]?.focus()
    }
  }

  // Handle pasting (optional but good UX)
  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text/plain').slice(0, length)
    if (!/^\d+$/.test(pastedData)) return // Only allow digits

    const newOtp = [...otp]
    pastedData.split('').forEach((char, idx) => {
      newOtp[idx] = char
    })
    setOtp(newOtp)

    const combinedOtp = newOtp.join('')
    onChange?.(combinedOtp)
    if (combinedOtp.length === length) {
      onComplete?.(combinedOtp)
    }

    // Focus the slot after the pasted content
    const focusIndex = Math.min(pastedData.length, length - 1)
    inputRefs.current[focusIndex]?.focus()
  }

  return (
    <div className="my-8 flex justify-between gap-2" onPaste={handlePaste}>
      {otp.map((digit, index) => (
        <input
          key={index}
          type="text"
          maxLength={1}
          ref={(el) => (inputRefs.current[index] = el)}
          value={digit ? '*' : ''}
          // To hide the numbers like the image (using asterisks), you could change type to "password"
          // But standard OTP UX usually shows the number.
          // To visually match the image's grey boxes:
          className={`h-14 w-12 rounded-lg bg-gray-200 text-center text-2xl font-bold outline-none transition-all focus:cursor-text focus:border-2 focus:border-gray-600 focus:bg-gray-200 focus:ring-1 focus:ring-gray-300 ${
            digit ? 'text-gray-700' : 'text-transparent'
          } ${error ? 'border-2 border-red-500' : ''}`}
          onChange={(e) => handleChange(e, index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          inputMode="numeric" // Hints mobile browsers to show numeric keyboard
        />
      ))}
    </div>
  )
}
