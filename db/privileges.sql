\connect sofiadb

ALTER TABLE wallaby.run OWNER TO "admin";
ALTER TABLE wallaby.instance OWNER TO "admin";
ALTER TABLE wallaby.detection OWNER TO "admin";
ALTER TABLE wallaby.products OWNER TO "admin";
ALTER TABLE wallaby.tag OWNER TO "admin";
ALTER TABLE wallaby.tag_detection OWNER TO "admin";
ALTER TABLE wallaby.comments OWNER TO "admin";
ALTER TABLE wallaby.sources OWNER TO "admin";

GRANT ALL PRIVILEGES ON DATABASE sofiadb TO "admin";
GRANT ALL PRIVILEGES ON DATABASE sofiadb TO "gavoadmin";
GRANT ALL PRIVILEGES ON DATABASE sofiadb TO "gavo";

GRANT CONNECT ON DATABASE sofiadb TO "wallaby_user";
GRANT USAGE ON SCHEMA "wallaby" TO "wallaby_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE wallaby.instance, wallaby.detection, wallaby.run, wallaby.products, wallaby.tag, wallaby.tag_detection, wallaby.comments, wallaby.sources TO "wallaby_user";
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA wallaby TO "wallaby_user";

GRANT CONNECT ON DATABASE sofiadb TO "gavoadmin";
GRANT USAGE ON SCHEMA "wallaby" TO "gavoadmin";
GRANT SELECT ON TABLE wallaby.instance, wallaby.detection, wallaby.run, wallaby.products, wallaby.tag, wallaby.tag_detection, wallaby.comments, wallaby.sources TO "gavoadmin";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA wallaby TO "gavoadmin";

GRANT CONNECT ON DATABASE sofiadb TO "gavo";
GRANT USAGE ON SCHEMA "wallaby" TO "gavo";
GRANT SELECT ON TABLE wallaby.instance, wallaby.detection, wallaby.run, wallaby.products, wallaby.tag, wallaby.tag_detection, wallaby.comments, wallaby.sources TO "gavo";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA wallaby TO "gavo";

GRANT CONNECT ON DATABASE sofiadb TO "untrusted";
GRANT USAGE ON SCHEMA "wallaby" TO "untrusted";
GRANT SELECT ON TABLE wallaby.instance, wallaby.detection, wallaby.run, wallaby.products, wallaby.tag, wallaby.tag_detection, wallaby.comments, wallaby.sources TO "untrusted";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA wallaby TO "untrusted";