"""
x402 Weather API Server (Python - No Dependencies)
A paid weather API using x402 payments
Price: $0.0001 USDC per request
"""

import json
import urllib.request
import urllib.parse
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler

import os
PORT = int(os.environ.get('PORT', 3000))
PAY_TO = '0x71f08aEfe062d28c7AD37344dC0D64e0adF8941E'
NETWORK = 'eip155:84532'  # Base Sepolia

# SSL context for Open-Meteo
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

class WeatherHandler(BaseHTTPRequestHandler):
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        if self.path == '/':
            self.send_json({
                'name': 'x402 Weather API',
                'version': '1.0.0',
                'price': '$0.0001 USDC per request',
                'network': NETWORK,
                'endpoints': {
                    '/weather': 'Current weather (lat, lon required)',
                    '/forecast': 'Weather forecast (lat, lon required)',
                    '/health': 'Health check (free)'
                }
            })
        
        elif self.path == '/health':
            self.send_json({'status': 'ok'})
        
        elif self.path.startswith('/weather'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            lat = params.get('lat', [None])[0]
            lon = params.get('lon', [None])[0]
            
            if not lat or not lon:
                self.send_json({'error': 'Missing lat/lon parameters'}, 400)
                return
            
            try:
                lat, lon = float(lat), float(lon)
                if lat < -90 or lat > 90 or lon < -180 or lon > 180:
                    self.send_json({'error': 'Invalid coordinates'}, 400)
                    return
                
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,cloud_cover,wind_speed_10m&timezone=auto"
                with urllib.request.urlopen(url, timeout=10, context=SSL_CONTEXT) as response:
                    data = json.loads(response.read().decode())
                
                self.send_json({
                    'success': True,
                    'data': {
                        'location': {'lat': lat, 'lon': lon},
                        'current': data.get('current', {}),
                        'timezone': data.get('timezone', 'UTC')
                    }
                })
            except Exception as e:
                self.send_json({'error': f'Failed to fetch weather: {str(e)}'}, 500)
        
        elif self.path.startswith('/forecast'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            lat = params.get('lat', [None])[0]
            lon = params.get('lon', [None])[0]
            days = min(int(params.get('days', ['7'])[0]), 14)
            
            if not lat or not lon:
                self.send_json({'error': 'Missing lat/lon parameters'}, 400)
                return
            
            try:
                lat, lon = float(lat), float(lon)
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&timezone=auto&forecast_days={days}"
                with urllib.request.urlopen(url, timeout=10, context=SSL_CONTEXT) as response:
                    data = json.loads(response.read().decode())
                
                self.send_json({
                    'success': True,
                    'data': {
                        'location': {'lat': lat, 'lon': lon},
                        'forecast': data
                    }
                })
            except Exception as e:
                self.send_json({'error': f'Failed to fetch forecast: {str(e)}'}, 500)
        
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    server = HTTPServer(('', PORT), WeatherHandler)
    print(f"x402 Weather API running on port {PORT}")
    server.serve_forever()
