## Tests

**Do not run these in a production environment**

A suite of functional tests to ensure the deployment is working correctly. This requires a small amount of setup.

### 1. Deploy

See repo [README](/README.md)

### 2. Injest data

- Download test data (cutouts of SBIDs 51506 and 51535)
- Run SoFiAX
- Run `dss_image` scripts for summary plots

### 3. Running test suite

- Create [`.env`](/tests/.env) with the following

```
URL = "127.0.0.1"
USERNAME = "admin"
PASSWORD = "admin"
TITLE = "survey"
```

Then run the tests pointing to the development environment

```
pytest
```
