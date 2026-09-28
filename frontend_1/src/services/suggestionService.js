import apiClient from './apiClient'

class SuggestionService {
  async getPricingSuggestions(status = null) {
    const url = status ? `/suggestions/pricing?status=${status}` : '/suggestions/pricing'
    return apiClient.get(url)
  }

  async getReorderSuggestions(status = null) {
    const url = status ? `/suggestions/reorder?status=${status}` : '/suggestions/reorder'
    return apiClient.get(url)
  }

  async acceptPricingSuggestion(suggestionId) {
    return apiClient.patch(`/suggestions/pricing/${suggestionId}`, { status: 'ACCEPTED' })
  }

  async rejectPricingSuggestion(suggestionId) {
    return apiClient.patch(`/suggestions/pricing/${suggestionId}`, { status: 'REJECTED' })
  }

  async acceptReorderSuggestion(suggestionId) {
    return apiClient.patch(`/suggestions/reorder/${suggestionId}`, { status: 'ACCEPTED' })
  }

  async rejectReorderSuggestion(suggestionId) {
    return apiClient.patch(`/suggestions/reorder/${suggestionId}`, { status: 'REJECTED' })
  }
}

export default new SuggestionService()