from django import template

register = template.Library()

CHANNEL_URLS = {
    'beIN SPORTS 1 HD': 'https://d.alkoora.live/albaplayer/on-time-sport-1/?serv=1',
    'beIN SPORTS 2 HD': 'https://d.alkoora.live/albaplayer/on-time-sport-2/?serv=1',
    'beIN SPORTS 3 HD': 'https://d.alkoora.live/albaplayer/on-time-sport-3/?serv=1',
    'beIN SPORTS 4 HD': 'https://4.buz-sport.site/albaplayer/bein5/?serv=0'
}

@register.filter
def get_channel_url(channel_name):
    if not channel_name:
        return None
    
    # Create a case-insensitive mapping
    channel_map = {k.lower(): v for k, v in CHANNEL_URLS.items()}
    
    # Look up using lowercase channel name
    return channel_map.get(channel_name.lower().strip())


