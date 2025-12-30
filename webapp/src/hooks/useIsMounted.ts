import { useEffect, useRef } from 'react'

// TODO: This hook combats async handler still operating while component is unmounted
//
// Normal case: Mounts -> handler starts -> unmounts -> handler checks this ref -> handler stops
// Edge case: Mounts -> handler starts -> unmounts -> REMOUNTS -> handler keeps running with stale data
export function useIsMounted() {
  const isMounted = useRef(true)
  useEffect(() => {
    isMounted.current = true
    return () => {
      isMounted.current = false
    }
  }, [])
  return isMounted
}
