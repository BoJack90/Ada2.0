'use client'

import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  color?: 'primary' | 'warning' | 'success' | 'danger' | 'info' | 'indigo'
  subtitle?: string
  trend?: {
    value: number
    isPositive: boolean
  }
  className?: string
}

export function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  color = 'primary', 
  subtitle,
  trend,
  className 
}: StatCardProps) {
  const colorClasses = {
    primary: 'text-primary bg-primary/10',
    warning: 'text-yellow-600 bg-yellow-50',
    success: 'text-green-600 bg-green-50',
    danger: 'text-destructive bg-destructive/10',
    info: 'text-blue-600 bg-blue-50',
    indigo: 'text-indigo-600 bg-indigo-50'
  }

  const iconBgClasses = {
    primary: 'bg-primary/10',
    warning: 'bg-yellow-50',
    success: 'bg-green-50',
    danger: 'bg-destructive/10',
    info: 'bg-blue-50',
    indigo: 'bg-indigo-50'
  }

  return (
    <div className={cn("card-base hover-lift p-6", className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground mb-1">
            {title}
          </p>
          <div className="text-2xl font-bold text-foreground">{value}</div>
          {subtitle && (
            <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={cn(
              "flex items-center gap-1 text-xs font-medium mt-2",
              trend.isPositive ? 'text-green-600' : 'text-destructive'
            )}>
              <span>{trend.isPositive ? '↗' : '↘'}</span>
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
        <div className={cn(
          "p-3 rounded-lg",
          iconBgClasses[color]
        )}>
          <Icon className={colorClasses[color].split(' ')[0]} size={20} />
        </div>
      </div>
    </div>
  )
}

interface CardProps {
  title?: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
  className?: string
  headerClassName?: string
  bodyClassName?: string
  noPadding?: boolean
  onClick?: (e: React.MouseEvent) => void
}

export function Card({ 
  title, 
  subtitle, 
  actions, 
  children, 
  className = '',
  headerClassName = '',
  bodyClassName = '',
  noPadding = false,
  onClick
}: CardProps) {
  return (
    <div className={cn("card-base", className)} onClick={onClick}>
      {(title || subtitle || actions) && (
        <div className={cn(
          "px-6 py-4 border-b border-border",
          headerClassName
        )}>
          <div className="flex items-center justify-between">
            <div>
              {title && <h3 className="text-lg font-semibold text-foreground">{title}</h3>}
              {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
            </div>
            {actions && <div className="flex items-center gap-2">{actions}</div>}
          </div>
        </div>
      )}
      <div className={cn(
        !noPadding && "p-6",
        bodyClassName
      )}>
        {children}
      </div>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    period: string
    isPositive: boolean
  }
  chart?: ReactNode
  color?: string
  className?: string
}

export function MetricCard({ title, value, change, chart, color = 'primary', className }: MetricCardProps) {
  return (
    <div className={cn("card-base p-6", className)}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h6 className="text-sm font-medium text-muted-foreground mb-1">{title}</h6>
          <div className="text-2xl font-bold text-foreground">{value}</div>
          {change && (
            <div className={cn(
              "flex items-center gap-1 text-xs font-medium mt-2",
              change.isPositive ? 'text-green-600' : 'text-destructive'
            )}>
              <span>{change.isPositive ? '+' : ''}{change.value}%</span>
              <span className="text-muted-foreground">vs {change.period}</span>
            </div>
          )}
        </div>
        {chart && (
          <div className="flex-shrink-0 ml-4">
            {chart}
          </div>
        )}
      </div>
    </div>
  )
}
