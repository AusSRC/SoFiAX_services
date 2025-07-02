\connect wallabydb
CREATE SCHEMA wallaby;
ALTER SCHEMA wallaby OWNER TO admin;

SET default_tablespace = '';
SET default_table_access_method = heap;

------------------------------------------------------------------------------
-- SoFiA output tables

CREATE TABLE wallaby.run (
    id bigserial primary key NOT NULL,
    name character varying NOT NULL,
    sanity_thresholds jsonb NOT NULL,
    created timestamp without time zone DEFAULT now()
)
WITH (autovacuum_enabled='on');
ALTER TABLE wallaby.run ADD CONSTRAINT run_name_unique UNIQUE (name);
ALTER TABLE wallaby.run ADD CONSTRAINT run_name_sanity_threshold_key UNIQUE (name, sanity_thresholds);
ALTER TABLE wallaby.run OWNER TO admin;

CREATE TABLE wallaby.instance (
    id bigserial primary key NOT NULL,
    run_id bigint NOT NULL,
    filename character varying NOT NULL,
    boundary integer[] NOT NULL,
    run_date timestamp without time zone NOT NULL,
    flag_log bytea,
    reliability_plot bytea,
    log bytea,
    parameters jsonb NOT NULL,
    version character varying,
    return_code integer,
    stdout bytea,
    stderr bytea
)
WITH (autovacuum_enabled='on');
ALTER TABLE wallaby.instance ADD FOREIGN KEY ("run_id") REFERENCES wallaby.run ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.instance ADD CONSTRAINT instance_run_id_filename_boundary_key UNIQUE (run_id, filename, boundary);
ALTER TABLE wallaby.instance OWNER TO admin;

CREATE TABLE wallaby.detection (
    id bigserial primary key NOT NULL,
    instance_id bigint NOT NULL,
    run_id bigint NOT NULL,
    name character varying NOT NULL,
    source_name character varying NULL,
    access_url character varying DEFAULT 'https://wallaby.aussrc.org/wallaby/vo/dl/dlmeta?ID='::character varying NOT NULL,
    access_format character varying DEFAULT 'application/x-votable+xml;content=datalink'::character varying NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    z double precision NOT NULL,
    x_min numeric NOT NULL,
    x_max numeric NOT NULL,
    y_min numeric NOT NULL,
    y_max numeric NOT NULL,
    z_min numeric NOT NULL,
    z_max numeric NOT NULL,
    n_pix numeric NOT NULL,
    f_min double precision,
    f_max double precision,
    f_sum double precision,
    rel double precision,
    rms double precision NOT NULL,
    w20 double precision NOT NULL,
    w50 double precision NOT NULL,
    ell_maj double precision NOT NULL,
    ell_min double precision NOT NULL,
    ell_pa double precision NOT NULL,
    ell3s_maj double precision,
    ell3s_min double precision,
    ell3s_pa double precision,
    kin_pa double precision,
    ra double precision,
    "dec" double precision,
    l double precision,
    b double precision,
    v_rad double precision,
    v_opt double precision,
    v_app double precision,
    err_x double precision,
    err_y double precision,
    err_z double precision,
    err_f_sum double precision,
    freq double precision,
    flag integer,
    unresolved boolean DEFAULT false NOT NULL,
    accepted boolean DEFAULT false NOT NULL,
    wm50 numeric,
    x_peak integer,
    y_peak integer,
    z_peak integer,
    ra_peak numeric,
    dec_peak numeric,
    freq_peak numeric,
    l_peak numeric,
    b_peak numeric,
    v_rad_peak numeric,
    v_opt_peak numeric,
    v_app_peak numeric,
    sofia_id bigint
)
WITH (autovacuum_enabled='on');
ALTER TABLE wallaby.detection ADD FOREIGN KEY ("run_id") REFERENCES wallaby.run ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.detection ADD FOREIGN KEY ("instance_id") REFERENCES wallaby.instance ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.detection ADD CONSTRAINT detection_constraints UNIQUE (name, x, y, z, x_min, x_max, y_min, y_max, z_min, z_max, n_pix, f_min, f_max, f_sum, instance_id, run_id);
ALTER TABLE wallaby.detection OWNER TO admin;

CREATE TABLE wallaby.product (
    id bigserial primary key NOT NULL,
    detection_id bigint NOT NULL,
    cube bytea,
    mask bytea,
    mom0 bytea,
    mom1 bytea,
    mom2 bytea,
    snr bytea,
    chan bytea,
    spec bytea,
    summary bytea,
    plot bytea,
    pv bytea
)
WITH (autovacuum_enabled='on');
ALTER TABLE wallaby.product ADD FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.product ADD CONSTRAINT product_detection_id_key UNIQUE (detection_id);
ALTER TABLE wallaby.product OWNER TO admin;

------------------------------------------------------------------------------
-- Metadata tables

CREATE TABLE wallaby.comment (
    id bigserial primary key NOT NULL,
    comment text NOT NULL,
    author text NOT NULL,
    detection_id bigint NOT NULL,
    updated_at timestamp without time zone DEFAULT now()
);
ALTER TABLE wallaby.comment ADD CONSTRAINT comment_detection_id_fkey FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE wallaby.comment OWNER TO admin;

CREATE TABLE wallaby.tag (
    id bigserial primary key NOT NULL,
    name character varying NOT NULL,
    description text,
    added_at timestamp without time zone DEFAULT now(),
    type text
);
ALTER TABLE wallaby.tag ADD CONSTRAINT tag_name_key UNIQUE (name);
ALTER TABLE wallaby.tag OWNER TO admin;

CREATE TABLE wallaby.tag_detection (
    id bigserial primary key NOT NULL,
    tag_id bigint NOT NULL,
    detection_id bigint NOT NULL,
    author text NOT NULL,
    added_at timestamp without time zone DEFAULT now()
);
ALTER TABLE wallaby.tag_detection ADD FOREIGN KEY ("tag_id") REFERENCES wallaby.tag ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.tag_detection ADD FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.tag_detection OWNER TO admin;

------------------------------------------------------------------------------
-- Operational tables

CREATE TABLE wallaby.external_conflict (
    id bigserial primary key NOT NULL,
    run_id bigint NOT NULL,
    detection_id bigint NOT NULL,
    conflict_detection_id bigint NOT NULL
);
ALTER TABLE wallaby.external_conflict ADD FOREIGN KEY ("run_id") REFERENCES wallaby.run ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.external_conflict ADD FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.external_conflict ADD FOREIGN KEY ("conflict_detection_id") REFERENCES wallaby.detection ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.external_conflict OWNER TO admin;

CREATE TABLE wallaby.observation (
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
ALTER TABLE wallaby.observation ADD FOREIGN KEY ("run_id") REFERENCES wallaby.run ("id") ON DELETE SET NULL;
ALTER TABLE wallaby.observation ADD CONSTRAINT observation_image_cube_file_key UNIQUE (image_cube_file);
ALTER TABLE wallaby.observation ADD CONSTRAINT observation_sbid_key UNIQUE (sbid);
ALTER TABLE wallaby.observation ADD CONSTRAINT observation_weights_cube_file_key UNIQUE (weights_cube_file);
ALTER TABLE wallaby.observation OWNER TO admin;

CREATE TABLE wallaby.tile (
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
ALTER TABLE wallaby.tile ADD FOREIGN KEY ("footprint_B") REFERENCES wallaby.observation ("id") ON DELETE SET NULL;
ALTER TABLE wallaby.tile ADD FOREIGN KEY ("footprint_A") REFERENCES wallaby.observation ("id") ON DELETE SET NULL;
ALTER TABLE wallaby.tile ADD CONSTRAINT "tile_footprint_A_key" UNIQUE ("footprint_A");
ALTER TABLE wallaby.tile ADD CONSTRAINT "tile_footprint_B_key" UNIQUE ("footprint_B");
ALTER TABLE wallaby.tile ADD CONSTRAINT tile_name_key UNIQUE (name);
ALTER TABLE wallaby.tile ADD CONSTRAINT tile_image_cube_file_key UNIQUE (image_cube_file);
ALTER TABLE wallaby.tile ADD CONSTRAINT tile_weights_cube_file_key UNIQUE (weights_cube_file);
ALTER TABLE wallaby.tile OWNER TO admin;

CREATE TABLE wallaby.tile_obs (
    id bigserial primary key NOT NULL,
    tile_id bigint NOT NULL,
    obs_id bigint NOT NULL
);
ALTER TABLE wallaby.tile_obs ADD FOREIGN KEY ("tile_id") REFERENCES wallaby.tile ("id") ON DELETE NO ACTION;
ALTER TABLE wallaby.tile_obs ADD FOREIGN KEY ("obs_id") REFERENCES wallaby.observation ("id") ON DELETE NO ACTION;
ALTER TABLE wallaby.tile_obs OWNER TO admin;

CREATE TABLE wallaby.survey_component (
    id bigserial primary key NOT NULL,
    name character varying NOT NULL,
    runs character varying[]
);
ALTER TABLE wallaby.survey_component ADD CONSTRAINT survey_component_name_key UNIQUE (name);
ALTER TABLE wallaby.survey_component OWNER TO admin;

CREATE TABLE wallaby.survey_component_run (
    id bigserial primary key NOT NULL,
    run_id bigint NOT NULL,
    sc_id bigint NOT NULL
);
ALTER TABLE wallaby.survey_component_run ADD FOREIGN KEY ("run_id") REFERENCES wallaby.run ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.survey_component_run ADD FOREIGN KEY ("sc_id") REFERENCES wallaby.survey_component ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.survey_component_run ADD CONSTRAINT run_id_sc UNIQUE (run_id, sc_id);
ALTER TABLE wallaby.survey_component_run OWNER TO admin;

CREATE TABLE wallaby.source_extraction_region (
    id bigserial primary key NOT NULL,
    run_id bigint,
    name character varying,
    ra_deg numeric,
    "dec_deg" numeric,
    status text,
    complete boolean DEFAULT false,
    scheduled boolean
);
ALTER TABLE wallaby.source_extraction_region ADD FOREIGN KEY ("run_id") REFERENCES wallaby.run ("id") ON DELETE NO ACTION;
ALTER TABLE wallaby.source_extraction_region OWNER TO admin;

CREATE TABLE wallaby.source_extraction_region_tile (
    id bigserial primary key NOT NULL,
    ser_id bigint NOT NULL,
    tile_id bigint NOT NULL
);
ALTER TABLE wallaby.source_extraction_region_tile ADD FOREIGN KEY ("ser_id") REFERENCES wallaby.source_extraction_region ("id") ON DELETE NO ACTION;
ALTER TABLE wallaby.source_extraction_region_tile ADD FOREIGN KEY ("tile_id") REFERENCES wallaby.tile ("id") ON DELETE NO ACTION;
ALTER TABLE wallaby.source_extraction_region_tile OWNER TO admin;

------------------------------------------------------------------------------
-- Other

CREATE TABLE wallaby.task (
    id bigserial primary key NOT NULL,
    func text NOT NULL,
    args jsonb,
    queryset jsonb,
    start timestamp without time zone DEFAULT now(),
    "end" timestamp without time zone,
    retval jsonb,
    error text,
    state text DEFAULT 'PENDING'::text,
    "user" text
);
ALTER TABLE wallaby.task OWNER TO admin;

CREATE TABLE wallaby.quality_check (
    id bigserial primary key not null,
    run_id bigint not null unique,
    mom0 bytea,
    frequency bytea
);
ALTER TABLE wallaby.quality_check ADD FOREIGN KEY ("run_id") REFERENCES wallaby.run ("id") ON DELETE CASCADE;
ALTER TABLE wallaby.quality_check OWNER TO admin;

------------------------------------------------------------------------------
-- Required extensions
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_sphere";
