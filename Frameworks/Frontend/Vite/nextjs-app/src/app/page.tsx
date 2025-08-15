import { DeviceCard } from '@/components/DeviceCard'
import { ServerStatus } from '@/components/ServerStatus'
import { getDeviceData, getServerTime } from '@/lib/api'

// This is a Server Component that runs on the server
export default async function HomePage() {
  // Server-side data fetching
  const [devices, serverTime] = await Promise.all([
    getDeviceData(),
    getServerTime(),
  ])

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          IoT Device Dashboard
        </h1>
        <p className="text-gray-600 mb-4">
          Monitor and manage your connected devices with server-side rendered data
        </p>
        <ServerStatus serverTime={serverTime} />
      </div>

      {/* Statistics Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Total Devices
          </h3>
          <p className="text-3xl font-bold text-blue-600">{devices.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Active Devices
          </h3>
          <p className="text-3xl font-bold text-green-600">
            {devices.filter(device => device.status === 'online').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Offline Devices
          </h3>
          <p className="text-3xl font-bold text-red-600">
            {devices.filter(device => device.status === 'offline').length}
          </p>
        </div>
      </div>

      {/* Devices Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices.map((device) => (
          <DeviceCard key={device.id} device={device} />
        ))}
      </div>

      {/* Server Info */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          Server-Side Rendering Info
        </h3>
        <div className="text-sm text-blue-700 space-y-1">
          <p>✅ This page was rendered on the server at build time or request time</p>
          <p>✅ Data was fetched server-side for better SEO and performance</p>
          <p>✅ Server time: {serverTime}</p>
          <p>✅ Hydration will make this interactive in the browser</p>
        </div>
      </div>
    </div>
  )
}
