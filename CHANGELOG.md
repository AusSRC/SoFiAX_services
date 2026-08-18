# Changelog

## Unreleased

### Added

- Added Reject and RFI actions to the manual inspection page.
- Added the nullable `Detection.rejection_reason` field.
- Added functional coverage for the Reject and RFI workflows.

### Changed

- Manual inspection now excludes detections with a rejection reason.
- Reject stores `noise`; RFI stores `rfi`.
- Accept and existing deselect/reopen workflows clear `rejection_reason`.
- Accept, Reject, and RFI all advance to the next detection.

### Database

Before deploying this version, add the nullable column to the existing database:

```sql
ALTER TABLE wallaby.detection
ADD COLUMN IF NOT EXISTS rejection_reason varchar NULL;
```

The application interprets `accepted` and `rejection_reason` together:

| Outcome | `accepted` | `rejection_reason` |
| --- | --- | --- |
| Accept | `true` | `NULL` |
| Reject | `false` | `noise` |
| RFI | `false` | `rfi` |
| Pending or legacy unclassified | `false` | `NULL` |

Button behaviour:

- Accept sets `accepted=true` and clears `rejection_reason`.
- Reject sets `accepted=false` and `rejection_reason=noise`.
- RFI sets `accepted=false` and `rejection_reason=rfi`.
- All three outcomes remove the detection from the current manual inspection
  list.
- Deselect/reopen clears `rejection_reason`, allowing the detection to return
  to manual inspection when it still meets the other list filters.

Historical rows are intentionally not backfilled. Before this change, an old
rejection and a detection that had never been inspected were both stored as
