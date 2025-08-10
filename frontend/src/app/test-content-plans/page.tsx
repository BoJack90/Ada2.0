'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export default function TestContentPlansPage() {
  console.log('TestContentPlansPage loaded')
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['test-content-plans'],
    queryFn: async () => {
      console.log('Fetching content plans via api.contentPlans.list...')
      try {
        const result = await api.contentPlans.list(1)
        console.log('Success:', result)
        return result
      } catch (err) {
        console.error('Error:', err)
        throw err
      }
    }
  })

  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Content Plans</h1>
      {isLoading && <p>Loading...</p>}
      {error && <p>Error: {String(error)}</p>}
      {data && (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  )
}