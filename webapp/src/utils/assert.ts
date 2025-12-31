type AssertMode = 'alert' | 'log' | 'off' | 'throw'
let globalMode: AssertMode = 'off'

export function initAssert(mode: AssertMode) {
  globalMode = mode
}

export function assert(cond: boolean, message?: string): asserts cond is true {
  if (globalMode === 'off') return
  if (cond) return
  message = `ASSERTION FAILED: ${message ?? 'No message'}`
  switch (globalMode) {
    case 'alert':
      alert(message)
      break
    case 'log':
      console.error(message)
      break
    case 'throw':
      throw new Error(message)
    default:
      throw new Error('Unhandled assertion mode: ' + globalMode)
  }
}
