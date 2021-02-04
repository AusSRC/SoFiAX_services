\connect sofiadb

-- Introducing additional functionality to detections table:
--    * Multiple tagging on all detections (Many-to-many)
--    * Comments for all detections (One-to-many)
--    * Sources table (catalogue of selected detections)

-- Tagging functionality

CREATE TABLE wallaby.tag (
  "id" BIGSERIAL PRIMARY KEY,
  "tag_name" varchar NOT NULL,
  "description" text,
  "added_at" timestamp without time zone NOT NULL,
  unique ("tag_name")
);

CREATE TABLE wallaby.tag_detection (
  "id" BIGSERIAL PRIMARY KEY,
  "tag_id" bigint NOT NULL,
  "detection_id" bigint NOT NULL
);

ALTER TABLE wallaby.tag_detection ADD FOREIGN KEY ("tag_id") REFERENCES wallaby.tag ("id") ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE wallaby.tag_detection ADD FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON UPDATE CASCADE ON DELETE CASCADE;

-- Commenting functionality
-- TODO: Add user details

CREATE TABLE wallaby.comments (
  "id" BIGSERIAL PRIMARY KEY,
  "comment" text NOT NULL,
  "detection_id" bigint NOT NULL,
  "added_at" timestamp without time zone NOT NULL,
  "updated_at" timestamp without time zone
);
ALTER TABLE wallaby.comments ADD FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON UPDATE CASCADE ON DELETE CASCADE;

-- Sources selected for catalogue

CREATE TABLE wallaby.sources (
  "id" BIGSERIAL PRIMARY KEY,
  "detection_id" bigint NOT NULL
);

ALTER TABLE wallaby.sources ADD FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON UPDATE CASCADE ON DELETE CASCADE;