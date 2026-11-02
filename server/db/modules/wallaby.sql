-- WALLABY tiles, source extraction regions, and kinematic model catalogues and products (requires operations)
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

CREATE TABLE kinematic_model (
  "id" BIGSERIAL PRIMARY KEY,
  "detection_id" bigint NOT NULL,
  "name" varchar,
  "ra" double precision NOT NULL,
  "dec" double precision NOT NULL,
  "freq" double precision NOT NULL,
  "team_release" varchar NOT NULL,
  "team_release_kin" varchar NOT NULL,
  "vsys_model" double precision NOT NULL,
  "e_vsys_model" double precision NOT NULL,
  "x_model" double precision NOT NULL,
  "e_x_model" double precision NOT NULL,
  "y_model" double precision NOT NULL,
  "e_y_model" double precision NOT NULL,
  "ra_model" double precision NOT NULL,
  "e_ra_model" double precision NOT NULL,
  "dec_model" double precision NOT NULL,
  "e_dec_model" double precision NOT NULL,
  "inc_model" double precision NOT NULL,
  "e_inc_model" double precision NOT NULL,
  "pa_model" double precision NOT NULL,
  "e_pa_model" double precision NOT NULL,
  "pa_model_g" double precision NOT NULL,
  "e_pa_model_g" double precision NOT NULL,
  "qflag_model" integer NOT NULL,
  "rad" varchar NOT NULL,
  "vrot_model" varchar NOT NULL,
  "e_vrot_model" varchar NOT NULL,
  "e_vrot_model_inc" varchar NOT NULL,
  "rad_sd" varchar NOT NULL,
  "sd_model" varchar NOT NULL,
  "sd_fo_model" varchar NOT NULL,
  "e_sd_model" varchar NULL,
  "e_sd_fo_model_inc" varchar NULL,
  "r_hi" double precision NULL,
  "v_disp" double precision NULL,
  "v_rhi" double precision NULL,
  "kinver" varchar NULL
);
ALTER TABLE kinematic_model ADD FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON DELETE CASCADE;

CREATE TABLE wkapp_product (
  "id" BIGSERIAL PRIMARY KEY,
  "kinematic_model_id" BIGINT NOT NULL,
  "baroloinput" bytea,
  "barolomod" bytea,
  "barolosurfdens" bytea,
  "diagnosticplot" bytea,
  "diffcube" bytea,
  "fatinput" bytea,
  "fatmod" bytea,
  "fullresmodcube" bytea,
  "fullresproccube" bytea,
  "modcube" bytea,
  "procdata" bytea
);
ALTER TABLE wkapp_product ADD FOREIGN KEY ("kinematic_model_id") REFERENCES kinematic_model ("id") ON DELETE CASCADE;

CREATE TABLE kinematic_model_3kidnas (
  "id" BIGSERIAL PRIMARY KEY,
  "detection_id" bigint NOT NULL,
  "team_release" varchar NOT NULL,
  "team_release_kin" varchar NOT NULL,
  "vsys_model" double precision NOT NULL,
  "e_vsys_model" double precision NOT NULL,
  "x_model" double precision NOT NULL,
  "e_x_model" double precision NOT NULL,
  "y_model" double precision NOT NULL,
  "e_y_model" double precision NOT NULL,
  "ra_model" double precision NOT NULL,
  "e_ra_model" double precision NOT NULL,
  "dec_model" double precision NOT NULL,
  "e_dec_model" double precision NOT NULL,
  "inc_model" double precision NOT NULL,
  "e_inc_model" double precision NOT NULL,
  "pa_model" double precision NOT NULL,
  "e_pa_model" double precision NOT NULL,
  "pa_model_g" double precision NOT NULL,
  "e_pa_model_g" double precision NOT NULL,
  "vdisp_model" double precision NOT NULL,
  "e_vdisp_model" double precision NOT NULL,
  "rad" varchar NOT NULL,
  "vrot_model" varchar NOT NULL,
  "e_vrot_model" varchar NOT NULL,
  "rad_sd" varchar NOT NULL,
  "sd_model" varchar NOT NULL,
  "e_sd_model" varchar NULL,
  "sdmethodflag" integer NOT NULL,
  "rhi_flag" integer NOT NULL,
  "rhi_as" double precision,
  "rhi_low_as" double precision,
  "rhi_high_as" double precision,
  "dist_model" double precision NOT NULL,
  "rhi_kpc" double precision,
  "rhi_low_kpc" double precision,
  "rhi_high_kpc" double precision,
  "vhi_flag" integer NOT NULL,
  "vhi" double precision,
  "e_vhi" double precision,
  "kflag" integer NOT NULL,
  "kinver" varchar NULL
);
ALTER TABLE kinematic_model_3kidnas ADD FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON DELETE CASCADE;

CREATE TABLE wrkp_product (
  "id" BIGSERIAL PRIMARY KEY,
  "kinematic_model_3kidnas" BIGINT NOT NULL,
  "bootstrapfits" bytea,
  "diagnosticplot" bytea,
  "diffcube" bytea,
  "flag" bytea,
  "modcube" bytea,
  "procdata" bytea,
  "pvmajordata" bytea,
  "pvmajormod" bytea,
  "pvminordata" bytea,
  "pvminormod" bytea
);
ALTER TABLE wrkp_product ADD FOREIGN KEY ("kinematic_model_3kidnas") REFERENCES kinematic_model_3kidnas ("id") ON DELETE CASCADE;

-- Detections waiting for kinematic modelling
CREATE TABLE kinematic_model_state (
    id bigserial primary key NOT NULL,
    detection_id bigint NOT NULL,
    attempted integer NOT NULL
);
ALTER TABLE kinematic_model_state ADD FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON DELETE CASCADE;
