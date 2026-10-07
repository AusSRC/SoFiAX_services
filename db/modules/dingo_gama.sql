-- DINGO: nearest GAMA catalogue objects for each detection (cata_id is the GAMA CATAID)
-- Tables are created in the first schema of the search_path (see install-modules.sh)

CREATE TABLE detection_nearest_gama (
    id bigserial primary key NOT NULL,
    detection_id bigint NOT NULL,
    cata_id bigint NOT NULL
);
ALTER TABLE detection_nearest_gama ADD FOREIGN KEY ("detection_id") REFERENCES detection ("id") ON DELETE CASCADE;
CREATE INDEX ON detection_nearest_gama (detection_id);
