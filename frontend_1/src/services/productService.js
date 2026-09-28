import apiClient from './apiClient'

class ProductService {
  async getProducts() {
    return apiClient.get('/products/')
  }

  async placeOrder(productId, orderData) {
    return apiClient.post(`/products/${productId}/orders`, orderData)
  }

  async updateStock(productId, stockData) {
    return apiClient.patch(`/products/${productId}/stock`, stockData)
  }

  async updateDemand(productId, demandData) {
    // Note: This would require a backend endpoint to update demand velocity
    // For now, we'll simulate this by updating the product directly
    // In a real implementation, this would be a separate endpoint
    throw new Error('Not implemented - backend endpoint needed')
  }

  async getPricingRecommendation(productId) {
    return apiClient.get(`/products/${productId}/pricing`)
  }

  async getReorderRecommendation(productId) {
    return apiClient.get(`/products/${productId}/reorder`)
  }
}

export default new ProductService()