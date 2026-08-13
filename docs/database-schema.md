# Database schema

** This doc is AI generatad. Correctness was not verified.

This project uses PostgreSQL database `wallabydb` and schema `wallaby`. The
diagram is derived from the foreign keys in `db/02-tables.sql` and
`db/04-kinematics.sql`; it describes the schema created by the repository, not
the contents of a particular running database.

## Entity relationship diagram

```mermaid
erDiagram
    RUN {
        bigint id PK
        varchar name UK
        jsonb sanity_thresholds
        timestamp created
    }
    INSTANCE {
        bigint id PK
        bigint run_id FK
        varchar filename
        int_array boundary
        timestamp run_date
        jsonb parameters
        int return_code
    }
    DETECTION {
        bigint id PK
        bigint instance_id FK
        bigint run_id FK
        varchar name
        varchar source_name
        double x
        double y
        double z
        double ra
        double dec
        double freq
        boolean accepted
        varchar rejection_reason
        boolean unresolved
    }
    PRODUCT {
        bigint id PK
        bigint detection_id FK,UK
        bytea cube
        bytea mask
        bytea moment_maps
        bytea plots
    }
    COMMENT {
        bigint id PK
        bigint detection_id FK
        text comment
        text author
        timestamp updated_at
    }
    TAG {
        bigint id PK
        varchar name UK
        text description
        text type
    }
    TAG_DETECTION {
        bigint id PK
        bigint tag_id FK
        bigint detection_id FK
        text author
        timestamp added_at
    }
    EXTERNAL_CONFLICT {
        bigint id PK
        bigint run_id FK
        bigint detection_id FK
        bigint conflict_detection_id FK
    }
    QUALITY_CHECK {
        bigint id PK
        bigint run_id FK,UK
        bytea mom0
        bytea frequency
    }
    SURVEY_COMPONENT {
        bigint id PK
        varchar name UK
        varchar_array runs
    }
    SURVEY_COMPONENT_RUN {
        bigint id PK
        bigint run_id FK
        bigint sc_id FK
    }

    RUN ||--o{ INSTANCE : contains
    RUN ||--o{ DETECTION : groups
    INSTANCE ||--o{ DETECTION : produces
    DETECTION ||--o| PRODUCT : has
    DETECTION ||--o{ COMMENT : receives
    TAG ||--o{ TAG_DETECTION : assigned_by
    DETECTION ||--o{ TAG_DETECTION : tagged_through
    RUN ||--o{ EXTERNAL_CONFLICT : scopes
    DETECTION ||--o{ EXTERNAL_CONFLICT : detection
    DETECTION ||--o{ EXTERNAL_CONFLICT : conflicting_detection
    RUN ||--o| QUALITY_CHECK : has
    RUN ||--o{ SURVEY_COMPONENT_RUN : belongs_through
    SURVEY_COMPONENT ||--o{ SURVEY_COMPONENT_RUN : contains_through
```

### Manual inspection state

The `accepted` and nullable `rejection_reason` columns together represent
the current manual inspection outcome:

| Outcome | `accepted` | `rejection_reason` |
| --- | --- | --- |
| Accept | `true` | `NULL` |
| Reject | `false` | `noise` |
| RFI | `false` | `rfi` |
| Pending or legacy unclassified | `false` | `NULL` |

Historical `accepted=false` rows are not backfilled because the old schema
did not distinguish an uninspected detection from an old rejection. Only
non-null rejection reasons written by the new workflow are classified
rejections.

## Observation and scheduling relationships

```mermaid
erDiagram
    RUN {
        bigint id PK
        varchar name UK
    }
    OBSERVATION {
        bigint id PK
        bigint run_id FK
        varchar name
        varchar sbid UK
        numeric ra
        numeric dec
        varchar status
        boolean scheduled
    }
    TILE {
        bigint id PK
        varchar name UK
        numeric ra_deg
        numeric dec_deg
        bigint footprint_A FK,UK
        bigint footprint_B FK,UK
    }
    TILE_OBS {
        bigint id PK
        bigint tile_id FK
        bigint obs_id FK
    }
    SOURCE_EXTRACTION_REGION {
        bigint id PK
        bigint run_id FK
        varchar name
        numeric ra_deg
        numeric dec_deg
        text status
        boolean complete
    }
    SOURCE_EXTRACTION_REGION_TILE {
        bigint id PK
        bigint ser_id FK
        bigint tile_id FK
    }

    RUN o|--o{ OBSERVATION : owns
    OBSERVATION o|--o| TILE : footprint_A
    OBSERVATION o|--o| TILE : footprint_B
    OBSERVATION ||--o{ TILE_OBS : linked_through
    TILE ||--o{ TILE_OBS : linked_through
    RUN o|--o{ SOURCE_EXTRACTION_REGION : defines
    SOURCE_EXTRACTION_REGION ||--o{ SOURCE_EXTRACTION_REGION_TILE : covers_through
    TILE ||--o{ SOURCE_EXTRACTION_REGION_TILE : covered_through
```

## Kinematic catalogue relationships

```mermaid
erDiagram
    DETECTION {
        bigint id PK
        varchar name
    }
    KINEMATIC_MODEL {
        bigint id PK
        bigint detection_id FK
        varchar name
        double ra
        double dec
        double freq
        varchar team_release
        varchar kinver
    }
    WKAPP_PRODUCT {
        bigint id PK
        bigint kinematic_model_id FK
        bytea model_files
    }
    KINEMATIC_MODEL_3KIDNAS {
        bigint id PK
        bigint detection_id FK
        varchar team_release
        double ra_model
        double dec_model
        varchar kinver
    }
    WRKP_PRODUCT {
        bigint id PK
        bigint kinematic_model_3kidnas FK
        bytea model_files
    }

    DETECTION ||--o{ KINEMATIC_MODEL : modelled_by
    KINEMATIC_MODEL ||--o{ WKAPP_PRODUCT : produces
    DETECTION ||--o{ KINEMATIC_MODEL_3KIDNAS : modelled_by
    KINEMATIC_MODEL_3KIDNAS ||--o{ WRKP_PRODUCT : produces
```

## Standalone table

`task` is an operational job table with no declared foreign keys. It stores a
function name, JSON arguments/queryset/result, timestamps, state, error, and
user. PostgreSQL extensions `postgis` and `pg_sphere` are also enabled but do
not add project-owned entities to this diagram.

## Reading the cardinality

- `||` means exactly one, `o|` means zero or one, and `o{` means zero or many.
- `PRODUCT` and `QUALITY_CHECK` are optional one-to-one relations because their
  foreign keys are unique.
- `TAG_DETECTION`, `TILE_OBS`, `SURVEY_COMPONENT_RUN`, and
  `SOURCE_EXTRACTION_REGION_TILE` are association tables implementing
  many-to-many relationships.
- Deleting a run cascades to instances, detections, conflicts, quality checks,
  and survey-component links. Observation links use `SET NULL`; scheduling
  region/tile links use `NO ACTION`.
