import { err, ok, Result } from 'neverthrow'

export class Time {
  public static get now(): number {
    return Math.floor(Date.now() / 1000)
  }

  public static MM_SS(time: number, opts?: { clamped?: boolean }) {
    const max = 59 * 60 + 59
    if (opts?.clamped) {
      time = Math.min(time, max)
    }
    return `${Math.floor(time / 60)
      .toString()
      .padStart(2, '0')}:${(time % 60).toString().padStart(2, '0')}`
  }

  public static DD_MM_YYYY(time: number | Date) {
    if (typeof time === 'number') {
      time = new Date(time * 1000)
    }
    const dd = time.getDate().toString().padStart(2, '0')
    const mm = (time.getMonth() + 1).toString().padStart(2, '0')
    const yyyy = time.getFullYear()
    return `${dd}/${mm}/${yyyy}`
  }

  public static isSameDay(a: Date, b: Date) {
    return (
      a.getDate() === b.getDate() &&
      a.getMonth() === b.getMonth() &&
      a.getFullYear() === b.getFullYear()
    )
  }

  /**
   * Parse time string to minutes
   * Accepts: "1h", "1 h", "1 giờ", "1 tiếng", "1 hour", "30m", "30 phút", "1 giây", etc.
   * Combinations: "1h 30m", "1 giờ 30 phút" (each unit appears at most once)
   * @param input Time string to parse
   * @returns Result containing total minutes or error message
   */
  public static parseTimeToMinutes(
    input: string,
    opts?: { keepFractional?: boolean }
  ): Result<number, string> {
    if (!input || typeof input !== 'string') {
      return err('Vui lòng nhập thời gian')
    }

    const trimmed = input.trim().toLowerCase()

    if (trimmed === '') {
      err('Vui lòng nhập thời gian')
    }

    // Unit patterns: (value) (optional space) (unit)
    const unitPatterns = [
      {
        regex: /(\d+(?:\.\d+)?)\s*(?:giờ|tiếng|h|hour|hours)/gi,
        unit: 'hour',
        minutes: 60
      },
      {
        regex: /(\d+(?:\.\d+)?)\s*(?:phút|p|m|min|minute|minutes)/gi,
        unit: 'minute',
        minutes: 1
      },
      {
        regex: /(\d+(?:\.\d+)?)\s*(?:giây|s|sec|second|seconds)/gi,
        unit: 'second',
        minutes: 1 / 60
      }
    ]

    let totalMinutes = 0
    const usedUnits = new Set<string>()
    let hasMatch = false

    for (const pattern of unitPatterns) {
      const matches = [...trimmed.matchAll(pattern.regex)]

      if (matches.length > 0) {
        if (usedUnits.has(pattern.unit)) {
          return err(
            `Đơn vị ${pattern.unit} không được xuất hiện nhiều hơn một lần`
          )
        }

        if (matches.length > 1) {
          return err(
            `Đơn vị ${pattern.unit} không được xuất hiện nhiều hơn một lần`
          )
        }

        hasMatch = true
        const value = parseFloat(matches[0][1])

        if (isNaN(value) || value < 0) {
          return err('Giá trị phải là số dương')
        }

        totalMinutes += value * pattern.minutes
        usedUnits.add(pattern.unit)
      }
    }

    if (!hasMatch) {
      return err(
        'Định dạng không hợp lệ. Sử dụng: "1h 30m", "1 giờ 30 phút", v.v.'
      )
    }

    if (totalMinutes === 0) {
      return err('Thời gian phải lớn hơn 0')
    }

    return opts?.keepFractional
      ? ok(totalMinutes)
      : ok(Math.round(totalMinutes))
  }

  /**
   * Format seconds to readable duration
   * Converts to hours, minutes, seconds format (highest to lowest units)
   * Stops when a unit is 0 or very close to 0 (using epsilon)
   * @param seconds Total seconds to format
   * @param opts Optional epsilon threshold (default 0.01)
   * @returns Formatted duration string (e.g., "1h 30m", "1 giờ 30 phút")
   */
  public static formatDuration(
    seconds: number,
    opts?: { eps?: number; english?: boolean }
  ): string {
    const eps = opts?.eps ?? 0.01
    const vietnamese = !opts?.english

    if (!seconds || seconds <= 0) {
      return ''
    }

    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    const parts: string[] = []

    if (hours > eps) {
      parts.push(vietnamese ? `${hours} giờ` : `${hours}h`)
    }

    if (minutes > eps) {
      parts.push(vietnamese ? `${minutes} phút` : `${minutes}m`)
    }

    if (secs > eps && parts.length < 2) {
      // Only show seconds if we have space and seconds is significant
      parts.push(
        vietnamese ? `${Math.round(secs)} giây` : `${Math.round(secs)}s`
      )
    }

    return parts.join(' ') || '0'
  }
}
