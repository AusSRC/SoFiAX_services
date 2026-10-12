# Changelog

## Modules

### Changed

- The web application is split into Django applications in `app/modules`: `core`, `operations`, `wallaby` and `dingo`.
- `MODULES` selects the applications, the database tables and the tables of the VO service.
- Tags and comments are part of `core` (previously `metadata`).
- Survey components, external conflicts, cross matching and the release of sources are part of `operations`. The run page only has these when `operations` is installed.
- Tiles, source extraction regions and kinematic models are `wallaby` (previously `wallaby_operations` and `wallaby_kinematics`), which requires `operations`.
- The GAMA matches are `dingo` (previously `dingo_gama`).
- The admin pages of a module are shown when the module is installed, not by `PROJECT`.
- The old module names are still accepted in `MODULES`.

### Deployment

The admin pages of the tables that moved out of `core` have new addresses, for example
`/admin/operations/observation/` and `/admin/wallaby/tile/`. The pages of the core tables are unchanged.

To keep the permissions of existing users for the moved tables, update the application of their
content types before starting this version (replace `survey` with the schema of the deployment):

```sql
UPDATE survey.django_content_type SET app_label = 'operations'
 WHERE app_label = 'survey' AND model IN ('externalconflict', 'observation', 'surveycomponent', 'surveycomponentrun');
UPDATE survey.django_content_type SET app_label = 'wallaby'
 WHERE app_label = 'survey' AND model IN ('tile', 'tileobs', 'sourceextractionregion', 'sourceextractionregiontile',
   'kinematicmodel', 'kinematicmodel_3kidnas', 'wkapp_product', 'wrkp_product', 'kinematicmodelstate');
UPDATE survey.django_content_type SET app_label = 'dingo'
 WHERE app_label = 'survey' AND model = 'detectionnearestgama';
```

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
