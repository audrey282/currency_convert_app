import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import time

class CurrencyConverter:
    """
    A comprehensive currency converter using multiple APIs for reliability
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_urls = {
            'exchangerate_api': 'https://v6.exchangerate-api.com/v6',
            'fixer': 'http://data.fixer.io/api',
            'free_api': 'https://api.exchangerate-api.com/v4/latest',
            'fxrates': 'https://api.fxratesapi.com/latest'
        }
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
        # Common currency codes and names
        self.currencies = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound Sterling',
            'JPY': 'Japanese Yen',
            'AUD': 'Australian Dollar',
            'CAD': 'Canadian Dollar',
            'CHF': 'Swiss Franc',
            'CNY': 'Chinese Yuan',
            'SEK': 'Swedish Krona',
            'NZD': 'New Zealand Dollar',
            'MXN': 'Mexican Peso',
            'SGD': 'Singapore Dollar',
            'HKD': 'Hong Kong Dollar',
            'NOK': 'Norwegian Krone',
            'INR': 'Indian Rupee',
            'TRY': 'Turkish Lira',
            'RUB': 'Russian Ruble',
            'KRW': 'South Korean Won',
            'BRL': 'Brazilian Real',
            'ZAR': 'South African Rand'
        }
    
    def _is_cache_valid(self, currency: str) -> bool:
        """Check if cached data is still valid"""
        if currency not in self.cache:
            return False
        
        cache_time = self.cache[currency]['timestamp']
        return datetime.now() - cache_time < self.cache_duration
    
    def _fetch_from_api(self, base_currency: str, api_name: str) -> Optional[Dict]:
        """Fetch exchange rates from a specific API"""
        try:
            if api_name == 'exchangerate_api' and self.api_key:
                url = f"{self.base_urls[api_name]}/{self.api_key}/latest/{base_currency}"
            elif api_name == 'fixer' and self.api_key:
                url = f"{self.base_urls[api_name]}/latest?access_key={self.api_key}&base={base_currency}"
            elif api_name == 'free_api':
                url = f"{self.base_urls[api_name]}/{base_currency}"
            elif api_name == 'fxrates':
                url = f"{self.base_urls[api_name]}?base={base_currency}"
            else:
                return None
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Normalize the response format
            if 'conversion_rates' in data:
                return data['conversion_rates']
            elif 'rates' in data:
                return data['rates']
            else:
                return None
                
        except requests.RequestException as e:
            print(f"Error fetching from {api_name}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {api_name}: {e}")
            return None
    
    def get_exchange_rates(self, base_currency: str = 'USD') -> Dict[str, float]:
        """
        Get exchange rates for a base currency
        Uses caching and multiple APIs for reliability
        """
        base_currency = base_currency.upper()
        
        # Check cache first
        if self._is_cache_valid(base_currency):
            return self.cache[base_currency]['rates']
        
        # Try multiple APIs in order of preference
        apis_to_try = ['free_api', 'fxrates', 'exchangerate_api', 'fixer']
        
        for api_name in apis_to_try:
            rates = self._fetch_from_api(base_currency, api_name)
            if rates:
                # Cache the results
                self.cache[base_currency] = {
                    'rates': rates,
                    'timestamp': datetime.now(),
                    'source': api_name
                }
                return rates
            
            # Small delay between API calls to be respectful
            time.sleep(0.5)
        
        raise Exception("Unable to fetch exchange rates from any API")
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Tuple[float, Dict]:
        """
        Convert amount from one currency to another
        Returns (converted_amount, conversion_info)
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency == to_currency:
            return amount, {
                'rate': 1.0,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'original_amount': amount,
                'converted_amount': amount,
                'timestamp': datetime.now().isoformat()
            }
        
        # Get exchange rates
        try:
            rates = self.get_exchange_rates(from_currency)
        except Exception:
            # Try with USD as base if direct conversion fails
            if from_currency != 'USD':
                usd_rates = self.get_exchange_rates('USD')
                if from_currency in usd_rates and to_currency in usd_rates:
                    # Convert via USD: from -> USD -> to
                    usd_amount = amount / usd_rates[from_currency]
                    converted_amount = usd_amount * usd_rates[to_currency]
                    rate = usd_rates[to_currency] / usd_rates[from_currency]
                else:
                    raise Exception(f"Unable to convert from {from_currency} to {to_currency}")
            else:
                raise
        else:
            if to_currency not in rates:
                raise Exception(f"Currency {to_currency} not supported")
            
            rate = rates[to_currency]
            converted_amount = amount * rate
        
        conversion_info = {
            'rate': rate,
            'from_currency': from_currency,
            'to_currency': to_currency,
            'original_amount': amount,
            'converted_amount': converted_amount,
            'timestamp': datetime.now().isoformat(),
            'source': self.cache.get(from_currency, {}).get('source', 'unknown')
        }
        
        return converted_amount, conversion_info
    
    def get_currency_list(self) -> Dict[str, str]:
        """Get list of supported currencies"""
        return self.currencies.copy()
    
    def format_currency(self, amount: float, currency: str) -> str:
        """Format amount with currency symbol"""
        currency = currency.upper()
        
        # Simple formatting - in production, use locale-specific formatting
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'INR': '₹',
            'TRY': '₺',
            'RUB': '₽'
        }
        
        symbol = currency_symbols.get(currency, currency + ' ')
        if currency == 'JPY':
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.2f}"

def main():
    """Example usage of the CurrencyConverter"""
    
    # Initialize converter (optionally with API key)
    converter = CurrencyConverter()
    
    print("=== Currency Converter Demo ===\n")
    
    # Example 1: Basic conversion
    print("1. Basic Conversion:")
    try:
        amount = 100
        from_curr = 'USD'
        to_curr = 'EUR'
        
        converted_amount, info = converter.convert(amount, from_curr, to_curr)
        
        print(f"   {converter.format_currency(amount, from_curr)} = "
              f"{converter.format_currency(converted_amount, to_curr)}")
        print(f"   Exchange rate: 1 {from_curr} = {info['rate']:.6f} {to_curr}")
        print(f"   Source: {info['source']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Example 2: Multiple conversions
    print("2. Multiple Conversions:")
    conversions = [
        (50, 'GBP', 'USD'),
        (1000, 'JPY', 'EUR'),
        (25, 'CAD', 'AUD'),
        (75, 'EUR', 'TRY')
    ]
    
    for amount, from_curr, to_curr in conversions:
        try:
            converted_amount, info = converter.convert(amount, from_curr, to_curr)
            print(f"   {converter.format_currency(amount, from_curr)} → "
                  f"{converter.format_currency(converted_amount, to_curr)}")
        except Exception as e:
            print(f"   {from_curr} to {to_curr}: Error - {e}")
    
    print()
    
    # Example 3: Show supported currencies
    print("3. Supported Currencies:")
    currencies = converter.get_currency_list()
    for code, name in list(currencies.items())[:10]:  # Show first 10
        print(f"   {code}: {name}")
    print(f"   ... and {len(currencies) - 10} more")
    
    print()
    
    # Example 4: Interactive mode
    print("4. Interactive Mode (type 'quit' to exit):")
    while True:
        try:
            print("\nEnter conversion details:")
            amount_input = input("Amount: ").strip()
            if amount_input.lower() == 'quit':
                break
                
            from_input = input("From currency (e.g., USD): ").strip().upper()
            if from_input.lower() == 'quit':
                break
                
            to_input = input("To currency (e.g., EUR): ").strip().upper()
            if to_input.lower() == 'quit':
                break
            
            amount = float(amount_input)
            converted_amount, info = converter.convert(amount, from_input, to_input)
            
            print(f"\nResult:")
            print(f"  {converter.format_currency(amount, from_input)} = "
                  f"{converter.format_currency(converted_amount, to_input)}")
            print(f"  Rate: 1 {from_input} = {info['rate']:.6f} {to_input}")
            print(f"  Last updated: {info['timestamp']}")
            
        except ValueError:
            print("Please enter a valid number for amount")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()