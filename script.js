class CurrencyConverter {
            constructor() {
                this.apiKey = 'YOUR_API_KEY'; // Replace with actual API key
                this.baseUrl = 'https://api.exchangerate-api.com/v4/latest/';
                this.fallbackUrl = 'https://api.fxratesapi.com/latest';
                
                this.initElements();
                this.bindEvents();
                this.loadExchangeRates();
            }
            
            initElements() {
                this.amountInput = document.getElementById('amount');
                this.fromCurrency = document.getElementById('fromCurrency');
                this.toCurrency = document.getElementById('toCurrency');
                this.convertBtn = document.getElementById('convertBtn');
                this.swapBtn = document.getElementById('swapBtn');
                this.result = document.getElementById('result');
                this.loading = document.getElementById('loading');
                this.resultContent = document.getElementById('resultContent');
                this.rateInfo = document.getElementById('rateInfo');
                
                this.exchangeRates = {};
                this.lastUpdate = null;
            }
            
            bindEvents() {
                this.convertBtn.addEventListener('click', () => this.convertCurrency());
                this.swapBtn.addEventListener('click', () => this.swapCurrencies());
                
                // Auto-convert on input change
                this.amountInput.addEventListener('input', () => {
                    if (this.amountInput.value && this.exchangeRates[this.fromCurrency.value]) {
                        this.convertCurrency();
                    }
                });
                
                this.fromCurrency.addEventListener('change', () => {
                    if (this.amountInput.value) {
                        this.convertCurrency();
                    }
                });
                
                this.toCurrency.addEventListener('change', () => {
                    if (this.amountInput.value) {
                        this.convertCurrency();
                    }
                });
                
                // Enter key to convert
                this.amountInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.convertCurrency();
                    }
                });
            }
            
            async loadExchangeRates() {
                try {
                    // Try primary API first
                    let response = await fetch(`${this.baseUrl}USD`);
                    
                    if (!response.ok) {
                        // Fallback to alternative API
                        response = await fetch(`${this.fallbackUrl}?base=USD`);
                    }
                    
                    const data = await response.json();
                    this.exchangeRates['USD'] = data.rates || data;
                    this.lastUpdate = new Date();
                    
                    // Load EUR rates as well for better conversion accuracy
                    response = await fetch(`${this.baseUrl}EUR`);
                    if (response.ok) {
                        const eurData = await response.json();
                        this.exchangeRates['EUR'] = eurData.rates || eurData;
                    }
                    
                } catch (error) {
                    console.error('Error loading exchange rates:', error);
                    this.showError('Failed to load exchange rates. Using fallback rates.');
                    this.loadFallbackRates();
                }
            }
            
            loadFallbackRates() {
                // Fallback exchange rates (approximate)
                this.exchangeRates['USD'] = {
                    EUR: 0.85,
                    GBP: 0.73,
                    JPY: 110,
                    AUD: 1.35,
                    CAD: 1.25,
                    CHF: 0.92,
                    CNY: 6.45,
                    INR: 74.5,
                    TRY: 8.5,
                    USD: 1
                };
            }
            
            async convertCurrency() {
                const amount = parseFloat(this.amountInput.value);
                const from = this.fromCurrency.value;
                const to = this.toCurrency.value;
                
                if (!amount || amount <= 0) {
                    this.showError('Please enter a valid amount');
                    return;
                }
                
                if (from === to) {
                    this.showResult(amount, from, to, 1);
                    return;
                }
                
                this.showLoading();
                
                try {
                    const rate = await this.getExchangeRate(from, to);
                    const convertedAmount = amount * rate;
                    this.showResult(convertedAmount, from, to, rate);
                } catch (error) {
                    console.error('Conversion error:', error);
                    this.showError('Conversion failed. Please try again.');
                }
            }
            
            async getExchangeRate(from, to) {
                // If we don't have rates for the base currency, fetch them
                if (!this.exchangeRates[from]) {
                    try {
                        const response = await fetch(`${this.baseUrl}${from}`);
                        const data = await response.json();
                        this.exchangeRates[from] = data.rates || data;
                    } catch (error) {
                        // Use cross-rate calculation via USD
                        if (this.exchangeRates['USD']) {
                            const usdToFrom = 1 / this.exchangeRates['USD'][from];
                            const usdToTo = this.exchangeRates['USD'][to];
                            return usdToTo * usdToFrom;
                        }
                        throw error;
                    }
                }
                
                return this.exchangeRates[from][to] || (1 / this.exchangeRates[to][from]);
            }
            
            swapCurrencies() {
                const fromValue = this.fromCurrency.value;
                const toValue = this.toCurrency.value;
                
                this.fromCurrency.value = toValue;
                this.toCurrency.value = fromValue;
                
                if (this.amountInput.value) {
                    this.convertCurrency();
                }
            }
            
            showLoading() {
                this.loading.classList.add('show');
                this.resultContent.style.display = 'none';
                this.result.classList.remove('error');
            }
            
            showResult(amount, from, to, rate) {
                this.loading.classList.remove('show');
                this.resultContent.style.display = 'block';
                this.result.classList.remove('error');
                this.result.classList.add('show');
                
                const formattedAmount = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: to,
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 6
                }).format(amount);
                
                this.resultContent.innerHTML = `
                    <div class="result-amount">${formattedAmount}</div>
                    <div class="result-text">
                        1 ${from} = ${rate.toFixed(6)} ${to}
                    </div>
                `;
                
                this.rateInfo.style.display = 'block';
            }
            
            showError(message) {
                this.loading.classList.remove('show');
                this.resultContent.style.display = 'block';
                this.result.classList.add('error');
                this.resultContent.innerHTML = `<div style="color: #e74c3c; font-weight: 600;">${message}</div>`;
            }
        }
        
        // Initialize the converter when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new CurrencyConverter();
        });