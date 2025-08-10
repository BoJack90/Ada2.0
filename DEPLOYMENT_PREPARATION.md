# Przygotowanie Ada 2.0 do wdrożenia na zewnętrznym hostingu

## ✅ Status przygotowania

### 1. **Prompty AI** ✅ GOTOWE
- **20 promptów** zdefiniowanych w systemie
- **Migracja 032** zapewnia odtworzenie wszystkich promptów po czystej instalacji
- Wszystkie prompty są wersjonowane i mają opisy
- Prompty obejmują:
  - Generowanie treści (blog, social media)
  - Analizę briefów i strategii
  - Rewizje i regeneracje
  - Harmonogramowanie
  - Research (Tavily)

### 2. **Optymalizacja Tavily API** ✅ ZAIMPLEMENTOWANE
- Zredukowano zużycie API z **~750 do ~20-30 wywołań** per plan treści (redukcja 97%)
- Wyłączono duplikowanie researchu dla wariantów
- Warianty używają teraz wspólnego researchu z super_context

### 3. **Analiza strony internetowej** ✅ ULEPSZONE
- Dodano AI processing z Google Gemini
- Rozszerzona analiza zawiera:
  - Company overview
  - Unique selling points
  - Brand personality
  - Market positioning
  - Customer pain points
  - Recommended content topics
- Dodano przycisk anulowania dla zawieszonych analiz

## 📋 Checklist przed wdrożeniem

### Zmienne środowiskowe (.env)
```bash
# Baza danych
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# API Keys
TAVILY_API_KEY=tvly-xxxxxxxxxxxx
GEMINI_API_KEY=AIxxxxxxxxxxxxxxxxxx
GOOGLE_AI_API_KEY=AIxxxxxxxxxxxxxxxxxx  # Alternatywa dla GEMINI_API_KEY

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
```

### Migracje bazy danych
1. **Pierwsze uruchomienie** - utwórz tabelę alembic_version:
```sql
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);
```

2. **Uruchom wszystkie migracje**:
```bash
docker exec ada20-web-1 python -m alembic upgrade head
```

3. **Lub ręcznie ustaw wersję** (jeśli baza już istnieje):
```sql
INSERT INTO alembic_version (version_num) VALUES ('032');
```

### Weryfikacja promptów
```sql
-- Sprawdź czy wszystkie 20 promptów istnieje
SELECT COUNT(*) FROM ai_prompts;
-- Powinno zwrócić: 20

-- Lista promptów
SELECT prompt_name FROM ai_prompts ORDER BY prompt_name;
```

### Docker Compose
Upewnij się, że docker-compose.yml używa zmiennych środowiskowych:
```yaml
environment:
  - TAVILY_API_KEY=${TAVILY_API_KEY}
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  - DATABASE_URL=${DATABASE_URL}
```

## 🚀 Kroki wdrożenia

### 1. Przygotowanie środowiska
```bash
# Sklonuj repozytorium
git clone <repo-url>
cd Ada2.0

# Skopiuj i wypełnij .env
cp .env.example .env
# Edytuj .env i dodaj wszystkie klucze API
```

### 2. Uruchomienie kontenerów
```bash
# Build i start
docker-compose up -d --build

# Sprawdź logi
docker-compose logs -f
```

### 3. Inicjalizacja bazy danych
```bash
# Uruchom migracje
docker exec ada20-web-1 python -m alembic upgrade head

# Jeśli potrzeba, uruchom skrypt dla promptów
docker exec ada20-web-1 python run_migration_032.py
```

### 4. Weryfikacja
```bash
# Sprawdź health check
curl http://localhost:8090/api/v1/health

# Sprawdź prompty
docker exec ada20-postgres-1 psql -U ada_user -d ada_db \
  -c "SELECT COUNT(*) FROM ai_prompts;"
```

## 🔍 Monitoring

### Logi Tavily API
```bash
# Sprawdź użycie Tavily
docker-compose logs celery-worker | grep "Tavily" | tail -20

# Powinno pokazywać:
# "Using existing research from super_context"
# NIE powinno pokazywać:
# "Starting Tavily research for topic"
```

### Status zadań Celery
```bash
# Sprawdź kolejkę zadań
docker exec ada20-redis-1 redis-cli LLEN celery
```

## ⚠️ Znane problemy

1. **Tavily API limit** - Upewnij się, że klucz API ma wystarczający limit
2. **Datetime serialization** - Naprawione w website_analysis.py
3. **Alembic version** - Może wymagać ręcznego ustawienia przy istniejącej bazie

## 📝 Notatki

- System jest gotowy do wdrożenia na zewnętrznym hostingu
- Wszystkie prompty AI odtworzą się automatycznie
- Zużycie Tavily API jest zoptymalizowane
- Analiza stron internetowych używa AI dla lepszej jakości
