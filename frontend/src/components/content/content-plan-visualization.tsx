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
  Hash,
  ChevronDown,
  ChevronUp,
  Eye,
  Heart,
  MessageCircle,
  Share2,
  Bookmark,
  ArrowLeft
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { useRouter } from 'next/navigation'

interface ContentPlanVisualizationProps {
  planId: number
  organizationId: number
}

interface ContentItem {
  id: number
  type: 'blog' | 'social_media'
  title: string
  content: string
  platform?: string
  parent_id?: number
  source_type?: string
  scheduled_date?: string
  variants?: Array<{
    id: number
    platform_name: string
    content_text: string
  }>
}

export function ContentPlanVisualization({ planId, organizationId }: ContentPlanVisualizationProps) {
  const router = useRouter()
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set())
  const [viewMode, setViewMode] = useState<'all' | 'blog' | 'social'>('all')

  // Fetch plan details with all content
  const { data: planData, isLoading } = useQuery({
    queryKey: ['content-plan-visualization', planId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/content-plans/${planId}/drafts`)
      return response.data
    }
  })

  const toggleExpanded = (id: number) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedItems(newExpanded)
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform?.toLowerCase()) {
      case 'facebook': return <Facebook className="h-5 w-5" />
      case 'linkedin': return <Linkedin className="h-5 w-5" />
      case 'instagram': return <Instagram className="h-5 w-5" />
      case 'blog':
      case 'wordpress': return <Globe className="h-5 w-5" />
      default: return <Hash className="h-5 w-5" />
    }
  }

  const BlogPostPreview = ({ item }: { item: ContentItem }) => {
    const isExpanded = expandedItems.has(item.id)
    const variant = item.variants?.[0]
    
    return (
      <Card className="overflow-hidden hover-lift">
        <div className="p-6">
          {/* Blog header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-xl font-bold text-foreground mb-2">{item.title}</h3>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  {item.scheduled_date ? format(new Date(item.scheduled_date), 'dd MMM yyyy', { locale: pl }) : 'Nie zaplanowano'}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  5 min czytania
                </span>
              </div>
            </div>
            <Badge variant="secondary" className="flex items-center gap-1">
              <FileText className="h-3 w-3" />
              Blog
            </Badge>
          </div>

          {/* Blog content preview */}
          <div className="prose prose-sm max-w-none">
            <p className="text-muted-foreground line-clamp-3">
              {variant?.content_text || item.content || 'Brak treści...'}
            </p>
          </div>

          {/* Expand button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleExpanded(item.id)}
            className="mt-4 w-full"
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
                  <div dangerouslySetInnerHTML={{ __html: variant.content_text.replace(/\n/g, '<br/>') }} />
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
        {planData?.socialPosts?.filter((sm: ContentItem) => sm.parent_id === item.id).length > 0 && (
          <div className="bg-muted/50 px-6 py-4 border-t">
            <div className="text-sm font-medium text-muted-foreground mb-3">
              Powiązane posty social media:
            </div>
            <div className="space-y-2">
              {planData.socialPosts
                .filter((sm: ContentItem) => sm.parent_id === item.id)
                .map((sm: ContentItem) => (
                  <div key={sm.id} className="flex items-center gap-2">
                    {getPlatformIcon(sm.platform)}
                    <span className="text-sm truncate">{sm.title}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </Card>
    )
  }

  const SocialMediaPostPreview = ({ item }: { item: ContentItem }) => {
    const variant = item.variants?.find(v => v.platform_name === item.platform) || item.variants?.[0]
    
    // Platform-specific styling
    const platformStyles = {
      facebook: 'bg-blue-50 border-blue-200',
      linkedin: 'bg-blue-100 border-blue-300',
      instagram: 'bg-gradient-to-br from-purple-50 to-pink-50 border-pink-200'
    }
    
    const platformStyle = platformStyles[item.platform?.toLowerCase() as keyof typeof platformStyles] || 'bg-gray-50'
    
    return (
      <Card className={`overflow-hidden ${platformStyle} border`}>
        <div className="p-4">
          {/* Platform header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {getPlatformIcon(item.platform || '')}
              <span className="font-medium capitalize">{item.platform}</span>
            </div>
            {item.parent_id && (
              <Badge variant="outline" className="text-xs">
                <Link2 className="h-3 w-3 mr-1" />
                Powiązany
              </Badge>
            )}
          </div>

          {/* Post content */}
          <div className="space-y-3">
            <p className="text-sm whitespace-pre-wrap">
              {variant?.content_text || item.title}
            </p>

            {/* Mock image placeholder for Instagram */}
            {item.platform?.toLowerCase() === 'instagram' && (
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
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  const blogPosts = planData?.blogPosts || []
  const socialPosts = planData?.socialPosts || []
  
  // Filter content based on view mode
  const filteredBlogPosts = viewMode === 'social' ? [] : blogPosts
  const filteredSocialPosts = viewMode === 'blog' ? [] : socialPosts

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/dashboard/content')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="text-2xl font-bold text-foreground">
              Plan treści: {planData?.plan?.plan_period}
            </h2>
            <p className="text-muted-foreground">
              {blogPosts.length} wpisów blogowych, {socialPosts.length} postów social media
            </p>
          </div>
        </div>
        
        {/* View mode switcher */}
        <div className="flex gap-2">
          {(['all', 'blog', 'social'] as const).map(mode => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === mode
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted hover:bg-accent'
              }`}
            >
              {mode === 'all' && 'Wszystkie'}
              {mode === 'blog' && (
                <>
                  <FileText className="h-4 w-4 inline mr-1" />
                  Blog
                </>
              )}
              {mode === 'social' && (
                <>
                  <Users className="h-4 w-4 inline mr-1" />
                  Social Media
                </>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content grid */}
      <div className="space-y-8">
        {/* Blog posts section */}
        {filteredBlogPosts.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              Wpisy blogowe
            </h3>
            <div className="grid gap-6 lg:grid-cols-2">
              {filteredBlogPosts.map((post, index) => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <BlogPostPreview item={post} />
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Social media posts section */}
        {filteredSocialPosts.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Users className="h-5 w-5 text-purple-600" />
              Posty social media
            </h3>
            
            {/* Group by platform */}
            {['facebook', 'linkedin', 'instagram'].map(platform => {
              const platformPosts = filteredSocialPosts.filter(
                post => post.platform?.toLowerCase() === platform
              )
              
              if (platformPosts.length === 0) return null
              
              return (
                <div key={platform} className="space-y-3">
                  <h4 className="text-md font-medium flex items-center gap-2 capitalize">
                    {getPlatformIcon(platform)}
                    {platform} ({platformPosts.length})
                  </h4>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {platformPosts.map((post, index) => (
                      <motion.div
                        key={post.id}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <SocialMediaPostPreview item={post} />
                      </motion.div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}