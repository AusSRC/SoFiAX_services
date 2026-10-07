   <table id="kinematic_model" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id"/>
      <column type="double precision" name="ra" unit="deg" ucd="pos.eq.ra;meta.main" description="Right ascension (J2000) of centroid position" verbLevel="1"/>
      <column type="double precision" name="dec" unit="deg" ucd="pos.eq.dec;meta.main" description="Declination (J2000) of centroid position" verbLevel="1"/>
      <column type="double precision" name="freq" unit="Hz" ucd="em.freq;meta.main" description="Barycentric frequency of centroid position"/>
      <column name="team_release" type="text" unit="" ucd="meta.dataset;meta.main" description="Internal team release"/>
      <column name="team_release_kin" type="text" unit="" ucd="meta.dataset;meta.main" description="Internal kinematic team release"/>
      <column name="vsys_model" type="double precision" unit="km/s" ucd="phys.veloc" description="Model systemic velocity"/>
      <column name="e_vsys_model" type="double precision" unit="km/s" ucd="stat.error;phys.veloc" description="Statistical uncertainty of model systemic velocity"/>
      <column name="x_model" type="double precision" unit="pix" ucd="pos.cartesian.x" description="Kinematically modelled center position in X"/>
      <column name="e_x_model" type="double precision" unit="pix" ucd="stat.error;pos.cartesian.x" description="Statistical uncertainty of modelled center position in X"/>
      <column name="y_model" type="double precision" unit="pix" ucd="pos.cartesian.y" description="Kinematically modelled center position in Y"/>
      <column name="e_y_model" type="double precision" unit="pix" ucd="stat.error;pos.cartesian.y" description="Statistical uncertainty of modelled center position in Y"/>
      <column name="ra_model" type="double precision" unit="deg" description="Kinematically modelled center position in Right ascension (J2000)"/>
      <column name="e_ra_model" type="double precision" unit="deg" ucd="stat.error;pos.eq.ra" description="Statistical uncertainty of modelled center position in Right ascension (J2000)"/>
      <column name="dec_model" type="double precision" unit="deg" ucd="pos.eq.dec" description="Kinematically modelled center position in Declination (J2000)"/>
      <column name="e_dec_model" type="double precision" unit="deg" ucd="stat.error;pos.eq.dec" description="Statistical uncertainty of modelled center position in Declination (J2000)"/>
      <column name="inc_model" type="double precision" unit="deg" ucd="phys" description="Kinematically modelled inclination"/>
      <column name="e_inc_model" type="double precision" unit="deg" ucd="stat.error;phys" description="Statistical uncertainty of modelled inclination"/>
      <column name="pa_model" type="double precision" unit="deg" ucd="pos.posAng" description="Kinematically modelled position angle relative to the local X-Y axis"/>
      <column name="e_pa_model" type="double precision" unit="deg" ucd="stat.error;pos.posAng" description="Statistical uncertainty of modelled position angle"/>
      <column name="pa_model_g" type="double precision" unit="deg" ucd="pos.posAng" description="Kinematically modelled position angle relative to the global N-S coordinates"/>
      <column name="e_pa_model_g" type="double precision" unit="deg" ucd="stat.error;pos.posAng" description="Statistical uncertainty of modelled position angle relative to the global N-S coordinates"/>
      <column name="qflag_model" type="integer" unit="" ucd="meta.code.qual" description="Kinematic model quality flag"/>
      <column name="rad" type="text" unit="arcsec" ucd="phys.size.radius" description="The radial array for the rotation curve"/>
      <column name="vrot_model" type="text" unit="km/s" ucd="phys.veloc.rotat" description="The kinematically modelled rotation curve"/>
      <column name="e_vrot_model" type="text" unit="km/s" ucd="stat.error;phys.veloc.rotat" description="Statistical uncertainty of the rotation curve"/>
      <column name="e_vrot_model_inc" type="text" unit="km/s" ucd="stat.error;phys.veloc.rotat" description="Statistical uncertainty of the rotation curve due to the error on the inclination"/>
      <column name="rad_sd" type="text" unit="arcsec" ucd="phys.size.radius" description="The radial array for the surface density profile"/>
      <column name="sd_model" type="text" unit="msol/pc^2" ucd="phys.density" description="The kinematically modelled projected surface density profile"/>
      <column name="e_sd_model" type="text" unit="msol/pc^2" ucd="stat.error;phys.density" description="Statistical uncertainty of the projected surface density"/>
      <column name="sd_fo_model" type="text" unit="msol/pc^2" ucd="phys.density" description="The kinematically modelled deprojected surface density profile"/>
      <column name="e_sd_fo_model_inc" type="text" unit="msol/pc^2" ucd="stat.error;phys.density" description="Statistical uncertainty of the deprojected surface density due to the inclination"/>
      <column name="r_hi" type="double precision" unit="arcsec" ucd="phys.size.radius" description="The radius where the surface density is 1 Msol/pc^2"/>
      <column name="v_disp" type="double precision" unit="km/s" ucd="phys.veloc.dispersion" description="The model velocity dispersion"/>
      <column name="v_rhi" type="double precision" unit="km/s" ucd="phys.veloc.rotat" description="The rotation velocity at r_hi"/>
      <column name="kinver" type="text" unit="" description="The version of the software used to generate the kinematic model"/>
      <foreignKey source="detection_id" dest="id" inTable="detection"/>
   </table>

   <table id="kinematic_model_3kidnas" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="team_release" type="text" unit="" ucd="meta.dataset;meta.main" description="Internal team release"/>
      <column name="team_release_kin" type="text" unit="" ucd="meta.dataset;meta.main" description="Internal kinematic team release"/>
      <column name="vsys_model" type="double precision" unit="km/s" ucd="phys.veloc" description="Model systemic velocity"/>
      <column name="e_vsys_model" type="double precision" unit="km/s" ucd="stat.error;phys.veloc" description="Statistical uncertainty of model systemic velocity"/>
      <column name="x_model" type="double precision" unit="pix" ucd="pos.cartesian.x" description="Kinematically modelled center position in X"/>
      <column name="e_x_model" type="double precision" unit="pix" ucd="stat.error;pos.cartesian.x" description="Statistical uncertainty of modelled center position in X"/>
      <column name="y_model" type="double precision" unit="pix" ucd="pos.cartesian.y" description="Kinematically modelled center position in Y"/>
      <column name="e_y_model" type="double precision" unit="pix" ucd="stat.error;pos.cartesian.y" description="Statistical uncertainty of modelled center position in Y"/>
      <column name="ra_model" type="double precision" unit="deg" description="Kinematically modelled center position in Right ascension (J2000)"/>
      <column name="e_ra_model" type="double precision" unit="deg" ucd="stat.error;pos.eq.ra" description="Statistical uncertainty of modelled center position in Right ascension (J2000)"/>
      <column name="dec_model" type="double precision" unit="deg" ucd="pos.eq.dec" description="Kinematically modelled center position in Declination (J2000)"/>
      <column name="e_dec_model" type="double precision" unit="deg" ucd="stat.error;pos.eq.dec" description="Statistical uncertainty of modelled center position in Declination (J2000)"/>
      <column name="inc_model" type="double precision" unit="deg" ucd="phys" description="Kinematically modelled inclination"/>
      <column name="e_inc_model" type="double precision" unit="deg" ucd="stat.error;phys" description="Statistical uncertainty of modelled inclination"/>
      <column name="pa_model" type="double precision" unit="deg" ucd="pos.posAng" description="Kinematically modelled position angle relative to the local X-Y axis"/>
      <column name="e_pa_model" type="double precision" unit="deg" ucd="stat.error;pos.posAng" description="Statistical uncertainty of modelled position angle"/>
      <column name="pa_model_g" type="double precision" unit="deg" ucd="pos.posAng" description="Kinematically modelled position angle relative to the global N-S coordinates"/>
      <column name="e_pa_model_g" type="double precision" unit="deg" ucd="stat.error;pos.posAng" description="Statistical uncertainty of modelled position angle relative to the global N-S coordinates"/>
      <column name="vdisp_model" type="double precision" unit="km/s" ucd="phys.veloc.dispersion" description="The model velocity dispersion"/>
      <column name="e_vdisp_model" type="double precision" unit="km/s" ucd="stat.error;phys.veloc.dispersion" description="Statistical uncertainty of modelled velocity dispersion"/>
      <column name="rad" type="text" unit="arcsec" ucd="phys.size.radius" description="The radial array for the rotation curve"/>
      <column name="vrot_model" type="text" unit="km/s" ucd="phys.veloc.rotat" description="The kinematically modelled rotation curve"/>
      <column name="e_vrot_model" type="text" unit="km/s" ucd="stat.error;phys.veloc.rotat" description="Statistical uncertainty of the rotation curve"/>
      <column name="rad_sd" type="text" unit="arcsec" ucd="phys.size.radius" description="The radial array for the surface density profile"/>
      <column name="sd_model" type="text" unit="msol/pc^2" ucd="phys.density" description="The kinematically modelled projected surface density profile"/>
      <column name="e_sd_model" type="text" unit="msol/pc^2" ucd="stat.error;phys.density" description="Statistical uncertainty of the projected surface density"/>
      <column name="sdmethodflag" type="integer" unit="" ucd="meta.code" description="A flag indicating the method used for obtaining the SD profile"/>
      <column name="rhi_flag" type="integer" unit="" ucd="meta.code.qual" description="A flag indicating the measurement of r_hi"/>
      <column name="rhi_as" type="double precision" unit="arcsec" ucd="phys.size.radius" description="The radius where the surface density is 1 Msol/pc^2 in arcsec"/>
      <column name="rhi_low_as" type="double precision" unit="arcsec" ucd="stat.error;phys.size.radius" description="The lower limit on rhi_as in arcsec"/>
      <column name="rhi_high_as" type="double precision" unit="arcsec" ucd="stat.error;phys.size.radius" description="The upper limit rhi_as on in arcsec"/>
      <column name="dist_model" type="double precision" unit="arcsec" ucd="pos.distance" description="The estimated distance to the galaxy based on the Hubble Flow with H0=70 km/s/kpc"/>
      <column name="rhi_kpc" type="double precision" unit="kpc" ucd="phys.size.radius" description="The value of rhi_as converted into kpc based on dist_model"/>
      <column name="rhi_low_kpc" type="double precision" unit="kpc" ucd="stat.error;phys.size.radius" description="The lower limit on rhi_kpc in kpc"/>
      <column name="rhi_high_kpc" type="double precision" unit="kpc" ucd="stat.error;phys.size.radius" description="The upper limit rhi_kpc on in kpc"/>
      <column name="vhi_flag" type="integer" unit="" ucd="meta.code" description="A flag describing the quality of the vhi calculation"/>
      <column name="vhi" type="double precision" unit="km/s" ucd="phys.veloc.rotat" description="The rotation velocity at rhi"/>
      <column name="e_vhi" type="double precision" unit="km/s" ucd="phys.veloc.rotat" description="Statistical uncertainty of vhi"/>
      <column name="kflag" type="integer" unit="" ucd="meta.code.qual" description="A flag indicating the robustness of the kinematic model"/>
      <column name="kinver" type="text" unit="" description="The version of the software used to generate the kinematic model"/>
      <foreignKey source="detection_id" dest="id" inTable="detection"/>
   </table>

   <data id="import_wallaby_kinematics">
      <make table="kinematic_model"/>
      <make table="kinematic_model_3kidnas"/>
   </data>
