-- WALLABY tiles, source extraction regions and survey components (requires operations)
-- Tables are created in the first schema of the search_path (see install-modules.sh)

CREATE TABLE tile (
    id bigserial primary key NOT NULL,
    name character varying NOT NULL,
    ra_deg numeric NOT NULL,
    "dec_deg" numeric NOT NULL,
    description character varying,
    phase character varying,
    "footprint_A" bigint,
    "footprint_B" bigint,
    image_cube_file character varying,
    weights_cube_file character varying
);
ALTER TABLE tile ADD FOREIGN KEY ("footprint_B") REFERENCES observation ("id") ON DELETE SET NULL;
ALTER TABLE tile ADD FOREIGN KEY ("footprint_A") REFERENCES observation ("id") ON DELETE SET NULL;
ALTER TABLE tile ADD CONSTRAINT "tile_footprint_A_key" UNIQUE ("footprint_A");
ALTER TABLE tile ADD CONSTRAINT "tile_footprint_B_key" UNIQUE ("footprint_B");
ALTER TABLE tile ADD CONSTRAINT tile_name_key UNIQUE (name);
ALTER TABLE tile ADD CONSTRAINT tile_image_cube_file_key UNIQUE (image_cube_file);
ALTER TABLE tile ADD CONSTRAINT tile_weights_cube_file_key UNIQUE (weights_cube_file);

CREATE TABLE tile_obs (
    id bigserial primary key NOT NULL,
    tile_id bigint NOT NULL,
    obs_id bigint NOT NULL
);
ALTER TABLE tile_obs ADD FOREIGN KEY ("tile_id") REFERENCES tile ("id") ON DELETE NO ACTION;
ALTER TABLE tile_obs ADD FOREIGN KEY ("obs_id") REFERENCES observation ("id") ON DELETE NO ACTION;

CREATE TABLE survey_component (
    id bigserial primary key NOT NULL,
    name character varying NOT NULL,
    runs character varying[]
);
ALTER TABLE survey_component ADD CONSTRAINT survey_component_name_key UNIQUE (name);

CREATE TABLE survey_component_run (
    id bigserial primary key NOT NULL,
    run_id bigint NOT NULL,
    sc_id bigint NOT NULL
);
ALTER TABLE survey_component_run ADD FOREIGN KEY ("run_id") REFERENCES run ("id") ON DELETE CASCADE;
ALTER TABLE survey_component_run ADD FOREIGN KEY ("sc_id") REFERENCES survey_component ("id") ON DELETE CASCADE;
ALTER TABLE survey_component_run ADD CONSTRAINT run_id_sc UNIQUE (run_id, sc_id);

CREATE TABLE source_extraction_region (
    id bigserial primary key NOT NULL,
    run_id bigint,
    name character varying,
    ra_deg numeric,
    "dec_deg" numeric,
    status text,
    complete boolean DEFAULT false,
    scheduled boolean
);
ALTER TABLE source_extraction_region ADD FOREIGN KEY ("run_id") REFERENCES run ("id") ON DELETE NO ACTION;

CREATE TABLE source_extraction_region_tile (
    id bigserial primary key NOT NULL,
    ser_id bigint NOT NULL,
    tile_id bigint NOT NULL
);
ALTER TABLE source_extraction_region_tile ADD FOREIGN KEY ("ser_id") REFERENCES source_extraction_region ("id") ON DELETE NO ACTION;
ALTER TABLE source_extraction_region_tile ADD FOREIGN KEY ("tile_id") REFERENCES tile ("id") ON DELETE NO ACTION;
