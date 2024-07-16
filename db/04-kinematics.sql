\connect surveydb

-- WKAPP Kinematic model catalogue
CREATE TABLE wallaby.kinematic_model (
  "id" BIGSERIAL PRIMARY KEY
);
ALTER TABLE wallaby.kinematic_model ADD COLUMN "name" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "ra" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "dec" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "freq" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "team_release" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "team_release_kin" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "vsys_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_vsys_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "x_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_x_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "y_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_y_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "ra_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_ra_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "dec_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_dec_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "inc_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_inc_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "pa_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_pa_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "pa_model_g" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_pa_model_g" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "qflag_model" integer NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "rad" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "vrot_model" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_vrot_model" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_vrot_model_inc" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "rad_sd" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "sd_model" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "sd_fo_model" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_sd_model" varchar NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "e_sd_fo_model_inc" varchar NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "r_hi" double precision NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "v_disp" double precision NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "v_rhi" double precision NULL;
ALTER TABLE wallaby.kinematic_model ADD COLUMN "kinver" varchar NULL;
ALTER TABLE wallaby.kinematic_model ADD FOREIGN KEY ("name") REFERENCES wallaby.source ("name") ON DELETE CASCADE;


-- Kinematic model product files
CREATE TABLE wallaby.wkapp_product (
  "id" BIGSERIAL PRIMARY KEY
);
ALTER TABLE wallaby.wkapp_product ADD COLUMN "kinematic_model_id" BIGINT NOT NULL;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "baroloinput" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "barolomod" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "barolosurfdens" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "diagnosticplot" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "diffcube" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "fatinput" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "fatmod" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "fullresmodcube" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "fullresproccube" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "modcube" bytea;
ALTER TABLE wallaby.wkapp_product ADD COLUMN "procdata" bytea;
ALTER TABLE wallaby.wkapp_product ADD FOREIGN KEY ("kinematic_model_id") REFERENCES wallaby.kinematic_model ("id") ON DELETE CASCADE;




-- WKAPP Kinematic model catalogue
CREATE TABLE wallaby.kinematic_model_3kidnas (
  "id" BIGSERIAL PRIMARY KEY
);
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "name" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "team_release" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "team_release_kin" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "vsys_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_vsys_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "x_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_x_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "y_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_y_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "ra_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_ra_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "dec_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_dec_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "inc_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_inc_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "pa_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_pa_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "pa_model_g" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_pa_model_g" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "vdisp_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_vdisp_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rad" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "vrot_model" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_vrot_model" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_vrot_model_inc" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rad_sd" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "sd_model" varchar NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_sd_model" varchar NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "sdmethodflag" integer NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rhi_flag" integer NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rhi_as" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rhi_low_as" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rhi_high_as" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "dist_model" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rhi_kpc" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rhi_low_kpc" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "rhi_high_kpc" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "vhi_flag" integer NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "vhi" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "e_vhi" double precision NOT NULL;
ALTER TABLE wallaby.kinematic_model_3kidnas ADD COLUMN "kflag" integer NOT NULL;
ALTER TABLE wallaby.kkinematic_model_3kidnas ADD COLUMN "kinver" varchar NULL;
ALTER TABLE wallaby.kkinematic_model_3kidnas ADD FOREIGN KEY ("name") REFERENCES wallaby.source ("name") ON DELETE CASCADE;

-- 3KIDNAS Kinematic model product files
CREATE TABLE wallaby.wrkp_product (
  "id" BIGSERIAL PRIMARY KEY
);
ALTER TABLE wallaby.wrkp_product ADD COLUMN "kinematic_model_id" BIGINT NOT NULL;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "bootstrapfits" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "diagnosticplot" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "diffcube" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "flag" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "modcube" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "procdata" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "pvmajordata" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "pvmajormod" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "pvminordata" bytea;
ALTER TABLE wallaby.wrkp_product ADD COLUMN "pvminormod" bytea;
ALTER TABLE wallaby.wrkp_product ADD FOREIGN KEY ("kinematic_model_id") REFERENCES wallaby.kinematic_model ("id") ON DELETE CASCADE;
