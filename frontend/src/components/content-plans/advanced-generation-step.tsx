'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Search, Sparkles, TrendingUp, FileSearch, Globe, Zap, BookOpen } from 'lucide-react'
import { UseFormRegister, FieldErrors, UseFormWatch, UseFormSetValue } from 'react-hook-form'

export interface AdvancedGenerationStepProps {
  register: UseFormRegister<any>
  errors: FieldErrors<any>
  watch: UseFormWatch<any>
  setValue: UseFormSetValue<any>
}

export function AdvancedGenerationStep({ register, errors, watch, setValue }: AdvancedGenerationStepProps) {
  const generationMethod = watch('generation_method') || 'standard'
  const useDeepResearch = watch('use_deep_research') ?? true
  const researchDepth = watch('research_depth') || 'deep'

  const handleGenerationMethodChange = (method: string) => {
    setValue('generation_method', method)
    // Set default values based on method
    if (method === 'deep_reasoning') {
      setValue('use_deep_research', true)
      setValue('research_depth', 'deep')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Metoda Generowania Treści</h3>
        <p className="text-gray-600 mb-6">
          Wybierz metodę generowania treści. Nowy system Deep Reasoning wykorzystuje zaawansowaną analizę 
          i zewnętrzne źródła dla lepszych rezultatów.
        </p>
      </div>

      {/* Generation Method Selection */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Standard Generation */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`relative cursor-pointer rounded-lg border-2 p-6 transition-all ${
            generationMethod === 'standard'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
          onClick={() => handleGenerationMethodChange('standard')}
        >
          <div className="flex items-center mb-4">
            <input
              type="radio"
              value="standard"
              checked={generationMethod === 'standard'}
              onChange={() => handleGenerationMethodChange('standard')}
              className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <label className="ml-3 block text-sm font-medium text-gray-700">
              Generowanie Standardowe
            </label>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <Zap className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-900">Szybkie generowanie</span>
            </div>
            
            <p className="text-sm text-gray-600">
              Klasyczna metoda generowania treści oparta na strategii komunikacji i briefach.
            </p>
            
            <div className="space-y-2 pt-2">
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Szybkie rezultaty (30-60 sekund)</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Podstawowa analiza briefów</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Sprawdzone podejście</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Deep Reasoning Generation */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`relative cursor-pointer rounded-lg border-2 p-6 transition-all ${
            generationMethod === 'deep_reasoning'
              ? 'border-purple-500 bg-purple-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
          onClick={() => handleGenerationMethodChange('deep_reasoning')}
        >
          <div className="absolute top-2 right-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r from-purple-500 to-pink-500 text-white">
              <Sparkles className="w-3 h-3 mr-1" />
              Nowe
            </span>
          </div>
          
          <div className="flex items-center mb-4">
            <input
              type="radio"
              value="deep_reasoning"
              checked={generationMethod === 'deep_reasoning'}
              onChange={() => handleGenerationMethodChange('deep_reasoning')}
              className="h-4 w-4 text-purple-600 border-gray-300 focus:ring-purple-500"
            />
            <label className="ml-3 block text-sm font-medium text-gray-700">
              Deep Reasoning AI
            </label>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <Brain className="h-5 w-5 text-purple-500 mr-2" />
              <span className="text-sm font-medium text-gray-900">Zaawansowana analiza</span>
            </div>
            
            <p className="text-sm text-gray-600">
              Wieloetapowe rozumowanie z wykorzystaniem zewnętrznych źródeł i analizy branżowej.
            </p>
            
            <div className="space-y-2 pt-2">
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Głęboka analiza briefów i priorytetów</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Research trendów i konkurencji</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Scoring jakości i różnorodności</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Automatyczna analiza branży</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Deep Reasoning Options */}
      {generationMethod === 'deep_reasoning' && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-4 mt-6 p-6 bg-purple-50 border border-purple-200 rounded-lg"
        >
          <h4 className="text-lg font-medium text-purple-900 mb-4">Opcje Deep Reasoning</h4>
          
          {/* Use Deep Research */}
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                {...register('use_deep_research')}
                id="use_deep_research"
                type="checkbox"
                className="focus:ring-purple-500 h-4 w-4 text-purple-600 border-gray-300 rounded"
              />
            </div>
            <div className="ml-3">
              <label htmlFor="use_deep_research" className="font-medium text-gray-700">
                Włącz głęboki research
              </label>
              <p className="text-sm text-gray-500 mt-1">
                Wykorzystaj Tavily API do analizy trendów, konkurencji i aktualnych wydarzeń w branży.
              </p>
            </div>
          </div>

          {/* Research Depth */}
          {useDeepResearch && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Głębokość researchu
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setValue('research_depth', 'basic')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    researchDepth === 'basic'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-purple-700 border border-purple-300 hover:bg-purple-50'
                  }`}
                >
                  <Search className="w-4 h-4 inline mr-1" />
                  Podstawowy
                </button>
                <button
                  type="button"
                  onClick={() => setValue('research_depth', 'deep')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    researchDepth === 'deep'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-purple-700 border border-purple-300 hover:bg-purple-50'
                  }`}
                >
                  <FileSearch className="w-4 h-4 inline mr-1" />
                  Głęboki
                </button>
                <button
                  type="button"
                  onClick={() => setValue('research_depth', 'comprehensive')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    researchDepth === 'comprehensive'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-purple-700 border border-purple-300 hover:bg-purple-50'
                  }`}
                >
                  <Globe className="w-4 h-4 inline mr-1" />
                  Kompleksowy
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {researchDepth === 'basic' && 'Szybki przegląd głównych trendów (1-2 minuty)'}
                {researchDepth === 'deep' && 'Analiza trendów i konkurencji (2-3 minuty)'}
                {researchDepth === 'comprehensive' && 'Pełna analiza z insights branżowymi (3-5 minut)'}
              </p>
            </div>
          )}

          {/* Additional Options */}
          <div className="mt-4 space-y-3">
            <div className="flex items-center">
              <input
                {...register('analyze_competitors')}
                id="analyze_competitors"
                type="checkbox"
                className="focus:ring-purple-500 h-4 w-4 text-purple-600 border-gray-300 rounded"
              />
              <label htmlFor="analyze_competitors" className="ml-2 text-sm text-gray-700">
                Analizuj strategie konkurencji
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                {...register('include_trends')}
                id="include_trends"
                type="checkbox"
                className="focus:ring-purple-500 h-4 w-4 text-purple-600 border-gray-300 rounded"
              />
              <label htmlFor="include_trends" className="ml-2 text-sm text-gray-700">
                Uwzględnij aktualne trendy branżowe
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                {...register('optimize_seo')}
                id="optimize_seo"
                type="checkbox"
                className="focus:ring-purple-500 h-4 w-4 text-purple-600 border-gray-300 rounded"
              />
              <label htmlFor="optimize_seo" className="ml-2 text-sm text-gray-700">
                Optymalizuj tematy pod kątem SEO
              </label>
            </div>
          </div>
        </motion.div>
      )}

      {/* Benefits Comparison */}
      <div className="mt-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-gray-200">
        <h4 className="text-lg font-medium text-gray-900 mb-4">
          <TrendingUp className="w-5 h-5 inline mr-2" />
          Porównanie metod
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="font-medium text-gray-700 mb-2">Generowanie Standardowe</h5>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Czas generowania: 30-60 sekund</li>
              <li>• Bazuje na strategii i briefach</li>
              <li>• Sprawdzone, stabilne rezultaty</li>
              <li>• Odpowiednie dla rutynowych planów</li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-medium text-purple-700 mb-2">Deep Reasoning AI</h5>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Czas generowania: 2-5 minut</li>
              <li>• Analiza wieloźródłowa</li>
              <li>• Unikalne, kreatywne tematy</li>
              <li>• Idealne dla kampanii strategicznych</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-white/70 rounded-md">
          <p className="text-sm text-gray-700">
            <BookOpen className="w-4 h-4 inline mr-1" />
            <strong>Rekomendacja:</strong> Użyj Deep Reasoning dla ważnych kampanii i gdy potrzebujesz 
            wysokiej jakości, zróżnicowanych treści. Standardowa metoda jest wystarczająca dla 
            regularnych planów treści.
          </p>
        </div>
      </div>
    </div>
  )
}