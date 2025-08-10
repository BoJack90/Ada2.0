import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

export interface BadgeProps {
  variant?: 'default' | 'new' | 'generating_topics' | 'pending_blog_topic_approval' | 
           'complete' | 'generating_sm_topics' | 'error' | 'warning' | 'info' | 
           'success' | 'secondary' | 'outline'
  size?: 'sm' | 'default' | 'lg'
  icon?: LucideIcon
  pulse?: boolean
  children: ReactNode
  className?: string
}

export function Badge({ 
  variant = 'default', 
  size = 'default',
  icon: Icon,
  pulse = false,
  className = '', 
  children, 
  ...props 
}: BadgeProps) {
  const getVariantClasses = (variant: string) => {
    switch (variant) {
      case 'new':
      case 'info':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'generating_topics':
      case 'warning':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200'
      case 'pending_blog_topic_approval':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200'
      case 'complete':
      case 'success':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'generating_sm_topics':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      case 'error':
        return 'bg-red-50 text-red-700 border-red-200'
      case 'secondary':
        return 'bg-muted text-muted-foreground border-muted'
      case 'outline':
        return 'bg-transparent text-foreground border-border'
      default:
        return 'bg-primary/10 text-primary border-primary/20'
    }
  }
  
  const getSizeClasses = (size: string) => {
    switch (size) {
      case 'sm':
        return 'px-2 py-0.5 text-xs'
      case 'lg':
        return 'px-3 py-1.5 text-sm'
      default:
        return 'px-2.5 py-1 text-xs'
    }
  }

  return (
    <motion.span
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium border',
        'transition-all duration-200',
        getVariantClasses(variant),
        getSizeClasses(size),
        pulse && 'animate-pulse',
        className
      )}
      {...props}
    >
      {Icon && <Icon className={cn('h-3 w-3', size === 'lg' && 'h-4 w-4')} />}
      {children}
      {pulse && (
        <motion.span
          className="inline-block h-2 w-2 rounded-full bg-current opacity-75"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
    </motion.span>
  )
}