-- Create database
CREATE DATABASE surveydb WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';

-- Create admin user
CREATE USER "admin";
ALTER USER "admin" WITH PASSWORD 'admin';
ALTER USER "admin" WITH SUPERUSER;
ALTER DATABASE surveydb OWNER TO "admin";

-- Create SURVEY user (read only)
CREATE USER "survey_user";
ALTER USER "survey_user" WITH PASSWORD 'survey_user';

-- Create VO user
CREATE USER "gavo";
ALTER USER "gavo" WITH PASSWORD 'gavo';
CREATE USER "gavoadmin";
ALTER USER "gavoadmin" WITH PASSWORD 'gavoadmin';
CREATE USER "untrusted";
ALTER USER "untrusted" WITH PASSWORD 'untrusted';

\connect surveydb


CREATE SCHEMA survey;
ALTER SCHEMA survey OWNER TO admin;

SET default_tablespace = '';
SET default_table_access_method = heap;

CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_sphere";

GRANT ALL ON DATABASE surveydb TO gavo;
GRANT ALL ON DATABASE surveydb TO gavoadmin;
GRANT CONNECT ON DATABASE surveydb TO untrusted;

GRANT ALL ON SCHEMA public TO gavo;
GRANT ALL ON SCHEMA public TO gavoadmin;
GRANT USAGE ON SCHEMA public TO untrusted;


CREATE TABLE survey.comment (
    id bigint NOT NULL,
    comment text NOT NULL,
    author text NOT NULL,
    detection_id bigint NOT NULL,
    updated_at timestamp without time zone NOT NULL
);

ALTER TABLE survey.comment OWNER TO admin;

CREATE SEQUENCE survey.comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE survey.comment_id_seq OWNER TO admin;

ALTER SEQUENCE survey.comment_id_seq OWNED BY survey.comment.id;

CREATE TABLE survey.detection (
    id bigint NOT NULL,
    instance_id bigint NOT NULL,
    run_id bigint NOT NULL,
    name character varying NOT NULL,
    access_url character varying DEFAULT 'https://survey.aussrc.org/survey/vo/dl/dlmeta?ID='::character varying NOT NULL,
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
    f_min double precision NOT NULL,
    f_max double precision NOT NULL,
    f_sum double precision NOT NULL,
    rel double precision,
    rms double precision NOT NULL,
    w20 double precision NOT NULL,
    w50 double precision NOT NULL,
    ell_maj double precision NOT NULL,
    ell_min double precision NOT NULL,
    ell_pa double precision NOT NULL,
    ell3s_maj double precision NOT NULL,
    ell3s_min double precision NOT NULL,
    ell3s_pa double precision NOT NULL,
    kin_pa double precision,
    ra double precision,
    "dec" double precision,
    l double precision,
    b double precision,
    v_rad double precision,
    v_opt double precision,
    v_app double precision,
    err_x double precision NOT NULL,
    err_y double precision NOT NULL,
    err_z double precision NOT NULL,
    err_f_sum double precision NOT NULL,
    freq double precision,
    flag integer,
    unresolved boolean DEFAULT false NOT NULL,
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


ALTER TABLE survey.detection OWNER TO admin;

CREATE SEQUENCE survey.detection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.detection_id_seq OWNER TO admin;

ALTER SEQUENCE survey.detection_id_seq OWNED BY survey.detection.id;

CREATE TABLE survey.external_conflict (
    id bigint NOT NULL,
    run_id bigint NOT NULL,
    detection_id bigint NOT NULL,
    conflict_source_detection_ids integer[] NOT NULL
);


ALTER TABLE survey.external_conflict OWNER TO admin;


CREATE SEQUENCE survey.external_conflict_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.external_conflict_id_seq OWNER TO admin;


ALTER SEQUENCE survey.external_conflict_id_seq OWNED BY survey.external_conflict.id;


CREATE SEQUENCE survey.instance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.instance_id_seq OWNER TO admin;


CREATE TABLE survey.instance (
    id bigint DEFAULT nextval('survey.instance_id_seq'::regclass) NOT NULL,
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


ALTER TABLE survey.instance OWNER TO admin;


CREATE TABLE survey.observation (
    id bigint NOT NULL,
    sbid bigint NOT NULL,
    ra numeric NOT NULL,
    "dec" numeric NOT NULL,
    description character varying,
    phase character varying,
    image_cube_file character varying,
    weights_cube_file character varying,
    quality character varying,
    status character varying,
    name character varying,
    rotation numeric
);


ALTER TABLE survey.observation OWNER TO admin;


CREATE SEQUENCE survey.observation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.observation_id_seq OWNER TO admin;

ALTER SEQUENCE survey.observation_id_seq OWNED BY survey.observation.id;


CREATE TABLE survey.observation_metadata (
    id bigint NOT NULL,
    observation_id bigint NOT NULL,
    slurm_output jsonb NOT NULL
);


ALTER TABLE survey.observation_metadata OWNER TO admin;


CREATE SEQUENCE survey.observation_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.observation_metadata_id_seq OWNER TO admin;


ALTER SEQUENCE survey.observation_metadata_id_seq OWNED BY survey.observation_metadata.id;


CREATE TABLE survey.postprocessing (
    id bigint NOT NULL,
    run_id bigint,
    name character varying NOT NULL,
    region character varying,
    sofia_parameter_file character varying,
    s2p_setup character varying,
    status character varying
);


ALTER TABLE survey.postprocessing OWNER TO admin;


CREATE SEQUENCE survey.postprocessing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.postprocessing_id_seq OWNER TO admin;


ALTER SEQUENCE survey.postprocessing_id_seq OWNED BY survey.postprocessing.id;


CREATE TABLE survey.prerequisite (
    id bigint NOT NULL,
    run_name character varying NOT NULL,
    sofia_parameter_file character varying,
    s2p_setup character varying,
    status character varying
);


ALTER TABLE survey.prerequisite OWNER TO admin;

--
-- TOC entry 310 (class 1259 OID 25208)
-- Name: prerequisite_id_seq; Type: SEQUENCE; Schema: survey; Owner: admin
--

CREATE SEQUENCE survey.prerequisite_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.prerequisite_id_seq OWNER TO admin;

--
-- TOC entry 5492 (class 0 OID 0)
-- Dependencies: 310
-- Name: prerequisite_id_seq; Type: SEQUENCE OWNED BY; Schema: survey; Owner: admin
--

ALTER SEQUENCE survey.prerequisite_id_seq OWNED BY survey.prerequisite.id;


--
-- TOC entry 313 (class 1259 OID 25218)
-- Name: prerequisite_identifier; Type: TABLE; Schema: survey; Owner: admin
--

CREATE TABLE survey.prerequisite_identifier (
    id bigint NOT NULL,
    prerequisite_id bigint NOT NULL,
    tile_id bigint NOT NULL
);


ALTER TABLE survey.prerequisite_identifier OWNER TO admin;


CREATE SEQUENCE survey.prerequisite_identifier_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.prerequisite_identifier_id_seq OWNER TO admin;

ALTER SEQUENCE survey.prerequisite_identifier_id_seq OWNED BY survey.prerequisite_identifier.id;

CREATE SEQUENCE survey.product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.product_id_seq OWNER TO admin;

CREATE TABLE survey.product (
    id bigint DEFAULT nextval('survey.product_id_seq'::regclass) NOT NULL,
    detection_id bigint NOT NULL,
    cube bytea,
    mask bytea,
    mom0 bytea,
    mom1 bytea,
    mom2 bytea,
    snr bytea,
    chan bytea,
    spec bytea,
    pv bytea,
    plot bytea
)
WITH (autovacuum_enabled='on');


ALTER TABLE survey.product OWNER TO admin;

CREATE SEQUENCE survey.run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.run_id_seq OWNER TO admin;

--
-- TOC entry 232 (class 1259 OID 18502)
-- Name: run; Type: TABLE; Schema: survey; Owner: admin
--

CREATE TABLE survey.run (
    id bigint DEFAULT nextval('survey.run_id_seq'::regclass) NOT NULL,
    name character varying NOT NULL,
    sanity_thresholds jsonb NOT NULL,
    created timestamp without time zone DEFAULT now()
)
WITH (autovacuum_enabled='on');


ALTER TABLE survey.run OWNER TO admin;

CREATE TABLE survey.source (
    id bigint NOT NULL,
    name character varying NOT NULL
)
WITH (autovacuum_enabled='on');


ALTER TABLE survey.source OWNER TO admin;


CREATE SEQUENCE survey.source_detection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.source_detection_id_seq OWNER TO admin;


CREATE TABLE survey.source_detection (
    id bigint DEFAULT nextval('survey.source_detection_id_seq'::regclass) NOT NULL,
    source_id bigint NOT NULL,
    detection_id bigint NOT NULL,
    added_at timestamp without time zone DEFAULT now()
)
WITH (autovacuum_enabled='on');


ALTER TABLE survey.source_detection OWNER TO admin;


CREATE SEQUENCE survey.source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.source_id_seq OWNER TO admin;


ALTER SEQUENCE survey.source_id_seq OWNED BY survey.source.id;


CREATE TABLE survey.survey_component (
    id bigint NOT NULL,
    name character varying NOT NULL,
    runs character varying[]
);


ALTER TABLE survey.survey_component OWNER TO admin;


CREATE SEQUENCE survey.survey_component_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.survey_component_id_seq OWNER TO admin;

ALTER SEQUENCE survey.survey_component_id_seq OWNED BY survey.survey_component.id;

CREATE TABLE survey.tag (
    id bigint NOT NULL,
    name character varying NOT NULL,
    description text,
    added_at timestamp without time zone DEFAULT now(),
    type text
);

ALTER TABLE survey.tag OWNER TO admin;

CREATE SEQUENCE survey.tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE survey.tag_id_seq OWNER TO admin;

ALTER SEQUENCE survey.tag_id_seq OWNED BY survey.tag.id;

CREATE TABLE survey.tag_source_detection (
    id bigint NOT NULL,
    tag_id bigint NOT NULL,
    source_detection_id bigint NOT NULL,
    author text NOT NULL,
    added_at timestamp without time zone DEFAULT now()
);

ALTER TABLE survey.tag_source_detection OWNER TO admin;

CREATE SEQUENCE survey.tag_source_detection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE survey.tag_source_detection_id_seq OWNER TO admin;

ALTER SEQUENCE survey.tag_source_detection_id_seq OWNED BY survey.tag_source_detection.id;

CREATE TABLE survey.task (
    id bigint NOT NULL,
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


ALTER TABLE survey.task OWNER TO admin;

CREATE SEQUENCE survey.task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE survey.task_id_seq OWNER TO admin;

ALTER SEQUENCE survey.task_id_seq OWNED BY survey.task.id;

CREATE TABLE survey.tile (
    id bigint NOT NULL,
    ra numeric NOT NULL,
    "dec" numeric NOT NULL,
    identifier character varying NOT NULL,
    description character varying,
    phase character varying,
    "footprint_A" bigint,
    "footprint_B" bigint,
    image_cube_file character varying,
    weights_cube_file character varying
);

ALTER TABLE survey.tile OWNER TO admin;

CREATE SEQUENCE survey.tile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE survey.tile_id_seq OWNER TO admin;

ALTER SEQUENCE survey.tile_id_seq OWNED BY survey.tile.id;

ALTER TABLE ONLY survey.comment ALTER COLUMN id SET DEFAULT nextval('survey.comment_id_seq'::regclass);

ALTER TABLE ONLY survey.detection ALTER COLUMN id SET DEFAULT nextval('survey.detection_id_seq'::regclass);

ALTER TABLE ONLY survey.external_conflict ALTER COLUMN id SET DEFAULT nextval('survey.external_conflict_id_seq'::regclass);

ALTER TABLE ONLY survey.observation ALTER COLUMN id SET DEFAULT nextval('survey.observation_id_seq'::regclass);

ALTER TABLE ONLY survey.observation_metadata ALTER COLUMN id SET DEFAULT nextval('survey.observation_metadata_id_seq'::regclass);

ALTER TABLE ONLY survey.postprocessing ALTER COLUMN id SET DEFAULT nextval('survey.postprocessing_id_seq'::regclass);

ALTER TABLE ONLY survey.prerequisite ALTER COLUMN id SET DEFAULT nextval('survey.prerequisite_id_seq'::regclass);

ALTER TABLE ONLY survey.prerequisite_identifier ALTER COLUMN id SET DEFAULT nextval('survey.prerequisite_identifier_id_seq'::regclass);

ALTER TABLE ONLY survey.source ALTER COLUMN id SET DEFAULT nextval('survey.source_id_seq'::regclass);

ALTER TABLE ONLY survey.survey_component ALTER COLUMN id SET DEFAULT nextval('survey.survey_component_id_seq'::regclass);

ALTER TABLE ONLY survey.tag ALTER COLUMN id SET DEFAULT nextval('survey.tag_id_seq'::regclass);

ALTER TABLE ONLY survey.tag_source_detection ALTER COLUMN id SET DEFAULT nextval('survey.tag_source_detection_id_seq'::regclass);

ALTER TABLE ONLY survey.task ALTER COLUMN id SET DEFAULT nextval('survey.task_id_seq'::regclass);

ALTER TABLE ONLY survey.tile ALTER COLUMN id SET DEFAULT nextval('survey.tile_id_seq'::regclass);


ALTER TABLE ONLY survey.comment
    ADD CONSTRAINT comment_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.detection
    ADD CONSTRAINT detection_constraints UNIQUE (name, x, y, z, x_min, x_max, y_min, y_max, z_min, z_max, n_pix, f_min, f_max, f_sum, instance_id, run_id);



ALTER TABLE ONLY survey.detection
    ADD CONSTRAINT detection_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.external_conflict
    ADD CONSTRAINT external_conflict_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.instance
    ADD CONSTRAINT instance_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.instance
    ADD CONSTRAINT instance_run_id_filename_boundary_key UNIQUE (run_id, filename, boundary);


ALTER TABLE ONLY survey.observation
    ADD CONSTRAINT observation_image_cube_file_key UNIQUE (image_cube_file);


ALTER TABLE ONLY survey.observation_metadata
    ADD CONSTRAINT observation_metadata_observation_id_key UNIQUE (observation_id);


ALTER TABLE ONLY survey.observation_metadata
    ADD CONSTRAINT observation_metadata_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.observation
    ADD CONSTRAINT observation_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.observation
    ADD CONSTRAINT observation_sbid_key UNIQUE (sbid);


ALTER TABLE ONLY survey.observation
    ADD CONSTRAINT observation_weights_cube_file_key UNIQUE (weights_cube_file);


ALTER TABLE ONLY survey.postprocessing
    ADD CONSTRAINT postprocessing_name_key UNIQUE (name);


ALTER TABLE ONLY survey.postprocessing
    ADD CONSTRAINT postprocessing_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.postprocessing
    ADD CONSTRAINT postprocessing_run_id_key UNIQUE (run_id);


ALTER TABLE ONLY survey.prerequisite_identifier
    ADD CONSTRAINT prerequisite_identifier_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.prerequisite_identifier
    ADD CONSTRAINT prerequisite_identifier_prerequisite_id_key UNIQUE (prerequisite_id);


ALTER TABLE ONLY survey.prerequisite_identifier
    ADD CONSTRAINT prerequisite_identifier_tile_id_key UNIQUE (tile_id);


ALTER TABLE ONLY survey.prerequisite
    ADD CONSTRAINT prerequisite_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.product
    ADD CONSTRAINT product_detection_id_key UNIQUE (detection_id);


ALTER TABLE ONLY survey.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);

ALTER TABLE ONLY survey.run
    ADD CONSTRAINT run_name_sanity_threshold_key UNIQUE (name, sanity_thresholds);


ALTER TABLE ONLY survey.run
    ADD CONSTRAINT run_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.source_detection
    ADD CONSTRAINT source_detection_detection_id_key UNIQUE (detection_id);


ALTER TABLE ONLY survey.source_detection
    ADD CONSTRAINT source_detection_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.source
    ADD CONSTRAINT source_name_key UNIQUE (name);


ALTER TABLE ONLY survey.source
    ADD CONSTRAINT source_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.survey_component
    ADD CONSTRAINT survey_component_name_key UNIQUE (name);


ALTER TABLE ONLY survey.survey_component
    ADD CONSTRAINT survey_component_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.tag
    ADD CONSTRAINT tag_name_key UNIQUE (name);


ALTER TABLE ONLY survey.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.tag_source_detection
    ADD CONSTRAINT tag_source_detection_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.task
    ADD CONSTRAINT task_pk PRIMARY KEY (id);


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT "tile_footprint_A_key" UNIQUE ("footprint_A");


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT "tile_footprint_B_key" UNIQUE ("footprint_B");


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT tile_identifier_key UNIQUE (identifier);


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT tile_image_cube_file_key UNIQUE (image_cube_file);


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT tile_pkey PRIMARY KEY (id);


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT tile_weights_cube_file_key UNIQUE (weights_cube_file);


ALTER TABLE ONLY survey.comment
    ADD CONSTRAINT comment_detection_id_fkey FOREIGN KEY (detection_id) REFERENCES survey.detection(id) ON UPDATE CASCADE ON DELETE CASCADE;


ALTER TABLE ONLY survey.detection
    ADD CONSTRAINT detection_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES survey.instance(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.detection
    ADD CONSTRAINT detection_run_id_fkey FOREIGN KEY (run_id) REFERENCES survey.run(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.external_conflict
    ADD CONSTRAINT external_conflict_detection_id_fkey FOREIGN KEY (detection_id) REFERENCES survey.detection(id) ON UPDATE CASCADE ON DELETE CASCADE;


ALTER TABLE ONLY survey.external_conflict
    ADD CONSTRAINT external_conflict_run_id_fkey FOREIGN KEY (run_id) REFERENCES survey.run(id) ON UPDATE CASCADE ON DELETE CASCADE;


ALTER TABLE ONLY survey.instance
    ADD CONSTRAINT instance_run_id_fkey FOREIGN KEY (run_id) REFERENCES survey.run(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.observation_metadata
    ADD CONSTRAINT observation_metadata_observation_id_fkey FOREIGN KEY (observation_id) REFERENCES survey.observation(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.postprocessing
    ADD CONSTRAINT postprocessing_run_id_fkey FOREIGN KEY (run_id) REFERENCES survey.run(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.prerequisite_identifier
    ADD CONSTRAINT prerequisite_identifier_prerequisite_id_fkey FOREIGN KEY (prerequisite_id) REFERENCES survey.prerequisite(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.prerequisite_identifier
    ADD CONSTRAINT prerequisite_identifier_tile_id_fkey FOREIGN KEY (tile_id) REFERENCES survey.tile(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.product
    ADD CONSTRAINT product_detection_id_fkey FOREIGN KEY (detection_id) REFERENCES survey.detection(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.source_detection
    ADD CONSTRAINT source_detection_detection_id_fkey FOREIGN KEY (detection_id) REFERENCES survey.detection(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.source_detection
    ADD CONSTRAINT source_detection_source_id_fkey FOREIGN KEY (source_id) REFERENCES survey.source(id) ON DELETE CASCADE;

ALTER TABLE ONLY survey.tag_source_detection
    ADD CONSTRAINT tag_source_detection_source_detection_id_fkey FOREIGN KEY (source_detection_id) REFERENCES survey.source_detection(id) ON UPDATE CASCADE ON DELETE CASCADE;


ALTER TABLE ONLY survey.tag_source_detection
    ADD CONSTRAINT tag_source_detection_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES survey.tag(id) ON UPDATE CASCADE ON DELETE CASCADE;


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT "tile_footprint_A_fkey" FOREIGN KEY ("footprint_A") REFERENCES survey.observation(id) ON DELETE CASCADE;


ALTER TABLE ONLY survey.tile
    ADD CONSTRAINT "tile_footprint_B_fkey" FOREIGN KEY ("footprint_B") REFERENCES survey.observation(id) ON DELETE CASCADE;


GRANT USAGE ON SCHEMA survey TO survey_user;
GRANT USAGE ON SCHEMA survey TO gavoadmin;
GRANT USAGE ON SCHEMA survey TO gavo;
GRANT USAGE ON SCHEMA survey TO untrusted;


GRANT SELECT ON TABLE survey.comment TO survey_user;
GRANT SELECT ON TABLE survey.comment TO gavoadmin;
GRANT SELECT ON TABLE survey.comment TO gavo;
GRANT SELECT ON TABLE survey.comment TO untrusted;


GRANT SELECT ON SEQUENCE survey.comment_id_seq TO survey_user;
GRANT SELECT,USAGE ON SEQUENCE survey.comment_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.comment_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.comment_id_seq TO untrusted;


GRANT SELECT ON TABLE survey.detection TO gavoadmin;
GRANT SELECT ON TABLE survey.detection TO gavo;
GRANT SELECT ON TABLE survey.detection TO untrusted;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE survey.detection TO survey_user;


GRANT SELECT,USAGE ON SEQUENCE survey.detection_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.detection_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.detection_id_seq TO untrusted;
GRANT SELECT,USAGE ON SEQUENCE survey.detection_id_seq TO survey_user;


GRANT SELECT,USAGE ON SEQUENCE survey.instance_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.instance_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.instance_id_seq TO untrusted;
GRANT SELECT,UPDATE ON SEQUENCE survey.instance_id_seq TO survey_user;

GRANT SELECT ON TABLE survey.instance TO gavoadmin;
GRANT SELECT ON TABLE survey.instance TO gavo;
GRANT SELECT ON TABLE survey.instance TO untrusted;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE survey.instance TO survey_user;

GRANT SELECT ON TABLE survey.observation TO survey_user;

GRANT SELECT ON TABLE survey.observation_metadata TO survey_user;


GRANT SELECT ON TABLE survey.postprocessing TO survey_user;

GRANT SELECT,USAGE ON SEQUENCE survey.product_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.product_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.product_id_seq TO untrusted;
GRANT SELECT,UPDATE ON SEQUENCE survey.product_id_seq TO survey_user;


GRANT SELECT ON TABLE survey.product TO gavoadmin;
GRANT SELECT ON TABLE survey.product TO gavo;
GRANT SELECT ON TABLE survey.product TO untrusted;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE survey.product TO survey_user;

GRANT SELECT,USAGE ON SEQUENCE survey.run_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.run_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.run_id_seq TO untrusted;
GRANT SELECT,UPDATE ON SEQUENCE survey.run_id_seq TO survey_user;

GRANT SELECT ON TABLE survey.run TO gavoadmin;
GRANT SELECT ON TABLE survey.run TO gavo;
GRANT SELECT ON TABLE survey.run TO untrusted;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE survey.run TO survey_user;

GRANT SELECT ON TABLE survey.source TO survey_user;
GRANT SELECT ON TABLE survey.source TO gavoadmin;
GRANT SELECT ON TABLE survey.source TO gavo;
GRANT SELECT ON TABLE survey.source TO untrusted;


GRANT SELECT,USAGE ON SEQUENCE survey.source_detection_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.source_detection_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.source_detection_id_seq TO untrusted;
GRANT SELECT,UPDATE ON SEQUENCE survey.source_detection_id_seq TO survey_user;


GRANT SELECT ON TABLE survey.source_detection TO survey_user;
GRANT SELECT ON TABLE survey.source_detection TO gavoadmin;
GRANT SELECT ON TABLE survey.source_detection TO gavo;
GRANT SELECT ON TABLE survey.source_detection TO untrusted;


GRANT SELECT ON SEQUENCE survey.source_id_seq TO survey_user;
GRANT SELECT,USAGE ON SEQUENCE survey.source_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.source_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.source_id_seq TO untrusted;


GRANT SELECT ON TABLE survey.tag TO survey_user;
GRANT SELECT ON TABLE survey.tag TO gavoadmin;
GRANT SELECT ON TABLE survey.tag TO gavo;
GRANT SELECT ON TABLE survey.tag TO untrusted;


GRANT SELECT ON SEQUENCE survey.tag_id_seq TO survey_user;
GRANT SELECT,USAGE ON SEQUENCE survey.tag_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.tag_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.tag_id_seq TO untrusted;


GRANT SELECT ON TABLE survey.tag_source_detection TO survey_user;
GRANT SELECT ON TABLE survey.tag_source_detection TO gavoadmin;
GRANT SELECT ON TABLE survey.tag_source_detection TO gavo;
GRANT SELECT ON TABLE survey.tag_source_detection TO untrusted;

GRANT SELECT ON SEQUENCE survey.tag_source_detection_id_seq TO survey_user;
GRANT SELECT,USAGE ON SEQUENCE survey.tag_source_detection_id_seq TO gavoadmin;
GRANT SELECT,USAGE ON SEQUENCE survey.tag_source_detection_id_seq TO gavo;
GRANT SELECT,USAGE ON SEQUENCE survey.tag_source_detection_id_seq TO untrusted;


GRANT SELECT ON TABLE survey.tile TO survey_user;