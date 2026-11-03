/**
 * API Client for the Alpha Convergence Engine.
 */

const API = {
  baseUrl: '',

  async getTopPicks() {
    const res = await fetch(`${this.baseUrl}/api/recommendations/top`);
    if (!res.ok) throw new Error('Failed to fetch top picks');
    return res.json();
  },

  async getAllStocks() {
    const res = await fetch(`${this.baseUrl}/api/recommendations/all`);
    if (!res.ok) throw new Error('Failed to fetch all stocks');
    return res.json();
  },

  async getStockDetail(ticker) {
    const res = await fetch(`${this.baseUrl}/api/stocks/${encodeURIComponent(ticker)}`);
    if (!res.ok) throw new Error(`Failed to fetch stock detail for ${ticker}`);
    return res.json();
  },

  async getChartData(ticker, timeframe = '1M') {
    const res = await fetch(`${this.baseUrl}/api/stocks/${encodeURIComponent(ticker)}/chart?timeframe=${encodeURIComponent(timeframe)}`);
    if (!res.ok) throw new Error(`Failed to fetch chart data for ${ticker}`);
    return res.json();
  },

  async getAIAnalysis(ticker) {
    const res = await fetch(`${this.baseUrl}/api/stocks/${encodeURIComponent(ticker)}/ai-analysis`);
    if (!res.ok) throw new Error(`Failed to fetch AI analysis for ${ticker}`);
    return res.json();
  },

  async triggerScan() {
    const res = await fetch(`${this.baseUrl}/api/scan/trigger`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to trigger scan pipeline');
    return res.json();
  },

  async addTicker(ticker, name = '', sector = '') {
    const params = new URLSearchParams({ ticker });
    if (name) params.append('name', name);
    if (sector) params.append('sector', sector);
    const res = await fetch(`${this.baseUrl}/api/tickers/add?${params.toString()}`, {
      method: 'POST'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to add ticker');
    }
    return res.json();
  }
};

window.API = API;
