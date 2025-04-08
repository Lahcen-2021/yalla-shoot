from django.shortcuts import render
from .services import FootballAPIService
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from .models import HistoricalMatch

# Create your views here.

def home(request):
    # Create cache key based on date and status filter
    date_filter = request.GET.get('date', 'today')
    status_filter = request.GET.get('status', 'all')
    cache_key = f'matches_{date_filter}_{status_filter}'
    
    # Try to get cached data
    cached_data = cache.get(cache_key)
    if cached_data:
        print("Returning cached data")
        return render(request, 'matches/matche.html', cached_data)

    api_service = FootballAPIService()
    
    # تحديد التاريخ
    date_filter = request.GET.get('date', 'today')
    today = datetime.now().date()
    
    if date_filter == 'yesterday':
        selected_date = today - timedelta(days=1)
    elif date_filter == 'tomorrow':
        selected_date = today + timedelta(days=1)
    else:
        selected_date = today
    
    print(f"Current date filter: {date_filter}")
    print(f"Selected date: {selected_date}")
    
    matches_data = api_service.get_matches_by_date(selected_date)
    matches = matches_data.get('response', [])
    
    # تحديث قائمة الدوريات (remove unwanted leagues)
    LEAGUES_TRANSLATION = {
        39: 'الدوري الإنجليزي',    # Premier League
        2: 'دوري أبطال أوروبا',    # Champions League
        140: 'الدوري الإسباني',    # La Liga
        135: 'الدوري الإيطالي',    # Serie A
        61: 'الدوري الفرنسي',      # Ligue 1
        307: 'الدوري السعودي'      # Saudi Pro League
    }
    
    # تحديث قاموس القنوات حسب الدوري (remove corresponding channels)
    # Update the CHANNEL_MAPPING dictionary
    CHANNEL_MAPPING = {
        39: 'beIN SPORTS 1 HD',    # Premier League
        2: ['beIN SPORTS 1 HD', 'beIN SPORTS 2 HD'],    # Champions League
        140: 'beIN SPORTS 3 HD',    # La Liga
        135: 'beIN SPORTS 4 HD',    # Serie A
        61: 'beIN SPORTS 6 HD',      # Ligue 1
        307: 'SSC SPORT 1'      # Saudi Pro League
    }
    
    # Update the channel assignment logic
    filtered_matches = []
    for match in matches:
        league_id = match['league']['id']
        if league_id in LEAGUES_TRANSLATION:
            # تحويل حالة المباراة
            status = match['fixture']['status']
            if status['long'] == 'Match Finished':
                status['short'] = 'FT'
                status['long'] = 'انتهت'
            elif status['long'] == 'Match Finished After Extra Time':
                status['short'] = 'AET'
                status['long'] = 'انتهت بعد الوقت الإضافي'
            elif status['long'] == 'Match Finished After Penalties':
                status['short'] = 'PEN'
                status['long'] = 'انتهت بركلات الترجيح'

            # إضافة اسم الدوري بالعربية
            match['league']['arabic_name'] = LEAGUES_TRANSLATION[league_id]
            
            # إضافة القناة
            # Update channel assignment to handle multiple channels
            channels = CHANNEL_MAPPING.get(league_id, 'beIN SPORTS HD')
            match['channel'] = channels[0] if isinstance(channels, list) else channels
            
            filtered_matches.append(match)
            
    # طباعة النتائج النهائية
    for match in filtered_matches[:3]:
        print(f"\nFinal Match Status:")
        print(f"Status Short: {match['fixture']['status']['short']}")
        print(f"Status Long: {match['fixture']['status'].get('long')}")
        print("---")
    
    # الحصول على فلتر الحالة
    status_filter = request.GET.get('status', 'all')
    
    # طباعة عدد المباريات بعد الفلترة
    print("Filtered matches:", len(filtered_matches))
    
    # فلترة المباريات حسب الحالة
    if status_filter != 'all':
        status_matches = []
        for match in filtered_matches:
            if status_filter == 'live' and match['fixture']['status']['short'] in ['1H', '2H', 'HT', 'ET', 'P', 'BT']:
                status_matches.append(match)
            elif status_filter == 'not_started' and match['fixture']['status']['short'] == 'NS':
                status_matches.append(match)
            elif status_filter == 'finished' and match['fixture']['status']['short'] in ['FT', 'AET', 'PEN']:
                status_matches.append(match)
        filtered_matches = status_matches

    # تصنيف وترتيب المباريات حسب الحالة
    live_matches = []
    upcoming_matches = []
    finished_matches = []

    for match in filtered_matches:
        status = match['fixture']['status']['short']
        print(f"Processing match with status: {status}")  # للتحقق من الحالة
        
        # المباريات الجارية
        if status in ['1H', '2H', 'HT', 'ET', 'P', 'BT']:
            live_matches.append(match)
        # المباريات التي لم تبدأ
        elif status in ['NS', 'TBD', 'PST']:
            upcoming_matches.append(match)
        # المباريات المنتهية
        elif status in ['FT', 'AET', 'PEN']:  # تأكد من أن هذه الحالات موجودة
            finished_matches.append(match)
        else:
            print(f"Unknown match status: {status}")  # طباعة الحالات غير المعروفة
            
    # طباعة معلومات التصحيح
    for match in filtered_matches[:3]:
        print(f"Match details for debugging:")
        print(f"- Status Short: {match['fixture']['status']['short']}")
        print(f"- Status Long: {match['fixture']['status'].get('long')}")
        print(f"- Is FT?: {match['fixture']['status']['short'] == 'FT'}")
        print(f"- In FT,AET,PEN?: {match['fixture']['status']['short'] in ['FT', 'AET', 'PEN']}")
        print("---")

    # ترتيب المباريات التي لم تبدأ حسب وقت البداية
    upcoming_matches.sort(key=lambda x: x['fixture']['timestamp'])
    
    for match in upcoming_matches:
        match_time = datetime.fromtimestamp(match['fixture']['timestamp']).strftime('%H:%M')
        print(f"{match['teams']['home']['name']} vs {match['teams']['away']['name']} - {match_time}")

    # دمج القوائم بالترتيب المطلوب
    sorted_matches = live_matches + upcoming_matches + finished_matches

    # Add formatted time to each match
    for match in sorted_matches:
        match['formatted_time'] = datetime.fromtimestamp(match['fixture']['timestamp']).strftime('%H:%M')

    # After processing matches, save to historical database
    for match in sorted_matches:
        HistoricalMatch.objects.update_or_create(
            match_id=match['fixture']['id'],
            defaults={
                'league_id': match['league']['id'],
                'home_team': match['teams']['home']['name'],
                'away_team': match['teams']['away']['name'],
                'home_score': match['goals']['home'],
                'away_score': match['goals']['away'],
                'match_date': datetime.fromtimestamp(match['fixture']['timestamp']),
                'status': match['fixture']['status']['short'],
                'channel': match['channel']
            }
        )

    context = {
        'matches': sorted_matches,
        'current_status': status_filter,
        'current_date': date_filter,
        'matches_count': len(sorted_matches),
        'date': selected_date.strftime('%Y-%m-%d'),
        'live_count': len(live_matches),
        'upcoming_count': len(upcoming_matches),
        'finished_count': len(finished_matches),
        'match_times': [match['fixture']['timestamp'] for match in sorted_matches]
    }

    # Cache the data for 5 minutes (300 seconds)
    # Before saving to cache
    print("ℹ️ Saving data to cache with key:", cache_key)
    cache.set(cache_key, context, 300)
    
    return render(request, 'matches/matche.html', context)


def match_details(request, match_id):
    api_service = FootballAPIService()
    
    # Try to get match from historical database first
    try:
        historical_match = HistoricalMatch.objects.get(match_id=match_id)
        # Get fresh data from API
        match_data = api_service.get_match_details(match_id)
        match = match_data.get('response', [{}])[0] if match_data.get('response') else {}
        
        if match:
            # Add channel information from historical data
            match['channel'] = historical_match.channel
            
            # Format the match data
            league_id = match['league']['id']
            LEAGUES_TRANSLATION = {
                39: 'الدوري الإنجليزي',
                2: 'دوري أبطال أوروبا',
                140: 'الدوري الإسباني',
                135: 'الدوري الإيطالي',
                61: 'الدوري الفرنسي',
                307: 'الدوري السعودي'
            }
            
            # Add Arabic league name
            match['league']['arabic_name'] = LEAGUES_TRANSLATION.get(league_id, match['league']['name'])
            
            # Format match time
            match_timestamp = match['fixture']['timestamp']
            match_datetime = datetime.fromtimestamp(match_timestamp)
            match['date'] = match_datetime.strftime('%Y-%m-%d')
            match['time'] = match_datetime.strftime('%H:%M')
            match['timezone'] = 'توقيت مكة المكرمة'
            
            context = {
                'match': match,
                'matches': [match],  # For compatibility with existing template
            }
            
            return render(request, 'matches/match_details.html', context)
            
    except HistoricalMatch.DoesNotExist:
        # Handle case where match is not found
        return render(request, 'matches/match_details.html', {
            'error': 'المباراة غير موجودة'
        })
