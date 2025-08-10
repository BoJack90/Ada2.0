'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ChevronLeft, ChevronRight, Check, Calendar, Settings, FileText, Link2, Brain } from 'lucide-react'

import { api } from '@/lib/api'
import { ContentPlanWizardData, ContentPlanCreate, SchedulingMode } from '@/types'
import { useOrganizationStore } from '@/stores'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { UseFormRegister, FieldErrors, UseFormWatch, UseFormSetValue } from 'react-hook-form'
import { AdvancedGenerationStep } from './advanced-generation-step'

// Validation schema
const wizardSchema = z.object({
  // Step 1: Plan Definition
  plan_period: z.string().min(1, 'Okres planowania jest wymagany'),
  blog_posts_quota: z.number().min(1, 'Minimalna liczba wpisów blogowych to 1').max(100, 'Maksymalna liczba wpisów to 100'),
  sm_posts_quota: z.number().min(1, 'Minimalna liczba postów SM to 1').max(500, 'Maksymalna liczba postów to 500'),
  
  // Step 2: Context and Strategy
  correlate_posts: z.boolean(),
  
  // Step 3: Correlation
  sm_posts_per_blog: z.number().min(0).max(10).optional(),
  brief_based_sm_posts: z.number().min(0).optional(),
  standalone_sm_posts: z.number().min(0).optional(),
  
  // Step 4: Schedule
  scheduling_mode: z.enum(['auto', 'with_guidelines', 'visual']),
  scheduling_guidelines: z.object({
    days_of_week: z.array(z.string()).optional(),
    preferred_times: z.array(z.string()).optional(),
    avoid_dates: z.array(z.string()).optional(),
  }).optional(),
  
  // Step 5: Advanced Generation
  generation_method: z.enum(['standard', 'deep_reasoning']).optional(),
  use_deep_research: z.boolean().optional(),
  research_depth: z.enum(['basic', 'deep', 'comprehensive']).optional(),
  analyze_competitors: z.boolean().optional(),
  include_trends: z.boolean().optional(),
  optimize_seo: z.boolean().optional(),
})

type WizardFormData = z.infer<typeof wizardSchema>

interface CreatePlanWizardProps {
  organizationId: number
  onSuccess?: (planId: number) => void
  onCancel?: () => void
}

interface StepComponentProps {
  register: UseFormRegister<WizardFormData>
  errors: FieldErrors<WizardFormData>
  watch: UseFormWatch<WizardFormData>
  setValue: UseFormSetValue<WizardFormData>
}

interface ContextStrategyStepProps extends StepComponentProps {
  monthlyBriefFile: File | null
  onFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void
}

interface ScheduleStepProps extends StepComponentProps {
  schedulingMode?: SchedulingMode
}

export function CreatePlanWizard({ organizationId, onSuccess, onCancel }: CreatePlanWizardProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [monthlyBriefFile, setMonthlyBriefFile] = useState<File | null>(null)
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
    getValues,
    trigger
  } = useForm<WizardFormData>({
    resolver: zodResolver(wizardSchema),
    mode: 'onChange',
    defaultValues: {
      plan_period: '',
      blog_posts_quota: 4,
      sm_posts_quota: 12,
      correlate_posts: true,
      sm_posts_per_blog: 2,
      brief_based_sm_posts: 0,
      standalone_sm_posts: 0,
      scheduling_mode: 'auto', // Zmiana: domyślnie auto
      scheduling_guidelines: {
        days_of_week: [],
        preferred_times: [],
        avoid_dates: []
      },
      generation_method: 'standard',
      use_deep_research: false,
      research_depth: 'deep',
      analyze_competitors: false,
      include_trends: false,
      optimize_seo: false
    }
  })

  const watchedValues = watch()
  const schedulingMode = watch('scheduling_mode')

  const mutation = useMutation({
    mutationFn: async (data: WizardFormData) => {
      console.log('[CreatePlanWizard] Mutation starting with data:', data)
      console.log('[CreatePlanWizard] generation_method from form:', data.generation_method)
      console.log('[CreatePlanWizard] use_deep_research from form:', data.use_deep_research)
      console.log('[CreatePlanWizard] Current step in mutation:', currentStep)
      
      // Double-check we're on the final step
      if (currentStep !== 5) {
        console.error('[CreatePlanWizard] Mutation called but not on step 5!')
        throw new Error('Form submitted too early')
      }
      
      if (!organizationId) {
        throw new Error('Nie wybrano organizacji')
      }

      // Create ContentPlanCreate payload for API call
      const contentPlanData: ContentPlanCreate = {
        plan_period: data.plan_period,
        blog_posts_quota: data.blog_posts_quota,
        sm_posts_quota: data.sm_posts_quota,
        correlate_posts: data.correlate_posts,
        scheduling_mode: data.scheduling_mode || 'auto', // Fallback to 'auto' if not selected
        scheduling_preferences: data.scheduling_guidelines ? JSON.stringify(data.scheduling_guidelines) : undefined,
        organization_id: organizationId,
        meta_data: {
          generation_method: data.generation_method || 'standard',
          use_deep_research: data.use_deep_research || false,
          research_depth: data.research_depth || 'deep',
          analyze_competitors: data.analyze_competitors || false,
          include_trends: data.include_trends || false,
          optimize_seo: data.optimize_seo || false
        }
      } as any

      console.log('[CreatePlanWizard] Calling API with:', contentPlanData)
      console.log('[CreatePlanWizard] meta_data specifically:', contentPlanData.meta_data)
      console.log('[CreatePlanWizard] meta_data type:', typeof contentPlanData.meta_data)
      console.log('[CreatePlanWizard] Monthly brief file:', monthlyBriefFile)

      // Use createWithFile to handle both data and optional file upload
      const contentPlan = await api.contentPlans.createWithFile(contentPlanData, monthlyBriefFile || undefined)
      
      // Create correlation rules if correlation is enabled
      if (data.correlate_posts) {
        const correlationRules = {
          content_plan_id: contentPlan.id,
          rule_type: 'blog_to_sm',
          sm_posts_per_blog: data.sm_posts_per_blog || 2,
          brief_based_sm_posts: data.brief_based_sm_posts || 0,
          standalone_sm_posts: data.standalone_sm_posts || 0,
          correlation_strength: 'moderate',
          timing_strategy: 'distributed'
        }
        
        console.log('[CreatePlanWizard] Creating correlation rules:', correlationRules)
        await api.contentPlans.createOrUpdateCorrelationRules(contentPlan.id, correlationRules)
      }
      
      return contentPlan
    },
    onSuccess: (contentPlan) => {
      console.log('[CreatePlanWizard] Plan created successfully:', contentPlan)
      console.log('[CreatePlanWizard] Current step when success:', currentStep)
      queryClient.invalidateQueries({ queryKey: ['contentPlans', organizationId] })
      onSuccess?.(contentPlan.id)
    },
    onError: (error: any) => {
      console.error('[CreatePlanWizard] Błąd podczas tworzenia planu treści:', error)
      console.error('[CreatePlanWizard] Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
    }
  })
  
  // Debug currentStep changes
  useEffect(() => {
    console.log('[CreatePlanWizard] currentStep changed to:', currentStep)
    console.log('[CreatePlanWizard] Mutation state:', {
      isPending: mutation.isPending,
      isError: mutation.isError,
      isSuccess: mutation.isSuccess
    })
  }, [currentStep, mutation.isPending, mutation.isError, mutation.isSuccess])

  const steps = [
    {
      id: 1,
      title: 'Definicja Planu',
      description: 'Okres i kwoty treści',
      icon: FileText,
      component: 'PlanDefinitionStep'
    },
    {
      id: 2,
      title: 'Kontekst i Strategia',
      description: 'Brief i korelacja treści',
      icon: Settings,
      component: 'ContextStrategyStep'
    },
    {
      id: 3,
      title: 'Korelacja treści',
      description: 'Powiązania blog-SM',
      icon: Link2,
      component: 'CorrelationStep'
    },
    {
      id: 4,
      title: 'Harmonogram',
      description: 'Tryb planowania',
      icon: Calendar,
      component: 'ScheduleStep'
    },
    {
      id: 5,
      title: 'Metoda AI',
      description: 'Sposób generowania',
      icon: Brain,
      component: 'AdvancedGenerationStep'
    }
  ]

  const handleNext = async () => {
    console.log('[CreatePlanWizard] handleNext called, currentStep:', currentStep)
    console.log('[CreatePlanWizard] Current values:', getValues())
    const isCurrentStepValid = await trigger()
    console.log('[CreatePlanWizard] Step valid:', isCurrentStepValid)
    if (isCurrentStepValid && currentStep < 5) {
      console.log('[CreatePlanWizard] Moving to step:', currentStep + 1)
      setCurrentStep(currentStep + 1)
      console.log('[CreatePlanWizard] Step updated to:', currentStep + 1)
    } else {
      console.log('[CreatePlanWizard] Cannot proceed:', { isCurrentStepValid, currentStep })
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setMonthlyBriefFile(file)
    }
  }

  const onSubmit = (data: WizardFormData) => {
    console.log('[CreatePlanWizard] onSubmit called with data:', data)
    console.log('[CreatePlanWizard] Current step:', currentStep)
    console.log('[CreatePlanWizard] Can proceed:', canProceed)
    console.log('[CreatePlanWizard] Organization ID:', organizationId)
    console.log('[CreatePlanWizard] Monthly brief file:', monthlyBriefFile)
    console.trace('[CreatePlanWizard] onSubmit call stack')
    
    // Only submit if we're on the last step
    if (currentStep === 5) {
      mutation.mutate(data)
    } else {
      console.error('[CreatePlanWizard] onSubmit called but not on step 5! Current step:', currentStep)
    }
  }

  const isStepValid = (stepNumber: number) => {
    const result = (() => {
      switch (stepNumber) {
        case 1:
          return watchedValues.plan_period && watchedValues.blog_posts_quota > 0 && watchedValues.sm_posts_quota > 0
        case 2:
          return true // Always valid, context/brief step
        case 3:
          // Correlation step - check if total SM posts don't exceed quota
          const smPerBlog = watchedValues.sm_posts_per_blog || 2
          const briefBased = watchedValues.brief_based_sm_posts || 0
          const standalone = watchedValues.standalone_sm_posts || 0
          const totalSm = (watchedValues.blog_posts_quota * smPerBlog) + briefBased + standalone
          return totalSm <= watchedValues.sm_posts_quota
        case 4:
          return true // Always valid since scheduling_mode has default value
        case 5:
          return true // Always valid, generation_method has default
        default:
          return false
      }
    })()
    
    console.log(`[CreatePlanWizard] Step ${stepNumber} validation:`, {
      result,
      watchedValues: watchedValues,
      schedulingMode: watchedValues.scheduling_mode
    })
    
    return result
  }

  const canProceed = isStepValid(currentStep)

  // Debug log for button state
  console.log('[CreatePlanWizard] Button state:', {
    currentStep,
    canProceed,
    isPending: mutation.isPending,
    isLastStep: currentStep >= steps.length,
    buttonDisabled: !canProceed || mutation.isPending
  })

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Nowy Plan Treści</h2>
        <p className="text-gray-600">Utwórz nowy plan treści dla swojej organizacji</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const isActive = currentStep === step.id
            const isCompleted = currentStep > step.id
            const isValidStep = isStepValid(step.id)
            
            return (
              <div key={step.id} className="flex items-center">
                <div className="flex flex-col items-center">
                  <motion.div
                    className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors ${
                      isCompleted 
                        ? 'bg-green-500 border-green-500 text-white' 
                        : isActive 
                          ? 'bg-blue-500 border-blue-500 text-white' 
                          : 'bg-gray-100 border-gray-300 text-gray-400'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {isCompleted ? (
                      <Check className="w-6 h-6" />
                    ) : (
                      <step.icon className="w-6 h-6" />
                    )}
                  </motion.div>
                  <div className="mt-2 text-center">
                    <div className={`text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-500'}`}>
                      {step.title}
                    </div>
                    <div className="text-xs text-gray-400">{step.description}</div>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-4 ${isCompleted ? 'bg-green-500' : 'bg-gray-200'}`} />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Form */}
      <form 
        onSubmit={(e) => {
          console.log('[CreatePlanWizard] Form onSubmit event triggered, currentStep:', currentStep)
          e.preventDefault()
          e.stopPropagation()
          // Never submit the form through the form's onSubmit
          return false
        }}
        onKeyDown={(e) => {
          // Prevent Enter key from submitting form
          if (e.key === 'Enter') {
            console.log('[CreatePlanWizard] Enter key prevented on step:', currentStep)
            e.preventDefault()
          }
        }}
        className="space-y-6"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            {currentStep === 1 && (
              <PlanDefinitionStep
                register={register}
                errors={errors}
                watch={watch}
                setValue={setValue}
              />
            )}
            {currentStep === 2 && (
              <ContextStrategyStep
                register={register}
                errors={errors}
                watch={watch}
                setValue={setValue}
                monthlyBriefFile={monthlyBriefFile}
                onFileChange={handleFileChange}
              />
            )}
            {currentStep === 3 && (
              <CorrelationStep
                register={register}
                errors={errors}
                watch={watch}
                setValue={setValue}
              />
            )}
            {currentStep === 4 && (
              <ScheduleStep
                register={register}
                errors={errors}
                watch={watch}
                setValue={setValue}
                schedulingMode={schedulingMode}
              />
            )}
            {currentStep === 5 && (
              <AdvancedGenerationStep
                register={register}
                errors={errors}
                watch={watch}
                setValue={setValue}
              />
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-6">
          <div className="flex space-x-3">
            {currentStep > 1 && (
              <button
                type="button"
                onClick={handlePrevious}
                className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 transition-colors"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Wstecz
              </button>
            )}
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 transition-colors"
              >
                Anuluj
              </button>
            )}
          </div>

          <div>
            {currentStep < 5 ? (
              <button
                type="button"
                onClick={handleNext}
                disabled={!canProceed}
                className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Dalej
                <ChevronRight className="w-4 h-4 ml-2" />
              </button>
            ) : (
              <button
                type="button"
                disabled={!canProceed || mutation.isPending}
                onClick={async (e) => {
                  console.log('[CreatePlanWizard] Submit button clicked', {
                    canProceed,
                    isPending: mutation.isPending,
                    disabled: !canProceed || mutation.isPending,
                    currentStep,
                    event: e
                  })
                  e.preventDefault()
                  e.stopPropagation()
                  
                  if (currentStep === 5 && canProceed && !mutation.isPending) {
                    const isValid = await trigger()
                    if (isValid) {
                      const data = getValues()
                      console.log('[CreatePlanWizard] Manually submitting form with data:', data)
                      onSubmit(data)
                    }
                  }
                }}
                className="flex items-center px-6 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {mutation.isPending ? (
                  <>
                    <LoadingSpinner size="small" className="mr-2" />
                    Tworzenie...
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    Stwórz Plan
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </form>

      {/* Error Message */}
      {mutation.isError && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="text-sm text-red-600">
            Wystąpił błąd podczas tworzenia planu treści. Spróbuj ponownie.
            {mutation.error && (
              <div className="mt-2 text-xs">
                {(mutation.error as any).response?.data?.detail || 
                 (mutation.error as any).message || 
                 'Nieznany błąd'}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Step 1: Plan Definition
export function PlanDefinitionStep({ register, errors, watch, setValue }: StepComponentProps) {
  const currentDate = new Date()
  const currentYear = currentDate.getFullYear()
  const currentMonth = currentDate.getMonth()
  
  // Generate period options (current month + next 11 months)
  const periodOptions = []
  for (let i = 0; i < 12; i++) {
    const date = new Date(currentYear, currentMonth + i, 1)
    const monthName = date.toLocaleString('pl-PL', { month: 'long' })
    const year = date.getFullYear()
    const value = `${year}-${String(date.getMonth() + 1).padStart(2, '0')}`
    periodOptions.push({
      value,
      label: `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${year}`
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Definicja Planu</h3>
        <p className="text-gray-600 mb-6">
          Określ podstawowe parametry planu treści - okres planowania i liczbę treści do wygenerowania.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Okres planowania */}
        <div>
          <label htmlFor="plan_period" className="block text-sm font-medium text-gray-700 mb-2">
            Okres planowania *
          </label>
          <select
            {...register('plan_period')}
            id="plan_period"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Wybierz okres planowania</option>
            {periodOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.plan_period && (
            <p className="mt-1 text-sm text-red-600">{errors.plan_period.message}</p>
          )}
        </div>

        {/* Spacer for grid alignment */}
        <div></div>

        {/* Liczba wpisów blogowych */}
        <div>
          <label htmlFor="blog_posts_quota" className="block text-sm font-medium text-gray-700 mb-2">
            Liczba wpisów blogowych *
          </label>
          <div className="relative">
            <input
              {...register('blog_posts_quota', { valueAsNumber: true })}
              type="number"
              id="blog_posts_quota"
              min="1"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="4"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-500 text-sm">artykułów</span>
            </div>
          </div>
          {errors.blog_posts_quota && (
            <p className="mt-1 text-sm text-red-600">{errors.blog_posts_quota.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Rekomendowane: 4-8 wpisów blogowych miesięcznie
          </p>
        </div>

        {/* Liczba postów SM */}
        <div>
          <label htmlFor="sm_posts_quota" className="block text-sm font-medium text-gray-700 mb-2">
            Liczba postów social media *
          </label>
          <div className="relative">
            <input
              {...register('sm_posts_quota', { valueAsNumber: true })}
              type="number"
              id="sm_posts_quota"
              min="1"
              max="500"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="12"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-500 text-sm">postów</span>
            </div>
          </div>
          {errors.sm_posts_quota && (
            <p className="mt-1 text-sm text-red-600">{errors.sm_posts_quota.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Rekomendowane: 12-30 postów social media miesięcznie
          </p>
        </div>
      </div>

      {/* Preview */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h4 className="text-sm font-medium text-blue-900 mb-2">Podgląd planu</h4>
        <div className="text-sm text-blue-800">
          <p>
            Plan treści na <strong>{periodOptions.find(p => p.value === watch('plan_period'))?.label || 'wybrany okres'}</strong>
          </p>
          <p className="mt-1">
            Wygenerujemy łącznie <strong>{(watch('blog_posts_quota') || 0) + (watch('sm_posts_quota') || 0)} treści</strong>:
          </p>
          <ul className="mt-1 ml-4 list-disc">
            <li>{watch('blog_posts_quota') || 0} artykułów blogowych</li>
            <li>{watch('sm_posts_quota') || 0} postów social media</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Step 2: Context and Strategy
export function ContextStrategyStep({ register, errors, watch, setValue, monthlyBriefFile, onFileChange }: ContextStrategyStepProps) {
  const correlate_posts = watch('correlate_posts')

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Kontekst i Strategia</h3>
        <p className="text-gray-600 mb-6">
          Dodaj dodatkowy kontekst do planu treści poprzez przesłanie briefu miesięcznego i skonfiguruj korelację między treściami.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Miesięczny Brief */}
        <div className="space-y-4">
          <div>
            <label htmlFor="monthly_brief" className="block text-sm font-medium text-gray-700 mb-2">
              Miesięczny Brief (opcjonalny)
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
              <div className="space-y-1 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="monthly_brief"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                  >
                    <span>Prześlij plik</span>
                    <input
                      id="monthly_brief"
                      name="monthly_brief"
                      type="file"
                      className="sr-only"
                      accept=".pdf,.doc,.docx,.txt,.rtf"
                      onChange={onFileChange}
                    />
                  </label>
                  <p className="pl-1">lub przeciągnij i upuść</p>
                </div>
                <p className="text-xs text-gray-500">
                  PDF, DOC, DOCX, TXT, RTF do 10MB
                </p>
              </div>
            </div>
            {monthlyBriefFile && (
              <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-md">
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-green-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-green-800">
                    Przesłano: {monthlyBriefFile.name}
                  </span>
                </div>
              </div>
            )}
            <p className="mt-2 text-xs text-gray-500">
              Brief miesięczny pomoże AI lepiej zrozumieć kontekst i cele biznesowe na dany miesiąc.
            </p>
          </div>
        </div>

        {/* Korelacja treści */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              Korelacja treści
            </label>
            <div className="space-y-4">
              <div className="relative flex items-start">
                <div className="flex items-center h-5">
                  <input
                    {...register('correlate_posts')}
                    id="correlate_posts"
                    type="checkbox"
                    className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="correlate_posts" className="font-medium text-gray-700">
                    Koreluj posty SM z blogami
                  </label>
                  <p className="text-gray-500 mt-1">
                    Wygenerowane posty social media będą tematycznie powiązane z artykułami blogowymi.
                  </p>
                </div>
              </div>

              {correlate_posts && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="ml-7 p-4 bg-blue-50 border border-blue-200 rounded-md"
                >
                  <h4 className="text-sm font-medium text-blue-900 mb-2">
                    Korzyści z korelacji:
                  </h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Spójna komunikacja między kanałami</li>
                    <li>• Wzajemne wzmacnianie przekazu</li>
                    <li>• Łatwiejsze zarządzanie treściami</li>
                    <li>• Zwiększona skuteczność kampanii</li>
                  </ul>
                </motion.div>
              )}
            </div>
          </div>

          {/* Strategia komunikacji */}
          <div className="p-4 bg-gray-50 border border-gray-200 rounded-md">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Strategia komunikacji
            </h4>
            <p className="text-sm text-gray-600 mb-3">
              System automatycznie wykorzysta aktywną strategię komunikacji Twojej organizacji do generowania treści.
            </p>
            <div className="flex items-center text-sm text-gray-500">
              <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Strategię można zarządzać w ustawieniach organizacji</span>
            </div>
          </div>
        </div>
      </div>

      {/* Podgląd konfiguracji */}
      <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-md">
        <h4 className="text-sm font-medium text-gray-900 mb-3">
          Podsumowanie konfiguracji
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Miesięczny brief:</span>
            <span className="ml-2 text-gray-600">
              {monthlyBriefFile ? monthlyBriefFile.name : 'Nie przesłano'}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Korelacja treści:</span>
            <span className="ml-2 text-gray-600">
              {correlate_posts ? 'Włączona' : 'Wyłączona'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Step 3: Schedule
export function ScheduleStep({ register, errors, watch, setValue, schedulingMode }: ScheduleStepProps) {
  const [selectedDays, setSelectedDays] = useState<string[]>([])
  const [preferredTimes, setPreferredTimes] = useState<string[]>([])

  const daysOfWeek = [
    { value: 'monday', label: 'Poniedziałek' },
    { value: 'tuesday', label: 'Wtorek' },
    { value: 'wednesday', label: 'Środa' },
    { value: 'thursday', label: 'Czwartek' },
    { value: 'friday', label: 'Piątek' },
    { value: 'saturday', label: 'Sobota' },
    { value: 'sunday', label: 'Niedziela' }
  ]

  const timeSlots = [
    { value: '08:00', label: '8:00' },
    { value: '10:00', label: '10:00' },
    { value: '12:00', label: '12:00' },
    { value: '14:00', label: '14:00' },
    { value: '16:00', label: '16:00' },
    { value: '18:00', label: '18:00' },
    { value: '20:00', label: '20:00' }
  ]

  const handleScheduleModeChange = (mode: SchedulingMode) => {
    console.log('[ScheduleStep] handleScheduleModeChange called with mode:', mode)
    setValue('scheduling_mode', mode)
    if (mode !== 'with_guidelines') {
      setValue('scheduling_guidelines', undefined)
    }
  }

  const handleDayToggle = (day: string) => {
    const newSelectedDays = selectedDays.includes(day)
      ? selectedDays.filter(d => d !== day)
      : [...selectedDays, day]
    
    setSelectedDays(newSelectedDays)
    setValue('scheduling_guidelines.days_of_week', newSelectedDays)
  }

  const handleTimeToggle = (time: string) => {
    const newPreferredTimes = preferredTimes.includes(time)
      ? preferredTimes.filter(t => t !== time)
      : [...preferredTimes, time]
    
    setPreferredTimes(newPreferredTimes)
    setValue('scheduling_guidelines.preferred_times', newPreferredTimes)
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Harmonogram</h3>
        <p className="text-gray-600 mb-6">
          Wybierz sposób planowania publikacji treści. Możesz wybrać automatyczne planowanie, planowanie z wytycznymi lub wizualne planowanie.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Planowanie Automatyczne */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`relative cursor-pointer rounded-lg border-2 p-6 transition-all ${
            schedulingMode === 'auto'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
          onClick={(e) => {
            e.stopPropagation()
            handleScheduleModeChange('auto')
          }}
        >
          <div className="flex items-center">
            <input
              {...register('scheduling_mode')}
              type="radio"
              value="auto"
              id="auto"
              className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              checked={schedulingMode === 'auto'}
              onChange={(e) => {
                e.stopPropagation()
                handleScheduleModeChange('auto')
              }}
            />
            <label htmlFor="auto" className="ml-3 block text-sm font-medium text-gray-700">
              Planowanie Automatyczne
            </label>
          </div>
          <div className="mt-4">
            <div className="flex items-center mb-2">
              <svg className="h-5 w-5 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Inteligentne planowanie</span>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              AI automatycznie wybierze optymalne terminy publikacji na podstawie najlepszych praktyk i analizy zaangażowania.
            </p>
            <div className="space-y-2">
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Optymalne godziny publikacji</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Równomierne rozłożenie treści</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Analiza branży i grupy docelowej</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Planowanie z Wytycznymi */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`relative cursor-pointer rounded-lg border-2 p-6 transition-all ${
            schedulingMode === 'with_guidelines'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
          onClick={(e) => {
            e.stopPropagation()
            handleScheduleModeChange('with_guidelines')
          }}
        >
          <div className="flex items-center">
            <input
              {...register('scheduling_mode')}
              type="radio"
              value="with_guidelines"
              id="with_guidelines"
              className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              checked={schedulingMode === 'with_guidelines'}
              onChange={(e) => {
                e.stopPropagation()
                handleScheduleModeChange('with_guidelines')
              }}
            />
            <label htmlFor="with_guidelines" className="ml-3 block text-sm font-medium text-gray-700">
              Planowanie z Wytycznymi
            </label>
          </div>
          <div className="mt-4">
            <div className="flex items-center mb-2">
              <svg className="h-5 w-5 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Planowanie z preferencjami</span>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Określ preferowane dni i godziny publikacji. AI zaplanuje treści zgodnie z Twoimi wytycznymi.
            </p>
            <div className="space-y-2">
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Własne preferencje czasowe</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Elastyczne dostosowanie</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Kontrola nad harmonogramem</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Planowanie Wizualne */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="relative cursor-not-allowed rounded-lg border-2 border-gray-200 bg-gray-50 p-6 opacity-60"
        >
          <div className="flex items-center">
            <input
              type="radio"
              value="visual"
              id="visual"
              className="h-4 w-4 text-gray-400 border-gray-300 cursor-not-allowed"
              disabled
            />
            <label htmlFor="visual" className="ml-3 block text-sm font-medium text-gray-400">
              Planowanie Wizualne
            </label>
          </div>
          <div className="mt-4">
            <div className="flex items-center mb-2">
              <svg className="h-5 w-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm font-medium text-gray-400">Interaktywny kalendarz</span>
            </div>
            <p className="text-sm text-gray-500 mb-4">
              Przeciągnij i upuść treści bezpośrednio na kalendarzu. Dostępne wkrótce!
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
              <div className="flex items-center">
                <svg className="h-4 w-4 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-xs font-medium text-yellow-800">Wkrótce!</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Wytyczne planowania */}
      <AnimatePresence>
        {schedulingMode === 'with_guidelines' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-6 p-6 bg-blue-50 border border-blue-200 rounded-lg"
          >
            <h4 className="text-lg font-medium text-blue-900 mb-4">Wytyczne planowania</h4>
            
            <div className="space-y-6">
              {/* Dni tygodnia */}
              <div>
                <label className="block text-sm font-medium text-blue-900 mb-3">
                  Preferowane dni publikacji
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
                  {daysOfWeek.map((day) => (
                    <button
                      key={day.value}
                      type="button"
                      onClick={() => handleDayToggle(day.value)}
                      className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        selectedDays.includes(day.value)
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-blue-700 border border-blue-300 hover:bg-blue-50'
                      }`}
                    >
                      {day.label.substring(0, 3)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Godziny */}
              <div>
                <label className="block text-sm font-medium text-blue-900 mb-3">
                  Preferowane godziny publikacji
                </label>
                <div className="grid grid-cols-3 md:grid-cols-7 gap-2">
                  {timeSlots.map((time) => (
                    <button
                      key={time.value}
                      type="button"
                      onClick={() => handleTimeToggle(time.value)}
                      className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        preferredTimes.includes(time.value)
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-blue-700 border border-blue-300 hover:bg-blue-50'
                      }`}
                    >
                      {time.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Podsumowanie */}
      <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-md">
        <h4 className="text-sm font-medium text-gray-900 mb-3">
          Podsumowanie harmonogramu
        </h4>
        <div className="text-sm text-gray-600">
          <p className="mb-2">
            <strong>Tryb planowania:</strong> {
              schedulingMode === 'auto' ? 'Automatyczny' :
              schedulingMode === 'with_guidelines' ? 'Z wytycznymi' :
              schedulingMode === 'visual' ? 'Wizualny' : 'Nie wybrano'
            }
          </p>
          {schedulingMode === 'with_guidelines' && (
            <div className="space-y-1">
              <p>
                <strong>Wybrane dni:</strong> {
                  selectedDays.length > 0 
                    ? selectedDays.map(day => daysOfWeek.find(d => d.value === day)?.label).join(', ')
                    : 'Brak preferencji'
                }
              </p>
              <p>
                <strong>Preferowane godziny:</strong> {
                  preferredTimes.length > 0 
                    ? preferredTimes.join(', ')
                    : 'Brak preferencji'
                }
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Step 3: Correlation Settings
export function CorrelationStep({ register, errors, watch, setValue }: StepComponentProps) {
  const blogPostsQuota = watch('blog_posts_quota') || 4
  const smPostsQuota = watch('sm_posts_quota') || 12
  const correlatePostsEnabled = watch('correlate_posts') ?? true
  
  // Default correlation values
  const smPerBlog = watch('sm_posts_per_blog') || 2
  const briefBasedPosts = watch('brief_based_sm_posts') || 0
  const standalonePosts = watch('standalone_sm_posts') || 0
  
  const handleCorrelationChange = (field: 'sm_posts_per_blog' | 'brief_based_sm_posts' | 'standalone_sm_posts', value: number) => {
    setValue(field, value)
  }
  
  const totalCalculated = (blogPostsQuota * smPerBlog) + briefBasedPosts + standalonePosts
  const isOverQuota = totalCalculated > smPostsQuota
  
  return (
    <div className="space-y-6">
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Konfiguracja korelacji treści</h3>
        <p className="text-sm text-gray-600">
          Określ jak posty na social media mają być powiązane z treściami blogowymi
        </p>
      </div>

      {/* Enable/Disable correlation */}
      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          id="correlate_posts"
          {...register('correlate_posts')}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="correlate_posts" className="text-sm font-medium text-gray-700">
          Włącz zaawansowaną korelację treści
        </label>
      </div>

      {correlatePostsEnabled && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-6"
        >
          {/* Blog-correlated posts */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
              <Link2 className="w-4 h-4" />
              Posty SM skorelowane z blogami
            </label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                {...register('sm_posts_per_blog', { valueAsNumber: true })}
                min="0"
                max="10"
                className="w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="text-sm text-gray-600">
                postów SM na każdy wpis blogowy
              </span>
              <span className="ml-auto text-sm font-medium text-gray-900">
                = {blogPostsQuota * smPerBlog} postów
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Każdy wpis blogowy będzie miał przypisane posty zapowiadające
            </p>
          </div>

          {/* Brief-based posts */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
              <FileText className="w-4 h-4" />
              Posty SM oparte na briefach
            </label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                {...register('brief_based_sm_posts', { valueAsNumber: true })}
                min="0"
                className="w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="text-sm text-gray-600">
                postów opartych na briefach
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Posty generowane na podstawie briefów (wydarzenia, aktualności)
            </p>
          </div>

          {/* Standalone posts */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
              <Settings className="w-4 h-4" />
              Niezależne posty SM
            </label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                {...register('standalone_sm_posts', { valueAsNumber: true })}
                min="0"
                className="w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="text-sm text-gray-600">
                niezależnych postów
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Posty niezwiązane z blogami (porady, pytania, behind-the-scenes)
            </p>
          </div>

          {/* Summary */}
          <div className={`p-4 rounded-lg border-2 ${
            isOverQuota ? 'border-red-300 bg-red-50' : 'border-green-300 bg-green-50'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Podsumowanie</h4>
                <div className="mt-2 space-y-1 text-sm text-gray-600">
                  <div>Posty powiązane z blogami: <strong>{blogPostsQuota * smPerBlog}</strong></div>
                  <div>Posty oparte na briefach: <strong>{briefBasedPosts}</strong></div>
                  <div>Posty niezależne: <strong>{standalonePosts}</strong></div>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-2xl font-bold ${
                  isOverQuota ? 'text-red-600' : 'text-green-600'
                }`}>
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
        </motion.div>
      )}
    </div>
  )
} 