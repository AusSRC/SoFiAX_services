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

   <data id="import_metadata">
      <make table="comment"/>
      <make table="tag"/>
      <make table="tag_detection"/>
   </data>
