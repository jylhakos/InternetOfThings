import { NextRequest, NextResponse } from 'next/server'
import { ServerInfo, ApiResponse } from '@/types'

export async function GET(): Promise<NextResponse<ApiResponse<ServerInfo>>> {
  try {
    console.log('[API] GET /api/server-info - Fetching server information')
    
    const serverInfo: ServerInfo = {
      serverTime: new Date().toISOString(),
      nodeVersion: process.version,
      platform: process.platform,
      uptime: process.uptime(),
    }
    
    const response: ApiResponse<ServerInfo> = {
      data: serverInfo,
      success: true,
      message: 'Server information fetched successfully',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(response, { status: 200 })
  } catch (error) {
    console.error('[API] Error fetching server info:', error)
    
    const errorResponse: ApiResponse<ServerInfo> = {
      data: {
        serverTime: new Date().toISOString(),
        nodeVersion: 'unknown',
        platform: 'unknown',
        uptime: 0,
      },
      success: false,
      message: 'Failed to fetch server information',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(errorResponse, { status: 500 })
  }
}
