-- Observations, quality checks and external conflicts
-- Tables are created in the first schema of the search_path (see install-modules.sh)

CREATE TABLE observation (
    id bigserial primary key NOT NULL,
    run_id bigint,
    name character varying,
    sbid character varying,
    ra numeric NOT NULL,
    "dec" numeric NOT NULL,
    rotation numeric,
    description character varying,
    phase character varying,
    image_cube_file character varying,
    weights_cube_file character varying,
    quality character varying,
    status character varying,
    scheduled boolean
);
ALTER TABLE observation ADD FOREIGN KEY ("run_id") REFERENCES run ("id") ON DELETE SET NULL;
ALTER TABLE observation ADD CONSTRAINT observation_image_cube_file_key UNIQUE (image_cube_file);
ALTER TABLE observation ADD CONSTRAINT observation_sbid_key UNIQUE (sbid);
ALTER TABLE observation ADD CONSTRAINT observation_weights_cube_file_key UNIQUE (weights_cube_file);

CREATE TABLE quality_check (
    id bigserial primary key not null,
    run_id bigint not null unique,
    mom0 bytea,
    frequency bytea
);
ALTER TABLE quality_check ADD FOREIGN KEY ("run_id") REFERENCES run ("id") ON DELETE CASCADE;

CREATE TABLE external_conflict (
    id bigserial primary key NOT NULL,
    run_id bigint NOT NULL,
    detection_id bigint NOT NULL,
    conflict_detection_id bigint NOT NULL
);
ALTER TABLE external_conflict ADD FOREIGN KEY ("run_id") REFERENCES run ("id") ON DELETE CASCADE;
ALTER TABLE external_conflict ADD FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON DELETE CASCADE;
ALTER TABLE external_conflict ADD FOREIGN KEY ("conflict_detection_id") REFERENCES detection ("id") ON DELETE CASCADE;
