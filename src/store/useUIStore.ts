import { create } from 'zustand'

interface UIState {
  navbarScrolled: boolean
  mobileMenuOpen: boolean
  setNavbarScrolled: (v: boolean) => void
  setMobileMenuOpen: (v: boolean) => void
}

export const useUIStore = create<UIState>((set) => ({
  navbarScrolled: false,
  mobileMenuOpen: false,
  setNavbarScrolled: (v) => set({ navbarScrolled: v }),
  setMobileMenuOpen: (v) => set({ mobileMenuOpen: v }),
}))
