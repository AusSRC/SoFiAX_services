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

   <data id="import_operations">
      <make table="observation"/>
   </data>
