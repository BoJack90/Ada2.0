'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText,
  Users,
  Calendar,
  Clock,
  Link2,
  Facebook,
  Linkedin,
  Instagram,
  Globe,
  ChevronDown,
  ChevronUp,
  Eye,
  Heart,
  MessageCircle,
  Share2,
  Bookmark,
  Filter
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'

interface ContentVisualizationProps {
  planId: number
  organizationId: number
}

interface ContentDraft {
  id: number
  suggested_topic: {
    id: number
    title: string
    description: string
    category: string
    is_correlated: boolean
    parent_topic_title?: string
  }
  status: string
  variants: Array<{
    id: number
    platform_name: string
    status: string
    content_preview: string
    created_at: string
  }>
  created_at: string
}

export function ContentVisualization({ planId, organizationId }: ContentVisualizationProps) {
  const [expandedPosts, setExpandedPosts] = useState<Set<number>>(new Set())
  const [viewMode, setViewMode] = useState<'all' | 'blog' | 'social'>('all')
  
  // Fetch content drafts
  const { data: drafts, isLoading, error } = useQuery<ContentDraft[]>({
    queryKey: ['content-plan-drafts', planId],
    queryFn: async () => {
      const data = await api.contentPlans.getDrafts(planId)
      console.log('Drafts fetched:', data)
      return data
    }
  })

  // Fetch plan details
  const { data: plan } = useQuery({
    queryKey: ['content-plan', planId],
    queryFn: async () => {
      const data = await api.contentPlans.get(planId)
      return data
    }
  })

  const toggleExpanded = (draftId: number) => {
    const newExpanded = new Set(expandedPosts)
    if (newExpanded.has(draftId)) {
      newExpanded.delete(draftId)
    } else {
      newExpanded.add(draftId)
    }
    setExpandedPosts(newExpanded)
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform?.toLowerCase()) {
      case 'facebook':
        return <Facebook className="h-5 w-5 text-blue-600" />
      case 'linkedin':
        return <Linkedin className="h-5 w-5 text-blue-700" />
      case 'instagram':
        return <Instagram className="h-5 w-5 text-pink-600" />
      case 'blog':
      case 'wordpress':
        return <Globe className="h-5 w-5 text-gray-600" />
      default:
        return <FileText className="h-5 w-5 text-gray-600" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <Card className="p-6 max-w-md">
          <p className="text-center text-red-500">Błąd podczas ładowania treści</p>
        </Card>
      </div>
    )
  }

  const blogDrafts = drafts?.filter(d => d.suggested_topic.category === 'blog') || []
  const socialDrafts = drafts?.filter(d => d.suggested_topic.category === 'social_media') || []

  const filteredBlogDrafts = viewMode === 'social' ? [] : blogDrafts
  const filteredSocialDrafts = viewMode === 'blog' ? [] : socialDrafts

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Plan treści: {plan?.plan_period}
        </h2>
        <p className="text-muted-foreground">
          {blogDrafts.length} wpisów blogowych, {socialDrafts.length} postów social media
        </p>
      </div>

      {/* View mode filter */}
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <div className="flex gap-2">
          {(['all', 'blog', 'social'] as const).map(mode => (
            <Button
              key={mode}
              variant={viewMode === mode ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode(mode)}
            >
              {mode === 'all' && 'Wszystkie'}
              {mode === 'blog' && 'Blog'}
              {mode === 'social' && 'Social Media'}
            </Button>
          ))}
        </div>
      </div>

      {/* Blog posts section */}
      {filteredBlogDrafts.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Wpisy blogowe
          </h3>
          <div className="grid gap-6">
            {filteredBlogDrafts.map(draft => (
              <BlogPostPreview 
                key={draft.id} 
                draft={draft}
                isExpanded={expandedPosts.has(draft.id)}
                onToggleExpand={() => toggleExpanded(draft.id)}
                relatedSocialDrafts={socialDrafts.filter(sd => 
                  sd.suggested_topic.parent_topic_title === draft.suggested_topic.title
                )}
              />
            ))}
          </div>
        </div>
      )}

      {/* Social media posts section */}
      {filteredSocialDrafts.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Users className="h-5 w-5" />
            Posty Social Media
          </h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredSocialDrafts.map(draft => (
              <SocialMediaPostPreview key={draft.id} draft={draft} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Blog post preview component
function BlogPostPreview({ 
  draft, 
  isExpanded, 
  onToggleExpand,
  relatedSocialDrafts 
}: { 
  draft: ContentDraft
  isExpanded: boolean
  onToggleExpand: () => void
  relatedSocialDrafts: ContentDraft[]
}) {
  const variant = draft.variants?.[0]
  
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-foreground mb-2">
              {draft.suggested_topic.title}
            </h3>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {format(new Date(draft.created_at), 'dd MMM yyyy', { locale: pl })}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                5 min czytania
              </span>
            </div>
          </div>
          <Badge variant="secondary">
            <FileText className="h-3 w-3 mr-1" />
            Blog
          </Badge>
        </div>

        {/* Content preview */}
        <div className="prose prose-sm max-w-none">
          <p className="text-muted-foreground line-clamp-3">
            {variant?.content_text || draft.suggested_topic.description || 'Brak treści...'}
          </p>
        </div>

        {/* Expand button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleExpand}
          className="w-full"
        >
          {isExpanded ? (
            <>Zwiń <ChevronUp className="h-4 w-4 ml-1" /></>
          ) : (
            <>Czytaj więcej <ChevronDown className="h-4 w-4 ml-1" /></>
          )}
        </Button>

        {/* Expanded content */}
        <AnimatePresence>
          {isExpanded && variant && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-4 border-t pt-4"
            >
              <div className="prose prose-sm max-w-none">
                <div 
                  className="whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: variant.content_text }}
                />
              </div>
              
              {/* Blog interactions */}
              <div className="flex items-center justify-between mt-6 pt-4 border-t">
                <div className="flex items-center gap-4">
                  <button className="flex items-center gap-1 text-muted-foreground hover:text-primary">
                    <Heart className="h-4 w-4" />
                    <span className="text-sm">142</span>
                  </button>
                  <button className="flex items-center gap-1 text-muted-foreground hover:text-primary">
                    <MessageCircle className="h-4 w-4" />
                    <span className="text-sm">23</span>
                  </button>
                  <button className="flex items-center gap-1 text-muted-foreground hover:text-primary">
                    <Share2 className="h-4 w-4" />
                    <span className="text-sm">Udostępnij</span>
                  </button>
                </div>
                <button className="text-muted-foreground hover:text-primary">
                  <Bookmark className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Related social media posts */}
      {relatedSocialDrafts.length > 0 && (
        <div className="bg-muted/50 px-6 py-4 border-t">
          <div className="text-sm font-medium text-muted-foreground mb-3">
            Powiązane posty social media:
          </div>
          <div className="space-y-2">
            {relatedSocialDrafts.map(socialDraft => (
              <div key={socialDraft.id} className="flex items-center gap-2">
                {socialDraft.variants.map(v => (
                  <div key={v.id} className="flex items-center gap-2">
                    {getPlatformIcon(v.platform_name)}
                    <span className="text-sm">{v.platform_name}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}

// Social media post preview component
function SocialMediaPostPreview({ draft }: { draft: ContentDraft }) {
  const variants = draft.variants || []
  
  return (
    <>
      {variants.map(variant => {
        // Platform-specific styling
        const platformStyles = {
          facebook: 'bg-blue-50 border-blue-200',
          linkedin: 'bg-blue-100 border-blue-300',
          instagram: 'bg-gradient-to-br from-purple-50 to-pink-50 border-pink-200'
        }
        
        const platformStyle = platformStyles[variant.platform_name.toLowerCase() as keyof typeof platformStyles] || 'bg-gray-50'
        
        return (
          <Card key={variant.id} className={`overflow-hidden ${platformStyle} border`}>
            <div className="p-4">
              {/* Platform header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {getPlatformIcon(variant.platform_name)}
                  <span className="font-medium capitalize">{variant.platform_name}</span>
                </div>
                {draft.suggested_topic.is_correlated && (
                  <Badge variant="outline" className="text-xs">
                    <Link2 className="h-3 w-3 mr-1" />
                    Powiązany
                  </Badge>
                )}
              </div>

              {/* Post content */}
              <div className="space-y-3">
                <h4 className="font-medium text-sm">{draft.suggested_topic.title}</h4>
                <p className="text-sm whitespace-pre-wrap">
                  {variant.content_preview}
                </p>

                {/* Mock image placeholder for Instagram */}
                {variant.platform_name.toLowerCase() === 'instagram' && (
                  <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                    <Eye className="h-8 w-8 text-muted-foreground" />
                  </div>
                )}

                {/* Platform interactions */}
                <div className="flex items-center justify-between pt-3 border-t">
                  <div className="flex items-center gap-3">
                    <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm">
                      <Heart className="h-4 w-4" />
                      <span>Lubię</span>
                    </button>
                    <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm">
                      <MessageCircle className="h-4 w-4" />
                      <span>Komentuj</span>
                    </button>
                    <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm">
                      <Share2 className="h-4 w-4" />
                      <span>Udostępnij</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )
      })}
    </>
  )
}

// Helper function
function getPlatformIcon(platform: string) {
  switch (platform?.toLowerCase()) {
    case 'facebook':
      return <Facebook className="h-5 w-5 text-blue-600" />
    case 'linkedin':
      return <Linkedin className="h-5 w-5 text-blue-700" />
    case 'instagram':
      return <Instagram className="h-5 w-5 text-pink-600" />
    default:
      return <FileText className="h-5 w-5 text-gray-600" />
  }
}