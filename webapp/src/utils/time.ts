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
}
