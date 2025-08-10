import './globals.css'
import '../styles/layout.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ReactQueryProvider } from '@/components/providers/react-query-provider'
import { LayoutWrapper } from '@/components/layout/layout-wrapper'
import { ToastProvider } from '@/components/providers/toast-provider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Ada 2.0',
  description: 'Nowoczesna aplikacja z FastAPI i Next.js',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pl">
      <body className={inter.className}>
        <ReactQueryProvider>
          <ToastProvider />
          <LayoutWrapper>
            {children}
          </LayoutWrapper>
        </ReactQueryProvider>
      </body>
    </html>
  )
}
