from celery.schedules import crontab

# Konfiguracja harmonogramów dla Celery Beat
CELERY_BEAT_SCHEDULE = {
    # Zadanie do planowania postów - uruchamiane co 15 minut
    'schedule-due-posts': {
        'task': 'schedule_due_posts_task',
        'schedule': crontab(minute='*/15'),  # Co 15 minut
        'options': {
            'expires': 300,  # Wygasa po 5 minutach
        }
    },
    
    # Zadanie do czyszczenia starych postów - uruchamiane codziennie o 2:00
    'cleanup-old-posts': {
        'task': 'cleanup_old_posts_task',
        'schedule': crontab(hour=2, minute=0),  # Codziennie o 2:00
        'options': {
            'expires': 3600,  # Wygasa po 1 godzinie
        }
    },
    
    # Opcjonalnie: zadanie do monitorowania statusów postów
    'monitor-publishing-status': {
        'task': 'monitor_publishing_status_task',
        'schedule': crontab(minute='*/30'),  # Co 30 minut
        'options': {
            'expires': 600,  # Wygasa po 10 minutach
        }
    },
}

# Timezone dla harmonogramów
CELERY_TIMEZONE = 'Europe/Warsaw' 