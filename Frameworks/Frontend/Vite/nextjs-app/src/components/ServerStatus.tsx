'use client'

import { format } from 'date-fns'

interface ServerStatusProps {
  serverTime: string
}

export function ServerStatus({ serverTime }: ServerStatusProps) {
  const formattedTime = format(new Date(serverTime), 'PPpp')
  
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className="h-3 w-3 bg-green-400 rounded-full animate-pulse"></div>
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-green-800">
            Server is running
          </p>
          <p className="text-sm text-green-600">
            Last updated: {formattedTime}
          </p>
        </div>
      </div>
    </div>
  )
}
