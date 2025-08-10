'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@/stores'
import { 
  Search, 
  Bell, 
  User, 
  Settings, 
  LogOut, 
  Menu,
  ChevronDown,
  Sun,
  Moon,
  HelpCircle,
  Command
} from 'lucide-react'

export function Header() {
  const [showSearch, setShowSearch] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
  }

  const mockNotifications = [
    { id: 1, title: 'Nowy plan treści został utworzony', time: '2 min temu', type: 'success' },
    { id: 2, title: 'Zadanie AI zostało ukończone', time: '5 min temu', type: 'info' },
    { id: 3, title: 'Wariant treści wymaga akceptacji', time: '10 min temu', type: 'warning' }
  ]

  return (
    <motion.header 
      initial={{ y: -64, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="fixed top-0 left-64 right-0 h-16 bg-background/80 backdrop-blur-md border-b border-border z-40"
    >
      <div className="h-full px-6 flex items-center justify-between">
        {/* Header Left */}
        <div className="flex items-center gap-4">
          {/* Mobile Navigation Toggle */}
          <button className="lg:hidden p-2 rounded-md hover:bg-accent transition-colors">
            <Menu size={20} className="text-muted-foreground" />
          </button>

          {/* Search */}
          <div className="relative">
            <motion.div
              className="flex items-center"
              animate={{ width: showSearch ? 300 : 40 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
            >
              {showSearch ? (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center w-full bg-muted rounded-md border border-input px-3 py-2"
                >
                  <Search size={18} className="text-muted-foreground mr-2" />
                  <input
                    type="text"
                    placeholder="Szukaj w aplikacji... (Ctrl+K)"
                    className="flex-1 bg-transparent outline-none text-sm text-foreground placeholder-muted-foreground"
                    autoFocus
                    onBlur={() => setShowSearch(false)}
                  />
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Command size={12} />
                    <span>K</span>
                  </div>
                </motion.div>
              ) : (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowSearch(true)}
                  className="p-2 rounded-md bg-muted hover:bg-accent transition-colors"
                >
                  <Search size={18} className="text-muted-foreground" />
                </motion.button>
              )}
            </motion.div>
          </div>
        </div>

        {/* Header Right */}
        <div className="flex items-center gap-3">
          {/* Quick Actions */}
          <div className="hidden md:flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 rounded-md bg-primary/10 hover:bg-primary/20 text-primary transition-all duration-200"
              title="Pomoc"
            >
              <HelpCircle size={18} />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 rounded-md bg-yellow-50 hover:bg-yellow-100 text-yellow-600 transition-all duration-200"
              title="Tryb ciemny"
            >
              <Moon size={18} />
            </motion.button>
          </div>

          {/* Notifications */}
          <div className="relative">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-md bg-muted hover:bg-accent transition-colors"
            >
              <Bell size={18} className="text-muted-foreground" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full flex items-center justify-center">
                <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
              </span>
            </motion.button>

            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 top-full mt-2 w-80 bg-card rounded-lg shadow-soft-lg border border-border z-50"
                >
                  <div className="p-4 border-b border-border">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-foreground">Powiadomienia</h3>
                      <span className="text-xs text-muted-foreground">{mockNotifications.length} nowe</span>
                    </div>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    {mockNotifications.map((notification) => (
                      <motion.div
                        key={notification.id}
                        whileHover={{ opacity: 0.8 }}
                        className="p-4 border-b border-border last:border-b-0 cursor-pointer hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                            notification.type === 'success' ? 'bg-green-500' :
                            notification.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                          }`}></div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-foreground mb-1">
                              {notification.title}
                            </p>
                            <p className="text-xs text-muted-foreground">{notification.time}</p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  <div className="p-3 border-t border-border">
                    <button className="w-full text-center text-sm text-primary hover:text-primary/80 font-medium">
                      Zobacz wszystkie powiadomienia
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* User Profile */}
          <div className="relative">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-2 p-2 rounded-md hover:bg-accent transition-colors"
            >
              <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
                <span className="text-primary-foreground text-sm font-bold">
                  {user?.username?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-foreground leading-none">
                  {user?.username || 'Użytkownik'}
                </p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <ChevronDown size={16} className="text-muted-foreground" />
            </motion.button>

            <AnimatePresence>
              {showProfile && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 top-full mt-2 w-56 bg-card rounded-lg shadow-soft-lg border border-border z-50"
                >
                  <div className="p-4 border-b border-border">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary rounded-md flex items-center justify-center">
                        <span className="text-primary-foreground font-bold">
                          {user?.username?.charAt(0) || 'U'}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-foreground truncate">
                          {user?.username || 'Użytkownik'}
                        </p>
                        <p className="text-sm text-muted-foreground truncate">{user?.email}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-2">
                    <motion.button
                      whileHover={{ opacity: 0.9 }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-left transition-colors hover:bg-accent"
                    >
                      <User size={16} className="text-muted-foreground" />
                      <span className="text-sm text-foreground">Profil użytkownika</span>
                    </motion.button>
                    
                    <motion.button
                      whileHover={{ opacity: 0.9 }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-left transition-colors hover:bg-accent"
                    >
                      <Settings size={16} className="text-muted-foreground" />
                      <span className="text-sm text-foreground">Ustawienia</span>
                    </motion.button>
                  </div>

                  <div className="p-2 border-t border-border">
                    <motion.button
                      whileHover={{ opacity: 0.9 }}
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-left transition-colors text-destructive hover:bg-destructive/10"
                    >
                      <LogOut size={16} />
                      <span className="text-sm">Wyloguj się</span>
                    </motion.button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.header>
  )
}
