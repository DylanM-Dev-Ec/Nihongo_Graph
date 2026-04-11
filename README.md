# NihongoGraph: Relational Database Architecture

This project utilizes a graph architecture stored in SQLite to manage Japanese language acquisition through a spaced repetition system (SRS).

## Entity-Relationship Model (Reflexive Graph)

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
        date last_review
        date next_review
    }
    