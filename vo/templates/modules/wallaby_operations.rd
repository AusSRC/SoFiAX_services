   <table id="tile" onDisk="True" adql="True">
      <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True"/>
      <column name="name" type="text" unit="" ucd="meta.id" required="True"/>
      <column type="double precision" name="ra_deg" unit="deg" ucd="pos.eq.ra;meta.main" verbLevel="1"/>
      <column type="double precision" name="dec_deg" unit="deg" ucd="pos.eq.dec;meta.main" verbLevel="1"/>
      <column name="phase" type="text" unit="" ucd="meta.id" required="True"/>
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

   <data id="import_wallaby_operations">
      <make table="tile"/>
      <make table="source_extraction_region"/>
      <make table="source_extraction_region_tile"/>
      <make table="tile_obs"/>
   </data>
