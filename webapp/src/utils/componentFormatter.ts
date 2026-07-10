/**
 * Format dish quantity (just number, rounded to 1 decimal if needed)
 */
export const formatDishQuantity = (quantity: number): string => {
  if (Number.isSafeInteger(quantity)) {
    return quantity.toString()
  }
  return quantity.toFixed(1)
}

/**
 * Format ingredient quantity with unit conversion
 * Handles g↔kg, ml↔L conversions based on value
 */
export const formatIngredientQuantity = (
  quantity: number,
  unit: string | null | undefined
): string => {
  const formattedQty = formatDishQuantity(quantity)
  if (!unit) {
    return formattedQty
  }

  const normalizedUnit = unit.toLowerCase().trim()

  // Gram conversions
  if (normalizedUnit === 'g') {
    if (quantity >= 1000) {
      return `${formatDishQuantity(quantity / 1000)} kg`
    }
    if (quantity < 1) {
      return `${formatDishQuantity(quantity * 1000)} mg`
    }
    return `${formattedQty} g`
  }

  // Milligram conversions
  if (normalizedUnit === 'mg') {
    if (quantity >= 1000000) {
      return `${formatDishQuantity(quantity / 1000000)} kg`
    }
    if (quantity >= 1000) {
      return `${formatDishQuantity(quantity / 1000)} g`
    }
    return `${formattedQty} mg`
  }

  // Kilogram conversions
  if (normalizedUnit === 'kg') {
    if (quantity < 1) {
      return `${formatDishQuantity(quantity * 1000)} g`
    }
    return `${formattedQty} kg`
  }

  // Milliliter conversions
  if (normalizedUnit === 'ml') {
    if (quantity >= 1000) {
      return `${formatDishQuantity(quantity / 1000)} L`
    }
    return `${formattedQty} ml`
  }

  // Liter conversions
  if (normalizedUnit === 'l' || normalizedUnit === 'liter') {
    if (quantity < 1) {
      return `${formatDishQuantity(quantity * 1000)} ml`
    }
    return `${formattedQty} L`
  }

  // Default: just number with space and unit
  return `${formattedQty} ${unit}`
}
