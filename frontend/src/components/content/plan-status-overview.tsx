'use client'

import { motion } from 'framer-motion'
import { 
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  RefreshCw,
  Loader2,
  FileText,
  Sparkles,
  AlertTriangle
} from 'lucide-react'
import { Card } from '@/components/ui/cards'

interface PlanStatusOverviewProps {
  status: string
}

export function PlanStatusOverview({ status }: PlanStatusOverviewProps) {
  const getStatusDetails = () => {
    switch (status) {
      case 'new':
        return {
          icon: <Clock className="h-12 w-12" />,
          title: 'Nowy plan',
          description: 'Ten plan został utworzony i oczekuje na rozpoczęcie procesu generowania treści',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50'
        }
      
      case 'generating_topics':
        return {
          icon: <Loader2 className="h-12 w-12 animate-spin" />,
          title: 'Generowanie tematów',
          description: 'Trwa generowanie propozycji tematów blogowych przy użyciu AI',
          color: 'text-primary',
          bgColor: 'bg-primary/10'
        }
      
      case 'topics_generated':
        return {
          icon: <FileText className="h-12 w-12" />,
          title: 'Tematy wygenerowane',
          description: 'Tematy blogowe zostały wygenerowane i oczekują na zatwierdzenie',
          color: 'text-green-600',
          bgColor: 'bg-green-50'
        }
      
      case 'in_progress':
        return {
          icon: <RefreshCw className="h-12 w-12 animate-spin" />,
          title: 'W trakcie realizacji',
          description: 'Plan jest w trakcie realizacji - trwa generowanie lub przetwarzanie treści',
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50'
        }
      
      case 'error':
        return {
          icon: <AlertTriangle className="h-12 w-12" />,
          title: 'Błąd',
          description: 'Wystąpił błąd podczas przetwarzania planu. Skontaktuj się z administratorem',
          color: 'text-destructive',
          bgColor: 'bg-destructive/10'
        }
      
      case 'cancelled':
        return {
          icon: <XCircle className="h-12 w-12" />,
          title: 'Anulowany',
          description: 'Ten plan został anulowany i nie będzie dalej przetwarzany',
          color: 'text-muted-foreground',
          bgColor: 'bg-muted'
        }
      
      case 'scheduled':
        return {
          icon: <CheckCircle className="h-12 w-12" />,
          title: 'Zaplanowany',
          description: 'Treści zostały zaplanowane do publikacji',
          color: 'text-green-600',
          bgColor: 'bg-green-50'
        }
      
      default:
        return {
          icon: <AlertCircle className="h-12 w-12" />,
          title: `Status: ${status}`,
          description: 'Ten plan znajduje się w stanie pośrednim. Proszę czekać na dalsze aktualizacje',
          color: 'text-muted-foreground',
          bgColor: 'bg-muted'
        }
    }
  }

  const statusDetails = getStatusDetails()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="p-8">
        <div className="flex flex-col items-center text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className={`p-4 rounded-full ${statusDetails.bgColor} ${statusDetails.color} mb-6`}
          >
            {statusDetails.icon}
          </motion.div>
          
          <motion.h3
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-2xl font-bold text-foreground mb-3"
          >
            {statusDetails.title}
          </motion.h3>
          
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-muted-foreground max-w-md"
          >
            {statusDetails.description}
          </motion.p>

          {status === 'in_progress' && (
            <motion.div
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "100%" }}
              transition={{ delay: 0.5, duration: 0.5 }}
              className="mt-6 w-full max-w-xs"
            >
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Przetwarzanie w toku...
              </p>
            </motion.div>
          )}

          {status === 'new' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-6"
            >
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Sparkles className="h-4 w-4" />
                <span>Wróć do listy planów, aby rozpocząć generowanie</span>
              </div>
            </motion.div>
          )}
        </div>
      </Card>
    </motion.div>
  )
}