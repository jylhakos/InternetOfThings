import { NextRequest, NextResponse } from 'next/server'
import { getDeviceData } from '@/lib/api'
import { ApiResponse, Device } from '@/types'

export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<Device[]>>> {
  try {
    console.log('[API] GET /api/devices - Fetching all devices')
    
    const devices = await getDeviceData()
    
    const response: ApiResponse<Device[]> = {
      data: devices,
      success: true,
      message: 'Devices fetched successfully',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(response, { status: 200 })
  } catch (error) {
    console.error('[API] Error fetching devices:', error)
    
    const errorResponse: ApiResponse<Device[]> = {
      data: [],
      success: false,
      message: 'Failed to fetch devices',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(errorResponse, { status: 500 })
  }
}
