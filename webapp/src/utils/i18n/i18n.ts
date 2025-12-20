import { i18nKeys } from './keys'
import { vi } from './vi'

const langs = {
  vi
}

export class i18n {
  private dict: Record<i18nKeys, string> | null = null

  public setLang(lang: keyof typeof langs) {
    this.dict = langs[lang]
  }

  public t(key: i18nKeys): string {
    if (!this.dict) return `i18n: ${key}`
    return this.dict[key]
  }

  private static instance = new i18n()
  public static t(key: i18nKeys): string {
    return this.instance.t(key)
  }

  public static init(lang: keyof typeof langs) {
    this.instance.setLang(lang)
  }
}
