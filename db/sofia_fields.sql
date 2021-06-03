-- Update detections table based on new information from WALLABY science team --

-- 02/06/2021 --
ALTER TABLE wallaby.detection ADD
    "wm50" numeric NULL,
    "x_peak" integer NULL,
    "y_peak" integer NULL,
    "z_peak" integer NULL,
    "ra_peak" numeric NULL,
    "dec_peak" numeric NULL,
    "freq_peak" numeric NULL,
    "l_peak" numeric NULL,
    "b_peak" numeric NULL,
    "v_rad_peak" numeric NULL,
    "v_opt_peak" numeric NULL,
    "v_app_peak" numeric NULL;