'use client'

import { useState, useCallback, useMemo } from 'react'
import { Calendar, momentLocalizer, View, Event } from 'react-big-calendar'
import moment from 'moment'
import 'moment/locale/pl'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Calendar as CalendarIcon,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Linkedin,
  Facebook,
  Twitter,
  Globe,
  FileText,
  X
} from 'lucide-react'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { ScheduledPost, ContentVariant } from '@/types'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import 'react-big-calendar/lib/css/react-big-calendar.css'

// Ustaw lokalizację dla moment
moment.locale('pl')
const localizer = momentLocalizer(moment)

// Polski słownik dla kalendarza
const messages = {
  allDay: 'Cały dzień',
  previous: 'Poprzedni',
  next: 'Następny',
  today: 'Dziś',
  month: 'Miesiąc',
  week: 'Tydzień',
  day: 'Dzień',
  agenda: 'Agenda',
  date: 'Data',
  time: 'Czas',
  event: 'Wydarzenie',
  noEventsInRange: 'Brak wydarzeń w tym zakresie',
  showMore: (total: number) => `+ ${total} więcej`
}

interface CalendarEvent extends Event {
  id: number
  scheduledPost: ScheduledPost
  platform: string
  status: string
  contentText: string
}

interface ContentCalendarProps {
  scheduledPosts: ScheduledPost[]
  onCancelPost?: (postId: number) => void
}

const platformIcons = {
  linkedin: Linkedin,
  facebook: Facebook,
  twitter: Twitter,
  blog: Globe,
  website: FileText,
} as const

const platformColors = {
  linkedin: '#0077B5',
  facebook: '#1877F2',
  twitter: '#1DA1F2',
  blog: '#6366F1',
  website: '#8B5CF6',
} as const

export function ContentCalendar({ scheduledPosts, onCancelPost }: ContentCalendarProps) {
  const [view, setView] = useState<View>('month')
  const [date, setDate] = useState(new Date())
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null)
  const [showEventModal, setShowEventModal] = useState(false)

  // Konwertuj posty na wydarzenia kalendarza
  const events: CalendarEvent[] = useMemo(() => {
    return scheduledPosts.map(post => ({
      id: post.id,
      title: post.content_variant?.platform || post.platform,
      start: new Date(post.scheduled_for),
      end: new Date(post.scheduled_for),
      scheduledPost: post,
      platform: post.platform.toLowerCase(),
      status: post.status,
      contentText: post.content_variant?.content_text || ''
    }))
  }, [scheduledPosts])

  const handleSelectEvent = useCallback((event: CalendarEvent) => {
    setSelectedEvent(event)
    setShowEventModal(true)
  }, [])

  const handleNavigate = useCallback((newDate: Date) => {
    setDate(newDate)
  }, [])

  const handleViewChange = useCallback((newView: View) => {
    setView(newView)
  }, [])

  const handleCancelPost = () => {
    if (selectedEvent && onCancelPost) {
      onCancelPost(selectedEvent.id)
      setShowEventModal(false)
    }
  }

  // Niestandardowy komponent wydarzenia
  const EventComponent = ({ event }: { event: CalendarEvent }) => {
    const Icon = platformIcons[event.platform as keyof typeof platformIcons] || FileText
    const color = platformColors[event.platform as keyof typeof platformColors] || '#6B7280'
    
    return (
      <div className="flex items-center gap-1 h-full px-1">
        <Icon size={14} style={{ color }} />
        <span className="text-xs font-medium truncate">{event.title}</span>
      </div>
    )
  }

  // Stylowanie kalendarza
  const calendarStyle = {
    height: 700,
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      scheduled: { label: 'Zaplanowany', className: 'bg-blue-50 text-blue-600' },
      published: { label: 'Opublikowany', className: 'bg-green-50 text-green-600' },
      failed: { label: 'Błąd', className: 'bg-destructive/10 text-destructive' },
      cancelled: { label: 'Anulowany', className: 'bg-muted text-muted-foreground' }
    }
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.scheduled
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-destructive" />
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-muted-foreground" />
      default:
        return <Clock className="h-5 w-5 text-blue-600" />
    }
  }

  return (
    <>
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary/10 rounded-lg">
              <CalendarIcon className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-foreground">Harmonogram publikacji</h2>
              <p className="text-muted-foreground">Zaplanowane posty do publikacji</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={view === 'month' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setView('month')}
            >
              Miesiąc
            </Button>
            <Button
              variant={view === 'week' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setView('week')}
            >
              Tydzień
            </Button>
            <Button
              variant={view === 'day' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setView('day')}
            >
              Dzień
            </Button>
          </div>
        </div>

        <div className="bg-background rounded-lg border border-border">
          <Calendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            style={calendarStyle}
            onSelectEvent={handleSelectEvent}
            onNavigate={handleNavigate}
            onView={handleViewChange}
            view={view}
            date={date}
            messages={messages}
            components={{
              event: EventComponent
            }}
            formats={{
              monthHeaderFormat: 'MMMM YYYY',
              weekdayFormat: 'dddd',
              dayFormat: 'D',
              dayHeaderFormat: 'dddd, D MMMM',
              timeGutterFormat: 'HH:mm',
            }}
          />
        </div>
      </Card>

      {/* Modal ze szczegółami wydarzenia */}
      <AnimatePresence>
        {showEventModal && selectedEvent && (
          <Dialog open={showEventModal} onOpenChange={setShowEventModal}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle className="flex items-center justify-between">
                  <span>Szczegóły publikacji</span>
                  <button
                    onClick={() => setShowEventModal(false)}
                    className="p-1 hover:bg-accent rounded-md transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-6">
                {/* Nagłówek z platformą i statusem */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {(() => {
                      const Icon = platformIcons[selectedEvent.platform as keyof typeof platformIcons] || FileText
                      const color = platformColors[selectedEvent.platform as keyof typeof platformColors] || '#6B7280'
                      return (
                        <div className="p-3 rounded-lg" style={{ backgroundColor: `${color}20` }}>
                          <Icon className="h-6 w-6" style={{ color }} />
                        </div>
                      )
                    })()}
                    <div>
                      <h3 className="text-lg font-semibold text-foreground capitalize">
                        {selectedEvent.platform}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(selectedEvent.scheduledPost.scheduled_for), 'dd MMMM yyyy, HH:mm', { locale: pl })}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(selectedEvent.status)}
                    {getStatusBadge(selectedEvent.status)}
                  </div>
                </div>

                {/* Treść posta */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-foreground">Treść posta:</h4>
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-foreground whitespace-pre-wrap">
                      {selectedEvent.contentText || 'Brak treści'}
                    </p>
                  </div>
                </div>

                {/* Informacje dodatkowe */}
                {selectedEvent.scheduledPost.published_at && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Opublikowano: {format(new Date(selectedEvent.scheduledPost.published_at), 'dd.MM.yyyy HH:mm', { locale: pl })}</span>
                  </div>
                )}

                {selectedEvent.scheduledPost.error_message && (
                  <div className="p-3 bg-destructive/10 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 text-destructive mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-destructive">Błąd publikacji</p>
                        <p className="text-sm text-destructive/80">{selectedEvent.scheduledPost.error_message}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <DialogFooter>
                {selectedEvent.status === 'scheduled' && onCancelPost && (
                  <Button
                    variant="destructive"
                    onClick={handleCancelPost}
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Anuluj publikację
                  </Button>
                )}
                <Button
                  variant="outline"
                  onClick={() => setShowEventModal(false)}
                >
                  Zamknij
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </AnimatePresence>
    </>
  )
}