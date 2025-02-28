<resource schema="wallaby">
   <meta name="title">ASKAP Survey</meta>
    <meta name="creationDate">2023-06-06T12:00:00Z</meta>
    <meta name="description">ASKAP Survey</meta>
    <meta name="copyright" format="plain"></meta>
    <meta name="_dataUpdated">2024-11-28T12:00:00Z</meta>

   <table id="run" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id"/>

      <meta name="_associatedDatalinkService">
         <meta name="serviceId">run_dl</meta>
         <meta name="idColumn">id</meta>
      </meta>
   </table>

   <table id="instance" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="run_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="filename" type="text" unit="" ucd="meta.id"/>
      <column name="run_date" type="timestamp" unit="" ucd="meta.id"/>
      <column name="version" type="text" unit="" ucd="meta.id"/>
      <foreignKey source="run_id" dest="id" inTable="run"/>
   </table>

   <table id="detection" onDisk="True" adql="True">
      <index columns="id"/>

      <meta name="_associatedDatalinkService">
         <meta name="serviceId">dl</meta>
         <meta name="idColumn">id</meta>
      </meta>

      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True" verbLevel="1"/>
      <column name="name" type="text" unit="" ucd="meta.id"/>
      <column name="run_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="instance_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="access_url" type="text"  ucd="meta.ref.url;meta.data.datalink" tablehead="Datalink" verbLevel="15" displayHint="type=url"/>
      <column name="access_format" type="text"  ucd="meta.code.mime"/>
      <column name="source_name" type="text" unit="" ucd="meta.id" description="WALLABY source name (WALLABY Jhhmmss+/-ddmmss)"/>
      <column type="double precision" name="x" unit="pix" ucd="pos.cartesian.x" description="Centroid position in x"/>
      <column type="double precision" name="y" unit="pix" ucd="pos.cartesian.y" description="Centroid position in y"/>
      <column type="double precision" name="z" unit="pix" ucd="pos.cartesian.z" description="Centroid position in z"/>
      <column type="double precision" name="x_min" unit="pix" ucd="pos.cartesian.x;stat.min" description="Lower end of bounding box in x"/>
      <column type="double precision" name="x_max" unit="pix" ucd="pos.cartesian.x;stat.max" description="Upper end of bounding box in x"/>
      <column type="double precision" name="y_min" unit="pix" ucd="pos.cartesian.y;stat.min" description="Lower end of bounding box in y"/>
      <column type="double precision" name="y_max" unit="pix" ucd="pos.cartesian.y;stat.max" description="Upper end of bounding box in y"/>
      <column type="double precision" name="z_min" unit="pix" ucd="pos.cartesian.z;stat.min" description="Lower end of bounding box in z"/>
      <column type="double precision" name="z_max" unit="pix" ucd="pos.cartesian.z;stat.max" description="Upper end of bounding box in z"/>
      <column type="double precision" name="n_pix" unit="" ucd="meta.number;instr.pixel" description="Number of pixels in 3D source mask"/>
      <column type="double precision" name="f_min" unit="Jy/beam" ucd="phot.flux.density;stat.min" description="Lowest flux density value within 3D source mask"/>
      <column type="double precision" name="f_max" unit="Jy/beam" ucd="phot.flux.density;stat.max" description="Highest flux density value within 3D source mask"/>
      <column type="double precision" name="f_sum" unit="Jy*Hz" ucd="phot.flux;meta.main" description="Integrated flux within 3D source mask"/>
      <column type="double precision" name="rel" unit="" ucd="stat.probability" description="Statistical reliability of detection from 0 to 1"/>
      <column type="integer" name="flag" unit="" ucd="meta.code.qual" required="True"/>
      <column type="double precision" name="rms" unit="Jy/beam" ucd="instr.det.noise" description="Local RMS noise level near source"/>
      <column type="double precision" name="w20" unit="Hz" ucd="spect.line.width;meta.main" description="Spectral line width at 20% of the peak (w20)"/>
      <column type="double precision" name="w50" unit="Hz" ucd="spect.line.width;meta.main" description="Spectral line width at 50% of the peak (w50)"/>
      <column type="double precision" name="ell_maj" unit="pix" ucd="phys.angSize.smajAxis" description="Major axis size of ellipse fitted to moment 0 map"/>
      <column type="double precision" name="ell_min" unit="pix" ucd="phys.angSize.sminAxis" description="Minor axis size of ellipse fitted to moment 0 map"/>
      <column type="double precision" name="ell_pa" unit="deg" ucd="pos.posAng" description="Position angle of ellipse fitted to moment 0 map"/>
      <column type="double precision" name="ell3s_maj" unit="pix" ucd="phys.angSize.smajAxis" description="Same as ell maj but &gt; 3 sigma pixels only and equal weight"/>
      <column type="double precision" name="ell3s_min" unit="pix" ucd="phys.angSize.sminAxis" description="Same as ell min but &gt; 3 sigma pixels only and equal weight"/>
      <column type="double precision" name="ell3s_pa" unit="deg" ucd="pos.posAng" description="Same as ell pa but &gt; 3 sigma pixels only and equal weight"/>
      <column type="double precision" name="kin_pa" unit="deg" ucd="pos.posAng" description="Position angle of kinematic major axis"/>
      <column type="double precision" name="err_x" unit="pix" ucd="stat.error;pos.cartesian.x" description="Statistical uncertainty of centroid position"/>
      <column type="double precision" name="err_y" unit="pix" ucd="stat.error;pos.cartesian.y" description="Statistical uncertainty of centroid position"/>
      <column type="double precision" name="err_z" unit="pix" ucd="stat.error;pos.cartesian.z" description="Statistical uncertainty of centroid position"/>
      <column type="double precision" name="err_f_sum" unit="Jy*Hz" ucd="stat.error;phot.flux" description="Statistical uncertainty of integrated flux"/>
      <column type="double precision" name="ra" unit="deg" ucd="pos.eq.ra;meta.main" description="Right ascension (J2000) of centroid position" verbLevel="1"/>
      <column type="double precision" name="dec" unit="deg" ucd="pos.eq.dec;meta.main" description="Declination (J2000) of centroid position" verbLevel="1"/>
      <column type="double precision" name="freq" unit="Hz" ucd="em.freq;meta.main" description="Barycentric frequency of centroid position"/>
      <column type="double precision" name="l" unit="deg" ucd="pos.galactic.lon"/>
      <column type="double precision" name="b" unit="deg" ucd="pos.galactic.lat"/>
      <column type="double precision" name="v_rad" unit="m/s" ucd="spect.dopplerVeloc.radio"/>
      <column type="double precision" name="v_opt" unit="m/s" ucd="spect.dopplerVeloc.opt"/>
      <column type="double precision" name="v_app" unit="m/s" ucd="spect.dopplerVeloc"/>
      <foreignKey source="run_id" dest="id" inTable="run"/>
      <foreignKey source="instance_id" dest="id" inTable="instance"/>

   </table>

   <service id="run_dl" allowed="dlget,dlmeta">
      <meta name="title">Run Datalink</meta>
      <meta name="dlget.description">Run Datalink</meta>
		<datalinkCore>
           <descriptorGenerator>
            <setup>
              <code>
                 class CustomDescriptor(ProductDescriptor):
                     def __init__(self, id):
                        super(ProductDescriptor, self).__init__()
                        self.pubDID = id
                        self.mime = ""
                        self.accref = ""
                        self.accessPath = ""
                        self.access_url = ""
                        self.suppressAutoLinks = True
                 </code>
             </setup>
            <code>
               return CustomDescriptor(pubDID)
            </code>
          </descriptorGenerator>

           <metaMaker>
              <code>
                  import os
                  from urllib.parse import urlencode

                  server_url = os.environ.get('PRODUCT_URL', "http://localhost:8080")

                  params = {"id": descriptor.pubDID}
                  url = "{1}/catalog?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="text/xml", description="Run Catalog", semantics="#preview")

                  params = {"id": descriptor.pubDID}
                  url = "{1}/run_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="application/x-tar", description="Run Products", semantics="#preview")

              </code>
           </metaMaker>

            <dataFunction>
               <setup>
                  <code>
                     from gavo.svcs import WebRedirect
                  </code>
               </setup>
               <code>
                  import os
                  server_url = os.environ.get('PRODUCT_URL', "http://localhost:8080")
                  url = "{1}/catalog?id={0}".format(descriptor.pubDID, server_url)
                  raise WebRedirect(url)
               </code>
            </dataFunction>

		</datalinkCore>

	</service>


	<service id="dl" allowed="dlget,dlmeta">
		<meta name="title">Detections Datalink</meta>
        <meta name="dlget.description">Detections Datalink</meta>
		<datalinkCore>
           <descriptorGenerator>
            <setup>
              <code>
                 class CustomDescriptor(ProductDescriptor):
                     def __init__(self, id):
                        super(ProductDescriptor, self).__init__()
                        self.pubDID = id
                        self.mime = ""
                        self.accref = ""
                        self.accessPath = ""
                        self.access_url = ""
                        self.suppressAutoLinks = True
                 </code>
             </setup>
            <code>
               return CustomDescriptor(pubDID)
            </code>
          </descriptorGenerator>

           <metaMaker>
              <code>
                  import os
                  from urllib.parse import urlencode

                  server_url = os.environ.get('PRODUCT_URL', "http://localhost:8080")

                  params = {"id": descriptor.pubDID, "product": "cube"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="image/fits", description="SoFiA-2 Detection Cube", semantics="#preview")

                  params = {"id": descriptor.pubDID, "product": "mom0"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="image/fits", description="SoFiA-2 Detection Moment0", semantics="#preview")

                  params = {"id": descriptor.pubDID, "product": "mom1"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="image/fits", description="SoFiA-2 Detection Moment1", semantics="#preview")

                  params = {"id": descriptor.pubDID, "product": "mom2"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="image/fits", description="SoFiA-2 Detection Moment2", semantics="#preview")

                  params = {"id": descriptor.pubDID, "product": "mask"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="image/fits", description="SoFiA-2 Detection Mask", semantics="#auxiliary")

                  params = {"id": descriptor.pubDID, "product": "chan"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="image/fits", description="SoFiA-2 Detection Channels", semantics="#auxiliary")

                  params = {"id": descriptor.pubDID, "product": "spec"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="text/plain", description="SoFiA-2 Detection Spectrum", semantics="#auxiliary")

                  params = {"id": descriptor.pubDID, "product": "plot"}
                  url = "{1}/detection_products?{0}".format(urlencode(params), server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="text/plain", description="SoFiA-2 Detection Summary Plot", semantics="#auxiliary")

                  url = "{1}/detection_products?id={0}".format(descriptor.pubDID, server_url)
                  yield LinkDef(descriptor.pubDID, url, contentType="application/x-tar", description="SoFiA-2 Detection Products", semantics="#this")
              </code>
           </metaMaker>

            <dataFunction>
               <setup>
                  <code>
                     from gavo.svcs import WebRedirect
                  </code>
               </setup>
               <code>
                  import os
                  server_url = os.environ.get('PRODUCT_URL', "http://localhost:8080")
                  url = "{1}/detection_products?id={0}".format(descriptor.pubDID, server_url)
                  raise WebRedirect(url)
               </code>
            </dataFunction>

		</datalinkCore>

	</service>

   <table id="comment" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="comment" type="text" unit="" ucd="meta.id"/>
      <column name="author" type="text" unit="" ucd="meta.id"/>
      <column name="detection_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="updated_at" type="timestamp" unit="" ucd="meta.id"/>
      <foreignKey source="detection_id" dest="id" inTable="detection"/>
   </table>


   <table id="tag" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id"/>
      <column name="description" type="text" unit="" ucd="meta.id"/>
      <column name="added_at" type="timestamp" unit="" ucd="meta.id"/>
   </table>


   <table id="tag_detection" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="tag_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="detection_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="author" type="text" unit="" ucd="meta.id"/>
      <column name="added_at" type="timestamp" unit="" ucd="meta.id"/>
      <foreignKey source="tag_id" dest="id" inTable="tag"/>
      <foreignKey source="detection_id" dest="id" inTable="detection"/>
   </table>


   <table id="tile" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id" required="True"/>
      <column type="double precision" name="ra_deg" unit="deg" ucd="pos.eq.ra;meta.main" verbLevel="1"/>
      <column type="double precision" name="dec_deg" unit="deg" ucd="pos.eq.dec;meta.main" verbLevel="1"/>
      <column name="phase" type="text" unit="" ucd="meta.id" required="True"/>
   </table>


   <table id="observation" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id" required="True"/>
      <column name="sbid" type="text" unit="" ucd="meta.id"/>
      <column type="double precision" name="ra" unit="deg" ucd="pos.eq.ra;meta.main" verbLevel="1"/>
      <column type="double precision" name="dec" unit="deg" ucd="pos.eq.dec;meta.main" verbLevel="1"/>
      <column type="double precision" name="rotation" unit="deg" ucd="pos.eq.dec;meta.main" verbLevel="1"/>
      <column name="description" type="text" unit="" ucd="meta.id"/>
      <column name="phase" type="text" unit="" ucd="meta.id"/>
      <column name="image_cube_file" type="text" unit="" ucd="meta.id"/>
      <column name="weights_cube_file" type="text" unit="" ucd="meta.id"/>
      <column name="quality" type="text" unit="" ucd="meta.id"/>
      <column name="status" type="text" unit="" ucd="meta.id"/>
   </table>


   <table id="source_extraction_region" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id" required="True"/>
      <column type="double precision" name="ra_deg" unit="deg" ucd="pos.eq.ra;meta.main" verbLevel="1"/>
      <column type="double precision" name="dec_deg" unit="deg" ucd="pos.eq.dec;meta.main" verbLevel="1"/>
      <column name="status" type="text" unit="" ucd="meta.id"/>
      <column name="complete" ucd="meta.code" type="boolean"/>
   </table>


   <table id="source_extraction_region_tile" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="ser_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="tile_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <foreignKey source="ser_id" dest="id" inTable="source_extraction_region"/>
      <foreignKey source="tile_id" dest="id" inTable="tile"/>
   </table>


   <table id="tile_obs" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="tile_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="obs_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <foreignKey source="obs_id" dest="id" inTable="observation"/>
      <foreignKey source="tile_id" dest="id" inTable="tile"/>
   </table>


   <table id="kinematic_model" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id"//>
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
      <column name="ra_model" type="double precision" unit="deg" ucd= description="Kinematically modelled center position in Right ascension (J2000)"/>
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
      <column name="kinver" type="text" unit="" ucd= description="The version of the software used to generate the kinematic model"/>
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
      <column name="ra_model" type="double precision" unit="deg" ucd= description="Kinematically modelled center position in Right ascension (J2000)"/>
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
      <column name="kinver" type="text" unit="" ucd= description="The version of the software used to generate the kinematic model"/>
      <foreignKey source="detection_id" dest="id" inTable="detection"/>
   </table>


   <data id="import">
      <make table="run"/>
      <make table="instance"/>
      <make table="detection"/>
      <make table="comment"/>
      <make table="tag"/>
      <make table="tag_detection"/>
      <make table="observation"/>
      <make table="tile"/>
      <make table="source_extraction_region"/>
      <make table="source_extraction_region_tile"/>
      <make table="tile_obs"/>
      <make table="kinematic_model"/>
      <make table="kinematic_model_3kidnas"/>
   </data>

</resource>
