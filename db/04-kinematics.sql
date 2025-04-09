\connect wallabydb

-- WKAPP Kinematic model catalogue
CREATE TABLE wallaby.kinematic_model (
  "id" BIGSERIAL PRIMARY KEY,
  "name" varchar NOT NULL,
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


-- Kinematic model product files
CREATE TABLE wallaby.wkapp_product (
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
ALTER TABLE wallaby.wkapp_product ADD FOREIGN KEY ("kinematic_model_id") REFERENCES wallaby.kinematic_model ("id") ON DELETE CASCADE;


-- WKAPP Kinematic model catalogue
CREATE TABLE wallaby.kinematic_model_3kidnas (
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
ALTER TABLE wallaby.kinematic_model_3kidnas ADD FOREIGN KEY ("detection_id") REFERENCES wallaby.detection ("id") ON DELETE CASCADE;


-- 3KIDNAS Kinematic model product files
CREATE TABLE wallaby.wrkp_product (
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
ALTER TABLE wallaby.wrkp_product ADD FOREIGN KEY ("kinematic_model_3kidnas") REFERENCES wallaby.kinematic_model_3kidnas ("id") ON DELETE CASCADE;

-- Permissions
ALTER TABLE wallaby.kinematic_model OWNER TO cirada;
ALTER TABLE wallaby.wkapp_product OWNER TO cirada;
ALTER TABLE wallaby.kinematic_model_3kidnas OWNER TO cirada;
ALTER TABLE wallaby.wrkp_product OWNER TO cirada;
