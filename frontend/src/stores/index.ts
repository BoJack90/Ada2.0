import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, Organization } from '@/types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (token: string, user: User) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('auth_token', token)
        }
        set({ token, user, isAuthenticated: true })
      },
      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token')
        }
        set({ token: null, user: null, isAuthenticated: false })
      },
      setUser: (user: User) => set({ user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

interface OrganizationState {
  currentOrganization: Organization | null
  organizations: Organization[]
  setCurrentOrganization: (org: Organization | null) => void
  setOrganizations: (orgs: Organization[]) => void
  addOrganization: (org: Organization) => void
  updateOrganization: (id: number, updatedOrg: Organization) => void
  deleteOrganization: (id: number) => void
}

export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set) => ({
      currentOrganization: null,
      organizations: [],
      setCurrentOrganization: (org) => set({ currentOrganization: org }),
      setOrganizations: (orgs) => set({ organizations: orgs }),
      addOrganization: (org) => set((state) => ({ 
        organizations: [...state.organizations, org] 
      })),
      updateOrganization: (id, updatedOrg) => set((state) => ({
        organizations: state.organizations.map(org => 
          org.id === id ? updatedOrg : org
        )
      })),
      deleteOrganization: (id) => set((state) => ({
        organizations: state.organizations.filter(org => org.id !== id),
        currentOrganization: state.currentOrganization?.id === id ? null : state.currentOrganization
      })),
    }),
    {
      name: 'organization-storage',
      partialize: (state) => ({ 
        currentOrganization: state.currentOrganization,
        organizations: state.organizations 
      }),
    }
  )
)
