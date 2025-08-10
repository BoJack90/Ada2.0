# Optymalizacja wykorzystania Tavily API

## 🚨 KRYTYCZNY PROBLEM
Obecnie system wykonuje **700+ wywołań Tavily API** dla jednego planu treści!

### Rzeczywiste zużycie:
- **4 wywołania** - analiza strony
- **13 wywołań** - research tematów
- **16 wywołań** - 4 posty bloga × 4 zapytania każdy
- **144 wywołania** - 12 postów SM × 3 platformy × 4 zapytania
- **× 3-4 regeneracje** = **531-708 WYWOŁAŃ RAZEM!**

Każdy wariant wykonuje WŁASNY research z 4 zapytaniami zamiast używać wspólnych danych!

## 🔥 PILNA NAPRAWA - Wyłącz research dla wariantów!

### NATYCHMIAST: Wyłącz Tavily w variant_generation.py
**Plik**: `app/tasks/variant_generation.py` linia 374-456
**Akcja**: ZAKOMENTUJ cały blok researchu lub ustaw `skip_research = True`
```python
# PRZED (linie 374-456):
research_context = ""
try:
    logger.info(f"Starting Tavily research for topic: {topic_title}")
    # ... 80 linii kodu z 4 wywołaniami Tavily ...
    
# PO:
research_context = ""  # Research już był zrobiony podczas generowania tematów!
skip_research = True  # WYŁĄCZ TAVILY DLA WARIANTÓW
```
**Efekt**: Z 700 wywołań spadnie do ~20 wywołań (redukcja 97%!)

## Rozwiązania długoterminowe

### 1. **Cache współdzielony między wariantami** (Redukcja: 95%)
**Problem**: Każdy wariant robi osobny research dla tego samego tematu
**Rozwiązanie**: Zrób research RAZ per temat, użyj dla wszystkich wariantów
```python
# W generate_content_variant_task
research_cache_key = f"topic_research_{topic_id}"
if research_cache_key in redis_cache:
    research_data = redis_cache.get(research_cache_key)
else:
    research_data = tavily.research(topic)
    redis_cache.set(research_cache_key, research_data, ttl=7200)  # 2h cache
```

### 2. **Wyłącz research dla postów SM** (Redukcja: 50%)
**Problem**: Krótkie posty SM nie potrzebują głębokiego researchu
**Rozwiązanie**: Research tylko dla blogów
```python
if content_type == 'blog':
    research_data = tavily.research(topic)
else:
    research_data = None  # SM używa tylko kontekstu z super_context
```

### 3. **Batch research zamiast pojedynczych** (Redukcja: 30%)
**Problem**: Osobne wywołania dla każdego aspektu
**Rozwiązanie**: Jedno wywołanie z wieloma pytaniami
```python
# Zamiast 4 wywołań dla analizy strony:
all_questions = [
    f"company overview {url}",
    f"industry sector {url}",
    f"services offered {url}",
    f"company values {url}"
]
result = tavily.search(' AND '.join(all_questions), max_results=10)
# Parsuj jeden wynik na 4 kategorie
```

### 4. **Zwiększ cache TTL** (Redukcja: 20%)
**Problem**: Cache 24h, ale plany często regenerowane
**Rozwiązanie**: 
- Cache analizy strony: 7 dni
- Cache research tematów: 3 dni
- Cache ogólnych trendów: 7 dni

### 5. **Warunki pomijania researchu** (Redukcja: 15%)
```python
# Pomiń research gdy:
if any([
    'case study' in topic.lower(),  # Case studies używają danych wewnętrznych
    'zespół' in topic.lower(),      # Posty o zespole
    'akson elektro' in topic.lower() and 'sukces' in topic.lower(),  # Własne sukcesy
]):
    skip_research = True
```

## Implementacja priorytetowa

### Krok 1: Cache współdzielony (najłatwiejszy)
**Plik**: `app/tasks/content_generation.py`
**Funkcja**: `generate_content_variant_task`
**Czas**: 30 min
**Redukcja**: 70% wywołań

### Krok 2: Wyłącz dla SM
**Plik**: `app/tasks/content_generation.py`  
**Warunek**: `if platform != 'blog'`
**Czas**: 15 min
**Redukcja**: 50% pozostałych

### Krok 3: Batch queries
**Plik**: `app/core/external_integrations.py`
**Funkcja**: `analyze_website`
**Czas**: 1h
**Redukcja**: 30% dla nowych analiz

## Wynik końcowy
Po implementacji:
- Przed: **65 wywołań**
- Po: **8-12 wywołań** (redukcja 80-85%)

## Monitoring
Dodaj licznik wywołań:
```python
# W TavilyIntegration.__init__
self.api_calls_count = 0

# W każdej metodzie wywołującej API
self.api_calls_count += 1
logger.info(f"Tavily API call #{self.api_calls_count}: {method_name}")
```