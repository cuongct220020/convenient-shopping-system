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
}
