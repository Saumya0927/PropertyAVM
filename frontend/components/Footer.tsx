export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-bold text-lg mb-4">PropertyAVM</h3>
            <p className="text-gray-400 text-sm">
              Advanced ML-powered commercial real estate valuation platform achieving 89% accuracy
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Platform</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li><a href="/valuation" className="hover:text-white transition-colors">Valuation Tool</a></li>
              <li><a href="/dashboard" className="hover:text-white transition-colors">Dashboard</a></li>
              <li><a href="http://localhost:8000/docs" className="hover:text-white transition-colors">API Docs</a></li>
              <li><a href="http://localhost:5000" className="hover:text-white transition-colors">MLflow</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Technology</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>XGBoost + LightGBM</li>
              <li>Neural Networks</li>
              <li>FastAPI Backend</li>
              <li>AWS Lambda</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Metrics</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>89.2% Accuracy</li>
              <li>60% Faster Processing</li>
              <li>50% Deployment Reduction</li>
              <li>&lt;100ms Response Time</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2024 Property Valuation Model. Built with Next.js, FastAPI, and ML.</p>
        </div>
      </div>
    </footer>
  )
}