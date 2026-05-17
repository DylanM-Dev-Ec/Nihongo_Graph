# Kioku Engine (MVP)

An optimized memory retention and spaced repetition engine (SRS) designed for structured Japanese language acquisition, utilizing a localized relational graph architecture in SQLite.

## Project Scope (MVP Limits)
To avoid scope creep and ensure system stability, this iteration is strictly constrained to:
- **Core Syllabaries:** Complete Hiragana and Katakana character mapping.
- **Vocabulary Baseline:** First 50 foundational N5 Kanjis and their core radical components.
- **SRS Execution:** Algorithmic scheduling based on a modified SM-2 (SuperMemo-2) interval calculation.

## Technical Architecture

### Relational Schema (Reflexive Graph)
```mermaid
erDiagram
    CONCEPT ||--o{ CONNECTION : "is source of"
    CONCEPT ||--o{ CONNECTION : "is target of"
    CONCEPT ||--|| PROGRESS : "has"

    CONCEPT {
        int concept_id PK
        string kanji
        string hiragana
        string katakana
        int jlpt_level
    }

    CONNECTION {
        int source_id FK
        int target_id FK
        string relationship_type
    }

    PROGRESS {
        int progress_id PK
        int concept_id FK
        float hit_rate
        int interval_days
        int repetitions
        float ease_factor
        date last_review
        date next_review
    }
    