export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            Welcome to Microservices App
          </h1>
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            A modern microservices architecture with Node.js backend, React frontend, 
            and AWS cloud deployment using CDK.
          </p>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Backend Services
              </h2>
              <ul className="text-left space-y-2 text-gray-600">
                <li>• Authentication Service (JWT)</li>
                <li>• User Management Service</li>
                <li>• API Gateway</li>
                <li>• PostgreSQL Database</li>
                <li>• RESTful APIs</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Frontend Features
              </h2>
              <ul className="text-left space-y-2 text-gray-600">
                <li>• React with TypeScript</li>
                <li>• Next.js Framework</li>
                <li>• Server-side Rendering</li>
                <li>• Responsive Design</li>
                <li>• Modern UI Components</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 space-x-4">
            <a
              href="/auth/signin"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
            >
              Sign In
            </a>
            <a
              href="/auth/signup"
              className="inline-block bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
            >
              Sign Up
            </a>
          </div>
        </div>
        
        <div className="mt-16 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
            Architecture Overview
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 font-bold text-xl">1</span>
              </div>
              <h3 className="font-semibold text-gray-800 mb-2">Frontend</h3>
              <p className="text-gray-600 text-sm">React + Next.js with TypeScript</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-green-600 font-bold text-xl">2</span>
              </div>
              <h3 className="font-semibold text-gray-800 mb-2">Microservices</h3>
              <p className="text-gray-600 text-sm">Node.js services with Express</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-600 font-bold text-xl">3</span>
              </div>
              <h3 className="font-semibold text-gray-800 mb-2">AWS Cloud</h3>
              <p className="text-gray-600 text-sm">ECS, RDS, CloudFront, CDK</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
