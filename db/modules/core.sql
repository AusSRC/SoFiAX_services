-- SoFiA output tables and web application tasks
-- Tables are created in the first schema of the search_path (see install-modules.sh)

CREATE TABLE run (
    id bigserial primary key NOT NULL,
    name character varying NOT NULL,
    sanity_thresholds jsonb NOT NULL,
    created timestamp without time zone DEFAULT now()
)
WITH (autovacuum_enabled='on');
ALTER TABLE run ADD CONSTRAINT run_name_unique UNIQUE (name);
ALTER TABLE run ADD CONSTRAINT run_name_sanity_threshold_key UNIQUE (name, sanity_thresholds);

CREATE TABLE instance (
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
ALTER TABLE instance ADD FOREIGN KEY ("run_id") REFERENCES run ("id") ON DELETE CASCADE;
ALTER TABLE instance ADD CONSTRAINT instance_run_id_filename_boundary_key UNIQUE (run_id, filename, boundary);

CREATE TABLE detection (
    id bigserial primary key NOT NULL,
    instance_id bigint NOT NULL,
    run_id bigint NOT NULL,
    name character varying NOT NULL,
    source_name character varying NULL,
    access_url character varying DEFAULT 'https://wallaby.aussrc.org/survey/vo/dl/dlmeta?ID='::character varying NOT NULL,
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
ALTER TABLE detection ADD FOREIGN KEY ("run_id") REFERENCES run ("id") ON DELETE CASCADE;
ALTER TABLE detection ADD FOREIGN KEY ("instance_id") REFERENCES instance ("id") ON DELETE CASCADE;
ALTER TABLE detection ADD CONSTRAINT detection_constraints UNIQUE (name, x, y, z, x_min, x_max, y_min, y_max, z_min, z_max, n_pix, f_min, f_max, f_sum, instance_id, run_id);

CREATE TABLE product (
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
ALTER TABLE product ADD FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON DELETE CASCADE;
ALTER TABLE product ADD CONSTRAINT product_detection_id_key UNIQUE (detection_id);

CREATE TABLE task (
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
