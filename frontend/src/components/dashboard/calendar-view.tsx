'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Calendar, Clock, Plus, ChevronLeft, ChevronRight, Users, CheckSquare, Bell } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface CalendarEvent {
  id: string
  title: string
  date: Date
  time: string
  type: 'meeting' | 'task' | 'reminder'
}

export function CalendarView() {
  const toast = useToast()
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [events] = useState<CalendarEvent[]>([
    {
      id: '1',
      title: 'Team Meeting',
      date: new Date(),
      time: '10:00',
      type: 'meeting'
    },
    {
      id: '2',
      title: 'Project Review',
      date: new Date(),
      time: '14:30',
      type: 'task'
    },
    {
      id: '3',
      title: 'Content Review',
      date: new Date(),
      time: '16:00',
      type: 'reminder'
    }
  ])

  const getEventTypeStyles = (type: string) => {
    switch (type) {
      case 'meeting':
        return {
          bg: 'bg-gradient-to-br from-blue-50 to-indigo-50',
          border: 'border-blue-200',
          badge: 'bg-blue-500',
          icon: Users
        }
      case 'task':
        return {
          bg: 'bg-gradient-to-br from-emerald-50 to-teal-50',
          border: 'border-emerald-200',
          badge: 'bg-emerald-500',
          icon: CheckSquare
        }
      case 'reminder':
        return {
          bg: 'bg-gradient-to-br from-yellow-50 to-orange-50',
          border: 'border-yellow-200',
          badge: 'bg-yellow-500',
          icon: Bell
        }
      default:
        return {
          bg: 'bg-gradient-to-br from-gray-50 to-slate-50',
          border: 'border-gray-200',
          badge: 'bg-gray-500',
          icon: Calendar
        }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      {/* Modern Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-700 rounded-2xl p-8 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="p-3 bg-white/20 rounded-xl backdrop-blur-sm"
              >
                <Calendar className="h-8 w-8" />
              </motion.div>
              <div>
                <h1 className="text-3xl font-bold">Calendar</h1>
                <p className="text-purple-100 mt-2">Zarządzaj wydarzeniami i planuj pracę zespołu</p>
              </div>
            </div>
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => toast.info('Funkcja dodawania wydarzeń będzie dostępna wkrótce')}
              className="px-6 py-3 bg-white/20 rounded-xl backdrop-blur-sm hover:bg-white/30 transition-colors flex items-center space-x-2"
            >
              <Plus className="h-5 w-5" />
              <span>Add Event</span>
            </motion.button>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Calendar Widget */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="lg:col-span-2"
        >
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-6 text-white">
              <div className="flex justify-content-between align-items-center">
                <h2 className="text-xl font-semibold">Calendar View</h2>
                <div className="flex items-center space-x-3">
                  <motion.button 
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 bg-white/20 rounded-lg backdrop-blur-sm hover:bg-white/30 transition-colors"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </motion.button>
                  <span className="text-lg font-medium">
                    {selectedDate.toLocaleDateString('en-US', { 
                      month: 'long', 
                      year: 'numeric' 
                    })}
                  </span>
                  <motion.button 
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 bg-white/20 rounded-lg backdrop-blur-sm hover:bg-white/30 transition-colors"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </motion.button>
                </div>
              </div>
            </div>
            
            <div className="p-8">
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="text-center py-12 bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl border border-gray-100"
              >
                <Calendar size={80} className="text-blue-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Calendar Integration
                </h3>
                <p className="text-gray-600 mb-4">
                  Pełna funkcjonalność kalendarza będzie wkrótce dostępna
                </p>
                <p className="text-sm text-gray-500">
                  W przyszłych wersjach zostanie zintegrowany interaktywny kalendarz z pełną funkcjonalnością
                </p>
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Events Sidebar */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="space-y-6"
        >
          {/* Today's Events */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white">
              <h2 className="text-xl font-semibold">Today's Events</h2>
              <p className="text-emerald-100">Wydarzenia na dziś</p>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                {events.length > 0 ? (
                  events.map((event, index) => {
                    const styles = getEventTypeStyles(event.type)
                    const IconComponent = styles.icon
                    
                    return (
                      <motion.div 
                        key={event.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + index * 0.1 }}
                        whileHover={{ scale: 1.02, y: -2 }}
                        className={`border rounded-xl p-4 ${styles.border} ${styles.bg} hover:shadow-md transition-all duration-300`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 ${styles.badge} text-white rounded-lg`}>
                              <IconComponent className="h-4 w-4" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-gray-900">{event.title}</h3>
                              <div className="flex items-center text-sm text-gray-600">
                                <Clock className="h-4 w-4 mr-1" />
                                {event.time}
                              </div>
                            </div>
                          </div>
                          <span className={`px-3 py-1 ${styles.badge} text-white text-xs font-medium rounded-full`}>
                            {event.type}
                          </span>
                        </div>
                      </motion.div>
                    )
                  })
                ) : (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-center py-8 bg-gradient-to-br from-gray-50 to-slate-50 rounded-xl"
                  >
                    <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-500">No events for today</p>
                  </motion.div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Add Event */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
          >
            <div className="bg-gradient-to-r from-orange-500 to-red-600 p-6 text-white">
              <h2 className="text-xl font-semibold">Quick Add</h2>
              <p className="text-orange-100">Szybkie dodawanie wydarzeń</p>
            </div>
            
            <div className="p-6 space-y-3">
              <motion.button 
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => toast.info('Funkcja dodawania spotkań będzie dostępna wkrótce')}
                className="w-full p-3 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-xl border border-blue-200 transition-all duration-300 flex items-center space-x-3 group"
              >
                <div className="p-2 bg-blue-500 text-white rounded-lg group-hover:scale-110 transition-transform">
                  <Users className="h-4 w-4" />
                </div>
                <span className="font-medium text-blue-900">Add Meeting</span>
              </motion.button>
              
              <motion.button 
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => toast.info('Funkcja dodawania zadań będzie dostępna wkrótce')}
                className="w-full p-3 bg-gradient-to-r from-emerald-50 to-teal-50 hover:from-emerald-100 hover:to-teal-100 rounded-xl border border-emerald-200 transition-all duration-300 flex items-center space-x-3 group"
              >
                <div className="p-2 bg-emerald-500 text-white rounded-lg group-hover:scale-110 transition-transform">
                  <CheckSquare className="h-4 w-4" />
                </div>
                <span className="font-medium text-emerald-900">Add Task</span>
              </motion.button>
              
              <motion.button 
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => toast.info('Funkcja dodawania przypomnień będzie dostępna wkrótce')}
                className="w-full p-3 bg-gradient-to-r from-yellow-50 to-orange-50 hover:from-yellow-100 hover:to-orange-100 rounded-xl border border-yellow-200 transition-all duration-300 flex items-center space-x-3 group"
              >
                <div className="p-2 bg-yellow-500 text-white rounded-lg group-hover:scale-110 transition-transform">
                  <Bell className="h-4 w-4" />
                </div>
                <span className="font-medium text-yellow-900">Add Reminder</span>
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
