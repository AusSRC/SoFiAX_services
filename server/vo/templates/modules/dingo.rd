   <table id="detection_nearest_gama" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="detection_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <column name="cata_id" type="bigint" unit="" ucd="meta.id" required="True"/>
      <foreignKey source="detection_id" dest="id" inTable="detection"/>
   </table>

   <data id="import_dingo_gama">
      <make table="detection_nearest_gama"/>
   </data>
