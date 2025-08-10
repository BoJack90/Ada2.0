'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay } from 'date-fns'
import { pl } from 'date-fns/locale'
import 'react-big-calendar/lib/css/react-big-calendar.css'

const locales = {
  'pl': pl,
}

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
})

interface Event {
  id: number
  title: string
  start: Date
  end: Date
  resource?: any
}

export function CalendarView() {
  const [events, setEvents] = useState<Event[]>([
    {
      id: 1,
      title: 'Spotkanie zespołu',
      start: new Date(2025, 6, 10, 10, 0),
      end: new Date(2025, 6, 10, 11, 0),
    },
    {
      id: 2,
      title: 'Przegląd kodu',
      start: new Date(2025, 6, 11, 14, 0),
      end: new Date(2025, 6, 11, 15, 30),
    },
    {
      id: 3,
      title: 'Demo dla klienta',
      start: new Date(2025, 6, 12, 16, 0),
      end: new Date(2025, 6, 12, 17, 0),
    },
  ])

  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [showEventForm, setShowEventForm] = useState(false)

  const handleSelectEvent = (event: Event) => {
    setSelectedEvent(event)
  }

  const handleSelectSlot = ({ start, end }: { start: Date; end: Date }) => {
    const title = window.prompt('Tytuł wydarzenia:')
    if (title) {
      const newEvent: Event = {
        id: events.length + 1,
        title,
        start,
        end,
      }
      setEvents([...events, newEvent])
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Kalendarz</h2>
        <motion.button
          onClick={() => setShowEventForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Dodaj wydarzenie
        </motion.button>
      </div>

      <motion.div
        className="h-96"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          onSelectEvent={handleSelectEvent}
          onSelectSlot={handleSelectSlot}
          selectable
          style={{ height: '100%' }}
          views={['month', 'week', 'day']}
          step={30}
          showMultiDayTimes
          components={{
            event: ({ event }) => (
              <motion.div
                className="p-1 text-xs bg-blue-100 text-blue-800 rounded"
                whileHover={{ scale: 1.05 }}
              >
                {event.title}
              </motion.div>
            ),
          }}
        />
      </motion.div>

      {selectedEvent && (
        <motion.div
          className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3 className="font-medium text-gray-900 mb-2">Szczegóły wydarzenia</h3>
          <p><strong>Tytuł:</strong> {selectedEvent.title}</p>
          <p><strong>Start:</strong> {selectedEvent.start.toLocaleString()}</p>
          <p><strong>Koniec:</strong> {selectedEvent.end.toLocaleString()}</p>
          <button
            onClick={() => setSelectedEvent(null)}
            className="mt-2 px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            Zamknij
          </button>
        </motion.div>
      )}
    </div>
  )
}
