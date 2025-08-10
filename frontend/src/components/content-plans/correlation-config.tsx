'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link2, Unlink, Info, Settings2, BarChart3, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'

import { api } from '@/lib/api'
import { Card } from '@/components/ui/cards'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select } from '@/components/ui/select'
import { useToast } from '@/hooks/use-toast'
import { cn } from '@/lib/utils'

interface CorrelationConfigProps {
  contentPlanId: number
  blogPostsQuota: number
  smPostsQuota: number
  isReadOnly?: boolean
}

interface CorrelationRule {
  id?: number
  rule_type: string
  sm_posts_per_blog: number
  brief_based_sm_posts: number
  standalone_sm_posts: number
  platform_rules?: Record<string, number>
  correlation_strength: string
  timing_strategy: string
}

const PLATFORMS = [
  { value: 'linkedin', label: 'LinkedIn', icon: '💼' },
  { value: 'facebook', label: 'Facebook', icon: '👍' },
  { value: 'instagram', label: 'Instagram', icon: '📸' },
  { value: 'twitter', label: 'Twitter/X', icon: '🐦' },
]

export function CorrelationConfig({
  contentPlanId,
  blogPostsQuota,
  smPostsQuota,
  isReadOnly = false
}: CorrelationConfigProps) {
  const [localRules, setLocalRules] = useState<CorrelationRule>({
    rule_type: 'blog_to_sm',
    sm_posts_per_blog: 2,
    brief_based_sm_posts: 0,
    standalone_sm_posts: 0,
    platform_rules: {},
    correlation_strength: 'moderate',
    timing_strategy: 'distributed'
  })
  const [isAdvancedMode, setIsAdvancedMode] = useState(false)
  
  const queryClient = useQueryClient()
  const { success: toastSuccess, error: toastError } = useToast()

  // Fetch existing rules
  const { data: existingRules } = useQuery({
    queryKey: ['correlationRules', contentPlanId],
    queryFn: async () => {
      return await api.contentPlans.getCorrelationRules(contentPlanId)
    },
    enabled: !!contentPlanId
  })

  // Update local state when data is fetched
  useEffect(() => {
    if (existingRules) {
      setLocalRules(existingRules)
      // Enable advanced mode if platform rules exist
      if (existingRules.platform_rules && Object.keys(existingRules.platform_rules).length > 0) {
        setIsAdvancedMode(true)
      }
    }
  }, [existingRules])

  // Calculate distribution
  const { data: distribution } = useQuery({
    queryKey: ['smDistribution', contentPlanId, blogPostsQuota],
    queryFn: async () => {
      return await api.contentPlans.getSmDistribution(contentPlanId, blogPostsQuota)
    },
    enabled: !!contentPlanId && !!blogPostsQuota
  })

  // Save rules mutation
  const saveRulesMutation = useMutation({
    mutationFn: async (rules: CorrelationRule) => {
      return await api.contentPlans.createOrUpdateCorrelationRules(contentPlanId, {
        ...rules,
        content_plan_id: contentPlanId
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['correlationRules', contentPlanId] })
      queryClient.invalidateQueries({ queryKey: ['smDistribution', contentPlanId] })
      toastSuccess('Reguły korelacji zostały zapisane')
    },
    onError: (error: any) => {
      toastError(error.response?.data?.detail || 'Błąd podczas zapisywania reguł')
    }
  })

  const handleRuleChange = (field: keyof CorrelationRule, value: any) => {
    setLocalRules(prev => ({ ...prev, [field]: value }))
  }

  const handlePlatformRuleChange = (platform: string, count: number) => {
    setLocalRules(prev => ({
      ...prev,
      platform_rules: {
        ...prev.platform_rules,
        [platform]: count
      }
    }))
  }

  const calculateTotalPosts = () => {
    const blogCorrelated = blogPostsQuota * localRules.sm_posts_per_blog
    const briefBased = localRules.brief_based_sm_posts
    const standalone = localRules.standalone_sm_posts
    return blogCorrelated + briefBased + standalone
  }

  const totalCalculated = calculateTotalPosts()
  const isOverQuota = totalCalculated > smPostsQuota

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Konfiguracja korelacji treści</h3>
          <p className="text-sm text-gray-600 mt-1">
            Określ jak posty na social media mają być powiązane z treściami blogowymi
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsAdvancedMode(!isAdvancedMode)}
          className="gap-2"
        >
          <Settings2 className="w-4 h-4" />
          {isAdvancedMode ? 'Tryb prosty' : 'Tryb zaawansowany'}
        </Button>
      </div>

      <div className="space-y-6">
        {/* Basic correlation settings */}
        <div className="space-y-4">
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Link2 className="w-4 h-4" />
              Posty SM skorelowane z blogami
            </label>
            <div className="flex items-center gap-4">
              <Input
                type="number"
                min="0"
                max="10"
                value={localRules.sm_posts_per_blog}
                onChange={(e) => handleRuleChange('sm_posts_per_blog', parseInt(e.target.value) || 0)}
                disabled={isReadOnly}
                className="w-20"
              />
              <span className="text-sm text-gray-600">
                postów SM na każdy wpis blogowy
              </span>
              <Badge variant="secondary">
                = {blogPostsQuota * localRules.sm_posts_per_blog} postów
              </Badge>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Każdy wpis blogowy będzie miał przypisane posty zapowiadające na social media
            </p>
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <BarChart3 className="w-4 h-4" />
              Posty SM oparte na briefach
            </label>
            <div className="flex items-center gap-4">
              <Input
                type="number"
                min="0"
                value={localRules.brief_based_sm_posts}
                onChange={(e) => handleRuleChange('brief_based_sm_posts', parseInt(e.target.value) || 0)}
                disabled={isReadOnly}
                className="w-20"
              />
              <span className="text-sm text-gray-600">
                postów opartych na briefach
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Posty generowane na podstawie informacji z briefów (wydarzenia, aktualności)
            </p>
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Unlink className="w-4 h-4" />
              Niezależne posty SM
            </label>
            <div className="flex items-center gap-4">
              <Input
                type="number"
                min="0"
                value={localRules.standalone_sm_posts}
                onChange={(e) => handleRuleChange('standalone_sm_posts', parseInt(e.target.value) || 0)}
                disabled={isReadOnly}
                className="w-20"
              />
              <span className="text-sm text-gray-600">
                niezależnych postów
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Posty niezwiązane z blogami (porady, pytania do społeczności, behind-the-scenes)
            </p>
          </div>
        </div>

        {/* Advanced settings */}
        {isAdvancedMode && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4 pt-4 border-t"
          >
            <h4 className="font-medium text-gray-900">Ustawienia zaawansowane</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Siła korelacji
                </label>
                <Select
                  value={localRules.correlation_strength}
                  onChange={(value: string) => handleRuleChange('correlation_strength', value)}
                  disabled={isReadOnly}
                  options={[
                    { value: "tight", label: "Ścisła" },
                    { value: "moderate", label: "Umiarkowana" },
                    { value: "loose", label: "Luźna" }
                  ]}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Strategia czasowa
                </label>
                <Select
                  value={localRules.timing_strategy}
                  onChange={(value: string) => handleRuleChange('timing_strategy', value)}
                  disabled={isReadOnly}
                  options={[
                    { value: "distributed", label: "Rozproszona" },
                    { value: "clustered", label: "Skupiona" },
                    { value: "sequential", label: "Sekwencyjna" }
                  ]}
                />
              </div>
            </div>

            {/* Platform-specific rules */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Dystrybucja na platformy
              </label>
              <div className="grid grid-cols-2 gap-3">
                {PLATFORMS.map(platform => (
                  <div key={platform.value} className="flex items-center gap-2">
                    <span className="text-lg">{platform.icon}</span>
                    <span className="text-sm flex-1">{platform.label}</span>
                    <Input
                      type="number"
                      min="0"
                      value={localRules.platform_rules?.[platform.value] || 0}
                      onChange={(e) => handlePlatformRuleChange(platform.value, parseInt(e.target.value) || 0)}
                      disabled={isReadOnly}
                      className="w-16"
                    />
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Summary */}
        <div className={cn(
          "p-4 rounded-lg border-2",
          isOverQuota ? "border-red-200 bg-red-50" : "border-green-200 bg-green-50"
        )}>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">Podsumowanie</h4>
              <div className="mt-2 space-y-1 text-sm">
                <div>Posty powiązane z blogami: <strong>{blogPostsQuota * localRules.sm_posts_per_blog}</strong></div>
                <div>Posty oparte na briefach: <strong>{localRules.brief_based_sm_posts}</strong></div>
                <div>Posty niezależne: <strong>{localRules.standalone_sm_posts}</strong></div>
              </div>
            </div>
            <div className="text-right">
              <div className={cn(
                "text-2xl font-bold",
                isOverQuota ? "text-red-600" : "text-green-600"
              )}>
                {totalCalculated} / {smPostsQuota}
              </div>
              <div className="text-sm text-gray-600">
                postów SM łącznie
              </div>
              {isOverQuota && (
                <p className="text-xs text-red-600 mt-1">
                  Przekroczono limit o {totalCalculated - smPostsQuota}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Save button */}
        {!isReadOnly && (
          <div className="flex justify-end">
            <Button
              onClick={() => saveRulesMutation.mutate(localRules)}
              disabled={saveRulesMutation.isPending || isOverQuota}
              className="gap-2"
            >
              {saveRulesMutation.isPending && (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              Zapisz reguły korelacji
            </Button>
          </div>
        )}
      </div>
    </Card>
  )
}