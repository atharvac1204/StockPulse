import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Simple fetch function
  const fetchProducts = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/products/')
      if (!response.ok) throw new Error('Failed to fetch products')
      const data = await response.json()
      setProducts(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [])

  return (
    <div className="app">
      <header>
        <h1>StockPulse Dashboard</h1>
        <button onClick={fetchProducts} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </header>

      {error && <div className="error">Error: {error}</div>}

      <main>
        <section className="products-section">
          <h2>Products ({products.length})</h2>
          <div className="products-grid">
            {products.map(product => (
              <div key={product.id} className="product-card">
                <div className="product-header">
                  <span className={`status-badge ${product.status.toLowerCase()}`}>
                    {product.status.replace('_', ' ')}
                  </span>
                  <h3>{product.name}</h3>
                  <p className="sku">SKU: {product.sku}</p>
                </div>
                
                <div className="product-details">
                  <div className="detail-row">
                    <span>Category:</span>
                    <span>{product.category}</span>
                  </div>
                  <div className="detail-row">
                    <span>Price:</span>
                    <span>${product.current_price.toFixed(2)}</span>
                  </div>
                  <div className="detail-row">
                    <span>Stock:</span>
                    <span>{product.stock_level}</span>
                  </div>
                  <div className="detail-row">
                    <span>Reorder Threshold:</span>
                    <span>{product.reorder_threshold}</span>
                  </div>
                  <div className="detail-row">
                    <span>Demand Velocity:</span>
                    <span>{product.demand_velocity.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App