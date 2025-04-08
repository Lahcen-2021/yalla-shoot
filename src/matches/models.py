from django.db import models

class Match(models.Model):
    STREAM_STATUS = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    match_date = models.DateTimeField()
    stream_url = models.URLField(blank=True)
    stream_status = models.CharField(max_length=10, choices=STREAM_STATUS, default='offline')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class HistoricalMatch(models.Model):
    match_id = models.IntegerField(unique=True)
    league_id = models.IntegerField()
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    match_date = models.DateTimeField()
    status = models.CharField(max_length=10)
    channel = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-match_date']