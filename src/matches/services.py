import requests
import os
from datetime import datetime, timedelta
from django.conf import settings

class FootballAPIService:
    def __init__(self):
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-apisports-key': settings.RAPID_API_KEY
        }

    def get_live_matches(self):
        endpoint = f"{self.base_url}/fixtures"
        params = {
            'live': 'all'
        }
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()

    def get_matches_by_date(self, date):
        try:
            url = f"{self.base_url}/fixtures"
            params = {
                'date': date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                
                # تحويل حالات المباريات
                for match in matches:
                    status = match['fixture']['status']
                    print(f"Original status from API: {status}")
                    
                    # تحويل الحالات المعروفة
                    if status.get('long') == 'Match Finished':
                        status['short'] = 'FT'
                    elif status.get('long') == 'Match Finished After Extra Time':
                        status['short'] = 'AET'
                    elif status.get('long') == 'Match Finished After Penalties':
                        status['short'] = 'PEN'
                    
                    print(f"Transformed status: {status['short']}")
                
                return {'response': matches}
                
            return {'response': []}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {'response': []}

    def _transform_status(self, status):
        status_mapping = {
            'SCHEDULED': 'NS',
            'LIVE': '1H',
            'IN_PLAY': '1H',
            'PAUSED': 'HT',
            'FINISHED': 'FT',
            'POSTPONED': 'PST',
            'SUSPENDED': 'SUSP',
            'CANCELLED': 'CANC',
            'FULL_TIME': 'FT',
            'AFTER_ET': 'AET',
            'AFTER_PEN': 'PEN'
        }
        return status_mapping.get(status, status)

    def get_match_events(self, match_id):
        try:
            url = f"{self.base_url}/matches/{match_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return {'response': response.json()}
        except Exception as e:
            print(f"Error fetching match events: {str(e)}")
            return {'response': []}

    def get_match_details(self, match_id):
        """Fetch details for a specific match by ID"""
        url = f"{self.base_url}/fixtures"
        
        params = {
            'id': match_id,
            'timezone': 'Asia/Riyadh'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching match details: {e}")
            return {'response': []}