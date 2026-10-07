# Changelog

## Manual inspection outcome

### Added

- Added Reject and RFI actions to the manual inspection page.
- Added the Rejected Detections admin page, with an action to reopen detections.

### Changed

- `Detection.accepted` is now nullable and holds the manual inspection outcome.
- Manual inspection only lists detections that have not been inspected.
- RFI rejects the detection and adds the `RFI` tag.
- Accept, Reject, and RFI all advance to the next detection.
- Deselect and reopen return the detection to manual inspection.

| Outcome | `accepted` |
| --- | --- |
| Not inspected | `NULL` |
| Accept | `true` |
| Reject | `false` |
| RFI | `false`, with the `RFI` tag |

### Database

New databases are created with a nullable `accepted` column without a default.
Before deploying this version to an existing database (replace `survey` with the
schema of the deployment):

```sql
ALTER TABLE survey.detection ALTER COLUMN accepted DROP DEFAULT;
ALTER TABLE survey.detection ALTER COLUMN accepted DROP NOT NULL;
```

Until now a rejected detection and a detection that had not been inspected were
both stored as `accepted=false`. Decide which of the existing `accepted=false`
rows are rejections, and set the rest to `NULL` so they return to manual
inspection. For example, where nothing has been rejected yet:

```sql
UPDATE survey.detection SET accepted = NULL WHERE accepted = false;
```

Anything that inserts detections (for example SoFiAX) must leave `accepted`
unset, otherwise new detections are treated as rejected.
