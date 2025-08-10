import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
// Tymczasowo używamy natywnych elementów HTML zamiast komponentów UI
// import { Checkbox } from '@/components/ui/checkbox'
// import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { Loader2, Play, CheckCircle2, XCircle } from 'lucide-react'
import { api } from '@/lib/api'

interface VariantGenerationControlProps {
  contentPlanId: number
  approvedSmTopics: Array<{
    id: number
    title: string
    hasVariants: boolean
  }>
}

export const VariantGenerationControl: React.FC<VariantGenerationControlProps> = ({
  contentPlanId,
  approvedSmTopics
}) => {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [selectedTopics, setSelectedTopics] = useState<number[]>([])
  const [generateAll, setGenerateAll] = useState(false)

  const topicsNeedingVariants = approvedSmTopics.filter(t => !t.hasVariants)

  const generateVariantsMutation = useMutation({
    mutationFn: async (data: { topicIds?: number[]; generateAll: boolean }) => {
      return api.contentPlans.generateSmVariants(contentPlanId, {
        topic_ids: data.topicIds,
        generate_all_approved: data.generateAll
      })
    },
    onSuccess: () => {
      toast({
        title: 'Generowanie rozpoczęte',
        description: 'Warianty treści są generowane w tle.'
      })
      queryClient.invalidateQueries({ queryKey: ['contentPlan', contentPlanId] })
      setSelectedTopics([])
      setGenerateAll(false)
    },
    onError: (error: any) => {
      toast({
        title: 'Błąd',
        description: error.response?.data?.detail || 'Nie udało się rozpocząć generowania',
        variant: 'destructive'
      })
    }
  })

  const handleGenerateClick = () => {
    if (generateAll) {
      generateVariantsMutation.mutate({ generateAll: true })
    } else if (selectedTopics.length > 0) {
      generateVariantsMutation.mutate({ topicIds: selectedTopics, generateAll: false })
    }
  }

  const toggleTopicSelection = (topicId: number) => {
    setSelectedTopics(prev => 
      prev.includes(topicId) 
        ? prev.filter(id => id !== topicId)
        : [...prev, topicId]
    )
    setGenerateAll(false)
  }

  if (topicsNeedingVariants.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Generowanie wariantów SM</CardTitle>
          <CardDescription>
            Wszystkie zatwierdzone tematy mają już wygenerowane warianty
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="h-5 w-5" />
            <span>Wszystkie warianty zostały wygenerowane</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generowanie wariantów SM</CardTitle>
        <CardDescription>
          Wybierz tematy, dla których chcesz wygenerować warianty treści
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center space-x-2 p-3 bg-muted rounded-lg">
            <input
              type="checkbox"
              id="generate-all"
              checked={generateAll}
              onChange={(e) => {
                setGenerateAll(e.target.checked)
                if (e.target.checked) setSelectedTopics([])
              }}
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <label 
              htmlFor="generate-all" 
              className="text-sm font-medium cursor-pointer flex-1"
            >
              Generuj dla wszystkich zatwierdzonych tematów ({topicsNeedingVariants.length})
            </label>
          </div>

          {!generateAll && (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {topicsNeedingVariants.map(topic => (
                <div key={topic.id} className="flex items-center space-x-2 p-2 hover:bg-muted rounded">
                  <input
                    type="checkbox"
                    id={`topic-${topic.id}`}
                    checked={selectedTopics.includes(topic.id)}
                    onChange={() => toggleTopicSelection(topic.id)}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <label 
                    htmlFor={`topic-${topic.id}`} 
                    className="text-sm cursor-pointer flex-1"
                  >
                    {topic.title}
                  </label>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            {generateAll 
              ? `Zostanie wygenerowanych ${topicsNeedingVariants.length} zestawów wariantów`
              : `Wybrano ${selectedTopics.length} tematów`
            }
          </div>
          
          <Button
            onClick={handleGenerateClick}
            disabled={!generateAll && selectedTopics.length === 0 || generateVariantsMutation.isLoading}
          >
            {generateVariantsMutation.isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generowanie...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Generuj warianty
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}