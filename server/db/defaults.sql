-- Column defaults that depend on the deployment. Run by install-modules.sh with psql variables.

ALTER TABLE :"schema".detection ALTER COLUMN access_url SET DEFAULT :'access_url';
