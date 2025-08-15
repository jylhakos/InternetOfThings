import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Next.js IoT Application',
  description: 'A modern IoT application built with Next.js, React, and TypeScript featuring server-side rendering',
  keywords: ['Next.js', 'React', 'TypeScript', 'IoT', 'Server-Side Rendering'],
  authors: [{ name: 'IoT Development Team' }],
  creator: 'IoT Development Team',
  publisher: 'IoT Solutions',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://your-domain.com',
    title: 'Next.js IoT Application',
    description: 'A modern IoT application with server-side rendering',
    siteName: 'IoT Solutions',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Next.js IoT Application',
    description: 'A modern IoT application with server-side rendering',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold text-gray-900">
                    IoT Dashboard
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">
                    Next.js with SSR
                  </span>
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            {children}
          </main>
          <footer className="bg-white border-t mt-12">
            <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
              <p className="text-center text-sm text-gray-500">
                © 2025 IoT Solutions. Built with Next.js and React.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
