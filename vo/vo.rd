<resource schema="dingo">
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


   <table id="detection_nearest_gama" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="detection_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="cata_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <foreignKey source="detection_id" dest="id" inTable="detection"/>
   </table>


   <data id="import">
      <make table="run"/>
      <make table="instance"/>
      <make table="detection"/>
      <make table="comment"/>
      <make table="tag"/>
      <make table="tag_detection"/>
      <make table="detection_nearest_gama"/>
   </data>

</resource>
