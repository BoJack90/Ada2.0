'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  FileEdit, 
  Calendar,
  Filter,
  Search,
  ChevronRight,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  FileText,
  MessageSquare,
  Link2,
  Facebook,
  Linkedin,
  Instagram,
  Globe,
  Hash,
  Users
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'

interface EnhancedContentWorkspaceProps {
  organizationId: number
  planId?: number
}

export function EnhancedContentWorkspace({ organizationId, planId }: EnhancedContentWorkspaceProps) {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<'all' | 'blog' | 'social_media'>('all')
  const [platformFilter, setPlatformFilter] = useState<string>('all')
  const [correlationFilter, setCorrelationFilter] = useState<'all' | 'correlated' | 'standalone'>('all')
  const [groupBy, setGroupBy] = useState<'plan' | 'category' | 'none'>('plan')

  // Fetch drafts with enhanced API
  const { data: response, isLoading } = useQuery({
    queryKey: ['enhanced-drafts', organizationId, planId, categoryFilter, platformFilter, correlationFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        organization_id: organizationId.toString()
      })
      
      if (planId) params.append('plan_id', planId.toString())
      if (categoryFilter !== 'all') params.append('category', categoryFilter)
      if (platformFilter !== 'all') params.append('platform', platformFilter)
      if (correlationFilter !== 'all') {
        params.append('is_correlated', correlationFilter === 'correlated' ? 'true' : 'false')
      }
      
      const response = await fetch(`/api/content-workspace/all-drafts?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      return response.json()
    }
  })

  const drafts = response?.drafts || []

  // Filter by search
  const filteredDrafts = drafts.filter(draft => {
    const searchLower = searchQuery.toLowerCase()
    return draft.topic.title.toLowerCase().includes(searchLower) ||
           draft.content_plan.plan_period.toLowerCase().includes(searchLower)
  })

  // Group drafts
  const groupedDrafts = groupBy === 'none' ? { 'Wszystkie': filteredDrafts } :
    filteredDrafts.reduce((groups, draft) => {
      const key = groupBy === 'plan' 
        ? `${draft.content_plan.plan_period} (ID: ${draft.content_plan.id})`
        : draft.topic.category === 'blog' ? 'Wpisy blogowe' : 'Social Media'
      
      if (!groups[key]) groups[key] = []
      groups[key].push(draft)
      return groups
    }, {} as Record<string, typeof drafts>)

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'facebook': return <Facebook className="h-4 w-4" />
      case 'linkedin': return <Linkedin className="h-4 w-4" />
      case 'instagram': return <Instagram className="h-4 w-4" />
      case 'blog':
      case 'wordpress': return <Globe className="h-4 w-4" />
      default: return <MessageSquare className="h-4 w-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'drafting': { label: 'Tworzenie', color: 'bg-gray-100 text-gray-700' },
      'pending_approval': { label: 'Do zatwierdzenia', color: 'bg-yellow-100 text-yellow-700' },
      'approved': { label: 'Zatwierdzony', color: 'bg-green-100 text-green-700' },
      'rejected': { label: 'Odrzucony', color: 'bg-red-100 text-red-700' }
    }
    
    const config = statusConfig[status] || statusConfig['drafting']
    return <Badge className={config.color}>{config.label}</Badge>
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header z statystykami */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">{response?.total || 0}</div>
            <div className="text-sm text-muted-foreground">Wszystkie treści</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {drafts.filter(d => d.topic.category === 'blog').length}
            </div>
            <div className="text-sm text-muted-foreground">Wpisy blogowe</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {drafts.filter(d => d.topic.category === 'social_media').length}
            </div>
            <div className="text-sm text-muted-foreground">Posty Social Media</div>
            <div className="text-xs text-muted-foreground mt-1">
              Blog: {drafts.filter(d => d.topic.category === 'social_media' && d.topic.is_correlated).length} | 
              Brief: {drafts.filter(d => d.topic.category === 'social_media' && d.topic.source_info?.type === 'brief').length}
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {drafts.filter(d => d.topic.is_correlated).length}
            </div>
            <div className="text-sm text-muted-foreground">Powiązane z blogiem</div>
          </div>
        </div>
      </Card>

      {/* Filtry i opcje */}
      <Card className="p-6">
        <div className="space-y-4">
          {/* Wyszukiwarka */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Szukaj po tytule lub planie..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-background border border-input rounded-md"
            />
          </div>

          {/* Filtry */}
          <div className="flex flex-wrap gap-4">
            {/* Kategoria */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Kategoria:</span>
              <div className="flex gap-1">
                {(['all', 'blog', 'social_media'] as const).map(cat => (
                  <button
                    key={cat}
                    onClick={() => setCategoryFilter(cat)}
                    className={`px-3 py-1 rounded-md text-sm ${
                      categoryFilter === cat 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-muted hover:bg-accent'
                    }`}
                  >
                    {cat === 'all' ? 'Wszystkie' : cat === 'blog' ? 'Blog' : 'Social Media'}
                  </button>
                ))}
              </div>
            </div>

            {/* Platforma */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Platforma:</span>
              <select
                value={platformFilter}
                onChange={(e) => setPlatformFilter(e.target.value)}
                className="px-3 py-1 rounded-md text-sm bg-muted"
              >
                <option value="all">Wszystkie</option>
                <option value="blog">Blog</option>
                <option value="facebook">Facebook</option>
                <option value="linkedin">LinkedIn</option>
                <option value="instagram">Instagram</option>
              </select>
            </div>

            {/* Powiązanie */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Typ:</span>
              <div className="flex gap-1">
                {(['all', 'correlated', 'standalone'] as const).map(type => (
                  <button
                    key={type}
                    onClick={() => setCorrelationFilter(type)}
                    className={`px-3 py-1 rounded-md text-sm ${
                      correlationFilter === type 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-muted hover:bg-accent'
                    }`}
                  >
                    {type === 'all' ? 'Wszystkie' : type === 'correlated' ? 'Powiązane' : 'Samodzielne'}
                  </button>
                ))}
              </div>
            </div>

            {/* Grupowanie */}
            <div className="flex items-center gap-2 ml-auto">
              <span className="text-sm font-medium">Grupuj według:</span>
              <select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value as typeof groupBy)}
                className="px-3 py-1 rounded-md text-sm bg-muted"
              >
                <option value="plan">Planu</option>
                <option value="category">Kategorii</option>
                <option value="none">Nie grupuj</option>
              </select>
            </div>
          </div>
        </div>
      </Card>

      {/* Lista treści pogrupowana */}
      <div className="space-y-6">
        {Object.entries(groupedDrafts).map(([groupName, groupDrafts]) => (
          <div key={groupName} className="space-y-4">
            {groupBy !== 'none' && (
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                {groupBy === 'plan' ? <Calendar className="h-5 w-5" /> : <Hash className="h-5 w-5" />}
                {groupName}
                <Badge variant="secondary">{groupDrafts.length}</Badge>
              </h3>
            )}
            
            <div className="grid gap-4">
              {groupDrafts.map((draft, index) => (
                <motion.div
                  key={draft.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card 
                    className="p-6 hover-lift cursor-pointer"
                    onClick={() => router.push(`/dashboard/drafts/${draft.id}`)}
                  >
                    <div className="flex items-start gap-4">
                      {/* Icon */}
                      <div className={`p-3 rounded-lg ${
                        draft.topic.category === 'blog' 
                          ? 'bg-blue-100 text-blue-600' 
                          : 'bg-purple-100 text-purple-600'
                      }`}>
                        {draft.topic.category === 'blog' ? <FileText className="h-5 w-5" /> : <Users className="h-5 w-5" />}
                      </div>
                      
                      {/* Content */}
                      <div className="flex-1 space-y-3">
                        {/* Title and status */}
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="text-lg font-semibold text-foreground">
                              {draft.topic.title}
                            </h4>
                            {draft.topic.is_correlated && draft.topic.parent_topic && (
                              <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                                <Link2 className="h-4 w-4" />
                                <span>Powiązany z: {draft.topic.parent_topic.title}</span>
                              </div>
                            )}
                            {draft.topic.source_info && (
                              <div className="flex items-center gap-2 mt-1">
                                {draft.topic.source_info.type === 'brief' && (
                                  <Badge variant="outline" className="text-xs">
                                    <FileText className="h-3 w-3 mr-1" />
                                    Z briefu
                                  </Badge>
                                )}
                                {draft.topic.source_info.type === 'standalone' && (
                                  <Badge variant="outline" className="text-xs">
                                    <Hash className="h-3 w-3 mr-1" />
                                    Samodzielny
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                          {getStatusBadge(draft.status)}
                        </div>
                        
                        {/* Platforms */}
                        <div className="flex flex-wrap gap-2">
                          {draft.topic.category === 'social_media' && draft.topic.suggested_platforms?.length > 0 ? (
                            // For SM posts, show suggested platforms
                            draft.topic.suggested_platforms.map(platform => (
                              <div
                                key={platform}
                                className="flex items-center gap-1 px-2 py-1 bg-muted rounded-md"
                              >
                                {getPlatformIcon(platform)}
                                <span className="text-sm font-medium">{platform}</span>
                              </div>
                            ))
                          ) : (
                            // For blog posts or posts with variants
                            Object.entries(draft.platforms).map(([platform, variants]) => (
                              <div
                                key={platform}
                                className="flex items-center gap-1 px-2 py-1 bg-muted rounded-md"
                              >
                                {getPlatformIcon(platform)}
                                <span className="text-sm font-medium">{platform}</span>
                                <Badge variant="outline" className="ml-1 text-xs">
                                  {variants.length}
                                </Badge>
                              </div>
                            ))
                          )}
                        </div>
                        
                        {/* Meta info */}
                        <div className="flex items-center gap-4 text-sm">
                          <Badge variant="secondary" className="font-medium">
                            <Calendar className="h-3 w-3 mr-1" />
                            Plan: {draft.content_plan.plan_period}
                          </Badge>
                          <span className="text-muted-foreground">
                            {format(new Date(draft.created_at), 'dd MMM yyyy', { locale: pl })}
                          </span>
                        </div>
                      </div>
                      
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {filteredDrafts.length === 0 && (
        <Card className="p-8 text-center">
          <FileEdit className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">
            Brak treści spełniających kryteria
          </h3>
          <p className="text-muted-foreground">
            Spróbuj zmienić filtry lub poczekaj na wygenerowanie nowych treści
          </p>
        </Card>
      )}
    </div>
  )
}