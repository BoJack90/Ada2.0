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
  Filter,
  Hash,
  ExternalLink
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'

interface ContentVisualizationV2Props {
  planId: number
  organizationId: number
}

export function ContentVisualizationV2({ planId, organizationId }: ContentVisualizationV2Props) {
  const [expandedPosts, setExpandedPosts] = useState<Set<number>>(new Set())
  const [viewMode, setViewMode] = useState<'all' | 'blog' | 'social'>('all')
  
  // Fetch full content data
  const { data, isLoading, error } = useQuery({
    queryKey: ['content-plan-full', planId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/content-plans/${planId}/full-content`)
      console.log('Full content data:', response.data)
      return response.data
    }
  })

  const toggleExpanded = (postId: number) => {
    const newExpanded = new Set(expandedPosts)
    if (newExpanded.has(postId)) {
      newExpanded.delete(postId)
    } else {
      newExpanded.add(postId)
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
      default:
        return <MessageCircle className="h-5 w-5 text-gray-600" />
    }
  }

  const getPlatformStyle = (platform: string) => {
    switch (platform?.toLowerCase()) {
      case 'facebook':
        return 'bg-blue-50 border-blue-200 hover:bg-blue-100'
      case 'linkedin':
        return 'bg-blue-100 border-blue-300 hover:bg-blue-200'
      case 'instagram':
        return 'bg-gradient-to-br from-purple-50 to-pink-50 border-pink-200 hover:from-purple-100 hover:to-pink-100'
      default:
        return 'bg-gray-50 border-gray-200 hover:bg-gray-100'
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

  const { plan, organized_content, standalone_social_posts, statistics } = data || {}
  
  
  // Filter content based on view mode
  const filteredContent = viewMode === 'social' 
    ? [] 
    : organized_content || []
    
  const filteredStandalone = viewMode === 'blog' 
    ? [] 
    : standalone_social_posts || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Plan treści: {plan?.plan_period}
        </h2>
        <p className="text-muted-foreground">
          {statistics?.total_blog_posts || 0} wpisów blogowych, {statistics?.total_social_posts || 0} postów social media
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

      {/* Blog posts with related social media */}
      {filteredContent.length > 0 && (
        <div className="space-y-8">
          {filteredContent.map((item: any) => (
            <BlogPostWithSocial
              key={item.blog_post.id}
              blogPost={item.blog_post}
              relatedSocialPosts={item.related_social_posts}
              isExpanded={expandedPosts.has(item.blog_post.id)}
              onToggleExpand={() => toggleExpanded(item.blog_post.id)}
              getPlatformIcon={getPlatformIcon}
              getPlatformStyle={getPlatformStyle}
            />
          ))}
        </div>
      )}

      {/* Standalone social media posts */}
      {filteredStandalone.length > 0 && viewMode !== 'blog' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Hash className="h-5 w-5" />
            Samodzielne posty Social Media
          </h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredStandalone.map((post: any) => (
              <StandaloneSocialPost
                key={post.id}
                post={post}
                getPlatformIcon={getPlatformIcon}
                getPlatformStyle={getPlatformStyle}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {filteredContent.length === 0 && filteredStandalone.length === 0 && (
        <Card className="p-8 text-center">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Brak treści do wyświetlenia</h3>
          <p className="text-muted-foreground">
            Ten plan nie zawiera jeszcze żadnych treści
          </p>
        </Card>
      )}
    </div>
  )
}

// Blog post with related social media component
function BlogPostWithSocial({ 
  blogPost, 
  relatedSocialPosts, 
  isExpanded, 
  onToggleExpand,
  getPlatformIcon,
  getPlatformStyle 
}: any) {
  const blogVariant = blogPost.variants?.[0]
  
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Blog Post Card */}
      <Card className="overflow-hidden hover:shadow-lg transition-all duration-300">
        <div className="p-6 space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-xl font-bold text-foreground mb-2">
                {blogPost.topic.title}
              </h3>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  {format(new Date(blogPost.created_at), 'dd MMM yyyy', { locale: pl })}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {Math.ceil((blogVariant?.content_text?.length || 0) / 1000)} min czytania
                </span>
              </div>
            </div>
            <Badge variant="secondary">
              <FileText className="h-3 w-3 mr-1" />
              Blog
            </Badge>
          </div>

          {/* Description */}
          {blogPost.topic.description && (
            <p className="text-muted-foreground">
              {blogPost.topic.description}
            </p>
          )}

          {/* Expand/Collapse button */}
          <Button
            variant="outline"
            size="sm"
            onClick={onToggleExpand}
            className="w-full"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4 mr-2" />
                Zwiń treść
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-2" />
                Pokaż pełną treść i powiązane posty ({relatedSocialPosts.length})
              </>
            )}
          </Button>

          {/* Expanded content */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                {/* Full blog content */}
                {blogVariant ? (
                  <div className="prose prose-sm max-w-none pt-4 border-t">
                    <div className="whitespace-pre-wrap text-foreground">
                      {blogVariant.content_text}
                    </div>
                  </div>
                ) : (
                  <div className="pt-4 border-t text-muted-foreground">
                    <p className="italic">Treść bloga jest w trakcie generowania...</p>
                  </div>
                )}

                {/* Blog interactions */}
                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center gap-4">
                    <button className="flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors">
                      <Heart className="h-4 w-4" />
                      <span className="text-sm">142</span>
                    </button>
                    <button className="flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors">
                      <MessageCircle className="h-4 w-4" />
                      <span className="text-sm">23</span>
                    </button>
                    <button className="flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors">
                      <Share2 className="h-4 w-4" />
                      <span className="text-sm">Udostępnij</span>
                    </button>
                  </div>
                  <button className="text-muted-foreground hover:text-primary transition-colors">
                    <Bookmark className="h-4 w-4" />
                  </button>
                </div>

                {/* Related social media posts */}
                {relatedSocialPosts.length > 0 && (
                  <div className="space-y-4 pt-6 border-t">
                    <h4 className="font-semibold flex items-center gap-2">
                      <Link2 className="h-4 w-4" />
                      Powiązane posty social media
                    </h4>
                    <div className="grid gap-4 md:grid-cols-2">
                      {relatedSocialPosts.map((socialPost: any) => (
                        <SocialMediaPost
                          key={socialPost.id}
                          post={socialPost}
                          getPlatformIcon={getPlatformIcon}
                          getPlatformStyle={getPlatformStyle}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </Card>
    </motion.div>
  )
}

// Social media post component
function SocialMediaPost({ post, getPlatformIcon, getPlatformStyle }: any) {
  const [expandedVariants, setExpandedVariants] = useState<Set<number>>(new Set())
  
  // Group variants by platform
  const variantsByPlatform = post.variants?.reduce((acc: any, variant: any) => {
    const platform = variant.platform_name?.toLowerCase() || 'unknown'
    if (!acc[platform]) {
      acc[platform] = []
    }
    acc[platform].push(variant)
    return acc
  }, {}) || {}
  
  const toggleExpanded = (variantId: number) => {
    const newExpanded = new Set(expandedVariants)
    if (newExpanded.has(variantId)) {
      newExpanded.delete(variantId)
    } else {
      newExpanded.add(variantId)
    }
    setExpandedVariants(newExpanded)
  }
  
  return (
    <>
      {Object.entries(variantsByPlatform).map(([platform, variants]: [string, any[]]) => (
        <Card 
          key={`${post.id}-${platform}`} 
          className={`overflow-hidden transition-all duration-300 ${getPlatformStyle(platform)}`}
        >
          <div className="p-4 space-y-3">
            {/* Platform header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getPlatformIcon(platform)}
                <span className="font-medium capitalize">{platform}</span>
                {variants.length > 1 && (
                  <Badge variant="secondary" className="text-xs">
                    {variants.length} wersje
                  </Badge>
                )}
              </div>
              <Badge variant="outline" className="text-xs">
                <Link2 className="h-3 w-3 mr-1" />
                Powiązany
              </Badge>
            </div>

            {/* Post title */}
            <h5 className="font-medium text-sm">{post.topic.title}</h5>

            {/* Show first variant by default */}
            {variants.map((variant: any, index: number) => {
              const isExpanded = expandedVariants.has(variant.id)
              const isFirstVariant = index === 0
              
              // Show only first variant, or all if there's only one
              if (!isFirstVariant && variants.length > 1) {
                return null
              }
              
              return (
                <div key={variant.id} className="text-sm text-foreground">
                  {!isExpanded && variant.content_text.length > 280 ? (
                    <>
                      {variant.content_text.substring(0, 280)}...
                      <button
                        onClick={() => toggleExpanded(variant.id)}
                        className="text-primary hover:underline ml-1"
                      >
                        więcej
                      </button>
                    </>
                  ) : (
                    <div className="whitespace-pre-wrap">
                      {variant.content_text}
                      {isExpanded && variant.content_text.length > 280 && (
                        <button
                          onClick={() => toggleExpanded(variant.id)}
                          className="text-primary hover:underline ml-1"
                        >
                          zwiń
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
            {/* Mock image placeholder for Instagram */}
            {platform === 'instagram' && (
              <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <Eye className="h-8 w-8 text-muted-foreground" />
              </div>
            )}

            {/* Platform interactions */}
            <div className="flex items-center justify-between pt-3 border-t">
              <div className="flex items-center gap-3">
                <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm transition-colors">
                  <Heart className="h-4 w-4" />
                  <span>Lubię</span>
                </button>
                <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm transition-colors">
                  <MessageCircle className="h-4 w-4" />
                  <span>Komentuj</span>
                </button>
                <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm transition-colors">
                  <Share2 className="h-4 w-4" />
                  <span>Udostępnij</span>
                </button>
              </div>
            </div>
          </div>
        </Card>
      ))}
    </>
  )
}

// Standalone social post component
function StandaloneSocialPost({ post, getPlatformIcon, getPlatformStyle }: any) {
  const [expandedVariants, setExpandedVariants] = useState<Set<number>>(new Set())
  
  const toggleVariantExpanded = (variantId: number) => {
    const newExpanded = new Set(expandedVariants)
    if (newExpanded.has(variantId)) {
      newExpanded.delete(variantId)
    } else {
      newExpanded.add(variantId)
    }
    setExpandedVariants(newExpanded)
  }
  
  // Group variants by platform
  const variantsByPlatform = post.variants?.reduce((acc: any, variant: any) => {
    const platform = variant.platform_name?.toLowerCase() || 'unknown'
    if (!acc[platform]) {
      acc[platform] = []
    }
    acc[platform].push(variant)
    return acc
  }, {}) || {}
  
  return (
    <>
      {Object.entries(variantsByPlatform).map(([platform, variants]: [string, any[]]) => {
        // Show only the first variant for each platform
        const variant = variants[0]
        const isExpanded = expandedVariants.has(variant.id)
        
        return (
          <Card 
            key={`${post.id}-${platform}`} 
            className={`overflow-hidden transition-all duration-300 ${getPlatformStyle(platform)}`}
          >
            <div className="p-4 space-y-3">
              {/* Platform header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getPlatformIcon(platform)}
                  <span className="font-medium capitalize">{platform}</span>
                  {variants.length > 1 && (
                    <Badge variant="secondary" className="text-xs ml-2">
                      {variants.length} wersje
                    </Badge>
                  )}
                </div>
                <Badge variant="secondary" className="text-xs">
                  <Hash className="h-3 w-3 mr-1" />
                  Samodzielny
                </Badge>
              </div>

              {/* Post title */}
              <h5 className="font-medium text-sm">{post.topic.title}</h5>

              {/* Post content */}
              <div className="text-sm text-foreground">
                {!isExpanded && variant.content_text.length > 280 ? (
                  <>
                    {variant.content_text.substring(0, 280)}...
                    <button
                      onClick={() => toggleVariantExpanded(variant.id)}
                      className="text-primary hover:underline ml-1"
                    >
                      więcej
                    </button>
                  </>
                ) : (
                  <div className="whitespace-pre-wrap">
                    {variant.content_text}
                    {isExpanded && variant.content_text.length > 280 && (
                      <button
                        onClick={() => toggleVariantExpanded(variant.id)}
                        className="text-primary hover:underline ml-1"
                      >
                        zwiń
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Mock image placeholder for Instagram */}
              {platform === 'instagram' && (
                <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                  <Eye className="h-8 w-8 text-muted-foreground" />
                </div>
              )}

              {/* Platform interactions */}
              <div className="flex items-center justify-between pt-3 border-t">
                <div className="flex items-center gap-3">
                  <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm transition-colors">
                    <Heart className="h-4 w-4" />
                    <span>Lubię</span>
                  </button>
                  <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm transition-colors">
                    <MessageCircle className="h-4 w-4" />
                    <span>Komentuj</span>
                  </button>
                  <button className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm transition-colors">
                    <Share2 className="h-4 w-4" />
                    <span>Udostępnij</span>
                  </button>
                </div>
              </div>
            </div>
          </Card>
        )
      })}
    </>
  )
}