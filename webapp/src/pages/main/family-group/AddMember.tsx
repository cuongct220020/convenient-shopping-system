import React, { useState } from 'react'
import { UserPlus, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { InputField } from '../../../components/InputField'
import { Button } from '../../../components/Button'
import { groupService } from '../../../services/group'

interface AddMemberProps {
  groupId: string | undefined
  onMemberAdded: () => void
  onCancel: () => void
}

const AddMember = ({ groupId, onMemberAdded, onCancel }: AddMemberProps) => {
  const [identifier, setIdentifier] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{
    type: 'success' | 'error' | null
    text: string
  }>({ type: null, text: '' })

  const handleAddMember = async () => {
    const trimmed = identifier.trim()
    if (!trimmed) {
      setMessage({
        type: 'error',
        text: 'Vui lòng nhập email hoặc tên đăng nhập'
      })
      return
    }

    if (!groupId) {
      setMessage({ type: 'error', text: 'Không tìm thấy ID nhóm' })
      return
    }

    setIsLoading(true)
    setMessage({ type: null, text: '' })

    const result = await groupService.addMember(groupId, trimmed)

    result.match(
      () => {
        setMessage({ type: 'success', text: 'Đã thêm thành viên thành công!' })
        setIdentifier('')
        // Notify parent to refresh group data
        onMemberAdded()
        // Clear success message after 2 seconds so user can add more
        setTimeout(() => {
          setMessage({ type: null, text: '' })
        }, 2000)
      },
      (error) => {
        console.error('Failed to add member:', error)
        if (error.type === 'unauthorized') {
          setMessage({
            type: 'error',
            text: 'Bạn cần đăng nhập để thêm thành viên'
          })
        } else if (error.type === 'not-found') {
          setMessage({
            type: 'error',
            text: 'Không tìm thấy người dùng'
          })
        } else if (error.type === 'forbidden') {
          setMessage({
            type: 'error',
            text: 'Bạn không có quyền thêm thành viên'
          })
        } else if (error.type === 'conflict') {
          setMessage({
            type: 'error',
            text: 'Người dùng này đã là thành viên của nhóm'
          })
        } else {
          setMessage({ type: 'error', text: 'Không thể thêm thành viên' })
        }
      }
    )

    setIsLoading(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) {
      e.preventDefault()
      handleAddMember()
    }
  }

  return (
    <div>
      {/* Input Field */}
      <div className="mb-4">
        <InputField
          label="Email"
          subLabel="hoặc tên đăng nhập"
          labelClassName="after:content-['*'] after:ml-0.5 after:text-red-500"
          placeholder="Nhập email hoặc tên đăng nhập"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
      </div>

      {/* Success/Error Message */}
      {message.type && (
        <div
          className={`mb-4 flex items-center gap-2 rounded-lg border px-4 py-3 ${
            message.type === 'success'
              ? 'border-green-200 bg-green-50'
              : 'border-red-200 bg-red-50'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 size={20} className="shrink-0 text-green-600" />
          ) : (
            <XCircle size={20} className="shrink-0 text-red-600" />
          )}
          <span
            className={`text-sm ${
              message.type === 'success' ? 'text-green-700' : 'text-red-700'
            }`}
          >
            {message.text}
          </span>
        </div>
      )}

      {/* Buttons */}
      <div className="flex justify-center gap-3">
        <div className="">
          <Button
            variant={isLoading ? 'disabled' : 'primary'}
            onClick={handleAddMember}
            icon={isLoading ? Loader2 : undefined}
            size="fit"
            className="bg-[#C3485C] hover:bg-[#a83648]"
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Đang thêm...
              </>
            ) : (
              'Thêm thành viên'
            )}
          </Button>
        </div>
        <div className="">
          <Button
            variant={isLoading ? 'disabled' : 'secondary'}
            onClick={onCancel}
            size="fit"
            className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]"
          >
            Hủy
          </Button>
        </div>
      </div>
    </div>
  )
}

export default AddMember
