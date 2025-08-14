import { NextRequest, NextResponse } from 'next/server'
import { getDeviceById } from '@/lib/api'
import { ApiResponse, Device } from '@/types'

interface Params {
  params: {
    id: string
  }
}

export async function GET(
  request: NextRequest, 
  { params }: Params
): Promise<NextResponse<ApiResponse<Device | null>>> {
  try {
    console.log(`[API] GET /api/devices/${params.id} - Fetching device`)
    
    const device = await getDeviceById(params.id)
    
    if (!device) {
      const notFoundResponse: ApiResponse<null> = {
        data: null,
        success: false,
        message: 'Device not found',
        timestamp: new Date().toISOString(),
      }
      return NextResponse.json(notFoundResponse, { status: 404 })
    }
    
    const response: ApiResponse<Device> = {
      data: device,
      success: true,
      message: 'Device fetched successfully',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(response, { status: 200 })
  } catch (error) {
    console.error(`[API] Error fetching device ${params.id}:`, error)
    
    const errorResponse: ApiResponse<null> = {
      data: null,
      success: false,
      message: 'Failed to fetch device',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(errorResponse, { status: 500 })
  }
}

export async function PUT(
  request: NextRequest,
  { params }: Params
): Promise<NextResponse<ApiResponse<Device | null>>> {
  try {
    console.log(`[API] PUT /api/devices/${params.id} - Updating device`)
    
    const body = await request.json()
    const device = await getDeviceById(params.id)
    
    if (!device) {
      const notFoundResponse: ApiResponse<null> = {
        data: null,
        success: false,
        message: 'Device not found',
        timestamp: new Date().toISOString(),
      }
      return NextResponse.json(notFoundResponse, { status: 404 })
    }
    
    // In a real application, you would update the device in the database
    const updatedDevice: Device = { ...device, ...body }
    
    const response: ApiResponse<Device> = {
      data: updatedDevice,
      success: true,
      message: 'Device updated successfully',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(response, { status: 200 })
  } catch (error) {
    console.error(`[API] Error updating device ${params.id}:`, error)
    
    const errorResponse: ApiResponse<null> = {
      data: null,
      success: false,
      message: 'Failed to update device',
      timestamp: new Date().toISOString(),
    }
    
    return NextResponse.json(errorResponse, { status: 500 })
  }
}
