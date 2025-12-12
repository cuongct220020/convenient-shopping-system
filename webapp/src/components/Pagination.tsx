import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showPreviousNext?: boolean
  maxVisiblePages?: number
  className?: string
}

/**
 * Pagination Component
 * Standard pagination component following common patterns
 */
export const Pagination = ({
  currentPage,
  totalPages,
  onPageChange,
  showPreviousNext = true,
  maxVisiblePages = 5,
  className = ''
}: PaginationProps) => {
  const getVisiblePages = () => {
    const pages: number[] = []
    const halfVisible = Math.floor(maxVisiblePages / 2)

    let startPage = Math.max(1, currentPage - halfVisible)
    const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)

    // Adjust start page if we're near the end
    if (endPage - startPage < maxVisiblePages - 1) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1)
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i)
    }

    return { startPage, endPage, pages }
  }

  const { startPage, endPage, pages } = getVisiblePages()

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page)
    }
  }

  if (totalPages <= 1) return null

  return (
    <div
      className={`flex items-center justify-center space-x-2 text-sm ${className}`}
    >
      {showPreviousNext && (
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          className={`flex items-center px-3 py-1 text-sm font-semibold hover:text-[#c93045] disabled:cursor-not-allowed disabled:opacity-50 ${
            currentPage === 1 ? 'cursor-not-allowed opacity-50' : ''
          }`}
        >
          <ChevronLeft size={16} className="mr-1" />
          Previous
        </button>
      )}

      {/* Show first page and ellipsis if needed */}
      {startPage > 1 && (
        <>
          <button
            onClick={() => handlePageChange(1)}
            className="w-8 h-8 flex items-center justify-center rounded text-sm font-medium bg-transparent text-gray-600 hover:bg-gray-100 hover:text-rose-500 transition-all duration-200"
          >
            1
          </button>
          {startPage > 2 && <span className="px-2">...</span>}
        </>
      )}

      {/* Visible page numbers */}
      {pages.map((page) => (
        <button
          key={page}
          onClick={() => handlePageChange(page)}
          className={`w-8 h-8 flex items-center justify-center rounded text-sm font-medium transition-all duration-200 ${
            page === currentPage
              ? 'bg-[#c93045] text-white hover:bg-[#b02a3d] shadow-md shadow-red-200'
              : 'bg-transparent text-gray-600 hover:bg-gray-100 hover:text-rose-500'
          }`}
        >
          {page}
        </button>
      ))}

      {/* Show last page and ellipsis if needed */}
      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="px-2">...</span>}
          <button
            onClick={() => handlePageChange(totalPages)}
            className="w-8 h-8 flex items-center justify-center rounded text-sm font-medium bg-transparent text-gray-600 hover:bg-gray-100 hover:text-rose-500 transition-all duration-200"
          >
            {totalPages}
          </button>
        </>
      )}

      {showPreviousNext && (
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`flex items-center px-3 py-1 text-sm font-semibold hover:text-[#c93045] disabled:cursor-not-allowed disabled:opacity-50 ${
            currentPage === totalPages ? 'cursor-not-allowed opacity-50' : ''
          }`}
        >
          Next
          <ChevronRight size={16} className="ml-1" />
        </button>
      )}
    </div>
  )
}
