-- Comments and tags on detections
-- Tables are created in the first schema of the search_path (see install-modules.sh)

CREATE TABLE comment (
    id bigserial primary key NOT NULL,
    comment text NOT NULL,
    author text NOT NULL,
    detection_id bigint NOT NULL,
    updated_at timestamp without time zone DEFAULT now()
);
ALTER TABLE comment ADD CONSTRAINT comment_detection_id_fkey FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON UPDATE CASCADE ON DELETE CASCADE;

CREATE TABLE tag (
    id bigserial primary key NOT NULL,
    name character varying NOT NULL,
    description text,
    added_at timestamp without time zone DEFAULT now(),
    type text
);
ALTER TABLE tag ADD CONSTRAINT tag_name_key UNIQUE (name);

CREATE TABLE tag_detection (
    id bigserial primary key NOT NULL,
    tag_id bigint NOT NULL,
    detection_id bigint NOT NULL,
    author text NOT NULL,
    added_at timestamp without time zone DEFAULT now()
);
ALTER TABLE tag_detection ADD FOREIGN KEY ("tag_id") REFERENCES tag ("id") ON DELETE CASCADE;
ALTER TABLE tag_detection ADD FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON DELETE CASCADE;
