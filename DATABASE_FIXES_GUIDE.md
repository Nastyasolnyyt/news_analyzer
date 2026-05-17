# Database Errors Fix Guide

## Issues Fixed

### Issue 1: Duplicate Key Violations in `post_entities` Table

**Error Message:**
```
duplicate key value violates unique constraint "post_entities_pkey"
Key (post_id, entity_id)=(75207, 3) already exists.
STATEMENT: INSERT INTO post_entities (post_id, entity_id) VALUES (75207, 299), (75207, 3), (75207, 3)
```

**Root Cause:**
- The NER extractor was returning duplicate entities from a single article
- Same entity (e.g., entity_id=3) appeared multiple times in the extraction result
- The service tried to insert all of them, causing duplicate key violations

**Solution Applied:**
1. **Deduplication in Extractor** (`services/ner-service/app/extractor.py`):
   - Modified the `extract()` method to deduplicate entities by their lemma (normalized form)
   - Uses a dictionary to track seen lemmas and only returns unique entities
   - Prevents the same entity from being extracted multiple times

2. **Batch Insert with ON CONFLICT** (`services/ner-service/app/kafka_worker.py`):
   - Changed from individual inserts to batch insert with `ON CONFLICT DO NOTHING`
   - Any remaining duplicates are silently ignored at the database level
   - More efficient and atomic operation

**Files Modified:**
- `services/ner-service/app/extractor.py` - Deduplicate entities by lemma
- `services/ner-service/app/kafka_worker.py` - Use batch insert with ON CONFLICT DO NOTHING

---

### Issue 2: Missing Unique Constraint on `risks.article_id`

**Error Message:**
```
there is no unique or exclusion constraint matching the ON CONFLICT specification
STATEMENT: INSERT INTO risks (article_id, risk_type, confidence) VALUES (9230, 'экономический', 0.358...) 
ON CONFLICT (article_id) DO UPDATE SET risk_type = 'экономический', ...
```

**Root Cause:**
- The risk-classifier code used `ON CONFLICT (article_id)` but no UNIQUE constraint existed on that column
- The column was defined as `unique=True` in the SQLAlchemy model but wasn't created in the database
- Alembic migrations might not have been applied or were incomplete

**Solution Applied:**
1. **New Alembic Migration** (`services/output_module/alembic/versions/g6g7h8i9j0k1_fix_unique_constraints.py`):
   - Creates the UNIQUE constraint on `risks.article_id`
   - Handles cases where constraint already exists
   - Removes conflicting indexes before creating the constraint

2. **Improved Error Handling** (`services/risk-classifier/app/storage.py`):
   - Updated both `save_risk_result()` and `save_risk_type()` functions
   - Uses explicit constraint name: `'uq_risks_article_id'`
   - Includes fallback mechanism if constraint doesn't exist:
     - Catches the error
     - Deletes existing record
     - Inserts new record
   - Ensures data consistency even during migration period

**Files Modified:**
- `services/output_module/alembic/versions/g6g7h8i9j0k1_fix_unique_constraints.py` - New migration
- `services/risk-classifier/app/storage.py` - Improved error handling with fallback

---

## Deployment Steps

### Step 1: Update Code

The code changes are already in place. The files have been modified with:
- Entity deduplication in NER service
- Batch insert with ON CONFLICT in NER service  
- Improved error handling in risk-classifier

### Step 2: Apply Database Migrations

Run the Alembic migration to add the missing unique constraint:

```bash
cd services/output_module

# Upgrade to the latest migration
alembic upgrade head
```

Or if running in Docker:

```bash
docker-compose exec app alembic upgrade head
```

**Migration Details:**
- Revision ID: `g6g7h8i9j0k1`
- Adds UNIQUE constraint `uq_risks_article_id` on `risks.article_id`
- Safely handles existing constraints

### Step 3: Restart Services

Rebuild and restart the affected services:

```bash
# For NER service
docker-compose up -d --build ner-service

# For risk-classifier
docker-compose up -d --build risk-classifier

# Or restart all services
docker-compose up -d --build
```

### Step 4: Monitor Logs

After restart, monitor the service logs for any remaining issues:

```bash
# Watch NER service logs
docker-compose logs -f ner-service

# Watch risk-classifier logs
docker-compose logs -f risk-classifier

# Look for these success indicators:
# NER: "✅ Article {id}: saved {count} entities"
# Risk: "✅ Article {id}: type={risk_type} ({confidence:.2f})"
```

---

## Verification Checklist

- [ ] Migration runs successfully without errors
- [ ] NER service logs show unique entity counts (no duplicates)
- [ ] Risk-classifier logs show successful risk insertions
- [ ] No "duplicate key" errors in postgres logs
- [ ] No "unique constraint" errors in risk-classifier logs
- [ ] Data is being processed correctly through the pipeline

---

## Rollback Instructions

If needed, you can rollback the changes:

```bash
cd services/output_module

# Downgrade to previous migration
alembic downgrade f5f6g7h8i9j0
```

---

## Technical Details

### NER Service Changes

**Deduplication Logic:**
```python
# Old: Returns all entities including duplicates
entities = [
    {'lemma': 'москва', 'type': 'LOC'},
    {'lemma': 'москва', 'type': 'LOC'},  # Duplicate!
]

# New: Returns unique entities by lemma
seen_lemmas = {}
# Only one entry for 'москва'
entities = [{'lemma': 'москва', 'type': 'LOC'}]
```

**Batch Insert:**
```python
# Old: Check and insert one by one
for entity in entities:
    if not exists:
        db.add(PostEntity(...))

# New: Batch insert with ON CONFLICT DO NOTHING
entity_links = [{'post_id': 123, 'entity_id': 1}, ...]
stmt = pg_insert(PostEntity).values(entity_links).on_conflict_do_nothing()
db.execute(stmt)
```

### Risk-Classifier Changes

**Constraint Handling:**
```python
# Uses explicit constraint name
stmt = insert(Risk).values(...).on_conflict_do_update(
    constraint='uq_risks_article_id',  # Explicit constraint name
    set_={...}
)

# Fallback mechanism
try:
    db.execute(stmt)
except:
    # Delete and insert if constraint doesn't exist
    db.execute(delete(Risk).where(Risk.article_id == article_id))
    db.add(Risk(...))
```

---

## Prevention Measures

To prevent similar issues in the future:

1. **Input Validation**: Always deduplicate entities at extraction time
2. **Database Constraints**: Ensure all business logic is backed by database constraints
3. **Migration Testing**: Test migrations in staging before production
4. **Error Handling**: Include fallback mechanisms for edge cases
5. **Monitoring**: Set up alerts for duplicate key errors and constraint violations
6. **Code Review**: Verify that SQLAlchemy models match actual database schema

---

## Support

For questions or issues:
1. Check the detailed logs in `docker-compose logs`
2. Verify migration was applied: `SELECT constraint_name FROM information_schema.table_constraints WHERE table_name='risks'`
3. Check post_entities has no duplicates: `SELECT post_id, entity_id, COUNT(*) FROM post_entities GROUP BY post_id, entity_id HAVING COUNT(*) > 1`
