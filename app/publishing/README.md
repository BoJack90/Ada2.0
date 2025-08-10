# Publishing System - Automated Content Publishing

System automatycznego publikowania treści na zewnętrzne platformy społecznościowe.

## Architektura

### Komponenty:
1. **PublishingService** - Serwis do publikacji na różnych platformach
2. **Celery Tasks** - Zadania do publikacji i zarządzania harmonogramem
3. **Celery Beat** - Automatyczne planowanie zadań

### Obsługiwane platformy:
- LinkedIn
- Facebook  
- Instagram
- WordPress

## Konfiguracja

### Zmienne środowiskowe

Dodaj następujące zmienne do konfiguracji:

```bash
# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_CLIENT_ID=your_linkedin_client_id

# Facebook
FACEBOOK_ACCESS_TOKEN=your_facebook_token
FACEBOOK_PAGE_ID=your_facebook_page_id

# Instagram
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id

# WordPress
WORDPRESS_USERNAME=your_wordpress_username
WORDPRESS_PASSWORD=your_wordpress_password
WORDPRESS_SITE_URL=https://your-site.com
```

### Uruchamianie

1. **Celery Worker** - do wykonywania zadań publikacji:
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

2. **Celery Beat** - do automatycznego planowania:
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

## Workflow

### 1. Planowanie publikacji

System automatycznie sprawdza co 15 minut posty, które mają być opublikowane w ciągu najbliższych 30 minut:

- Status: `scheduled` → `queued`
- Zadanie publikacji zostaje zaplanowane na dokładny czas `publication_date`

### 2. Publikacja

Gdy nadejdzie czas publikacji:

- Pobiera `ScheduledPost` i powiązany zaakceptowany `ContentVariant`
- Pobiera dane uwierzytelniające dla platformy
- Publikuje treść na platformie
- Aktualizuje status: `queued` → `published` lub `failed`

### 3. Monitorowanie

System monitoruje statusy publikacji co 30 minut:

- Zbiera statystyki
- Resetuje "utknięte" posty w statusie `queued`
- Loguje informacje o stanie systemu

## Dostępne zadania

### `publish_post_task(scheduled_post_id: int)`
Publikuje pojedynczy post na platformie.

### `schedule_due_posts_task()`
Planuje posty do publikacji (uruchamiane co 15 minut).

### `cleanup_old_posts_task()`
Czyści stare posty (uruchamiane codziennie o 2:00).

### `monitor_publishing_status_task()`
Monitoruje statusy publikacji (uruchamiane co 30 minut).

## Statusy postów

- `scheduled` - Zaplanowany do publikacji
- `queued` - Zadanie publikacji zakolejkowane
- `published` - Opublikowany pomyślnie
- `failed` - Publikacja nie powiodła się

## Rozwijanie

### Dodawanie nowej platformy

1. Dodaj metodę w `PublishingService`
2. Dodaj obsługę w `publish_to_platform()`
3. Dodaj dane uwierzytelniające w `get_platform_credentials()`

### Przykład:

```python
async def publish_to_twitter(self, content: str, credentials: Dict[str, Any]) -> bool:
    try:
        # Implementacja API Twitter
        return True
    except Exception as e:
        self.logger.error(f"Failed to publish to Twitter: {str(e)}")
        return False
```

## Bezpieczeństwo

- Wszystkie dane uwierzytelniające są pobierane z bezpiecznych źródeł
- Hasła i tokeny nie są przechowywane w kodzie
- Wszystkie operacje są logowane
- Timeouty i obsługa błędów są zaimplementowane

## Logowanie

System loguje:
- Wszystkie operacje publikacji
- Błędy i wyjątki
- Statystyki publikacji
- Operacje planowania zadań

Logi zawierają informacje o:
- ID posta
- Platformie
- Statusie operacji
- Szczegółach błędów 