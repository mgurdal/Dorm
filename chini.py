from main import Node
from drivers import Sqlite
n1 = Node(ip="0.0.0.0", port=0, name='mysqlite', user='sky', password='123', type_='sqlite')
sq1 = Sqlite(name='test-2.3.sqlite')
n1.bind(sq1)

n2 = Node(ip="0.0.0.0", port=0, name='mysqlite2', user='sky', password='123', type_='sqlite')
sq2 = Sqlite(name='test-network-2.3.sqlite')
n2.bind(sq2)


SELECT c.relname as "Name"
FROM pg_catalog.pg_class c
     LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r','v','m','S','f','')
      AND n.nspname <> 'pg_catalog'
      AND n.nspname <> 'information_schema'
      AND n.nspname !~ '^pg_toast'
  AND pg_catalog.pg_table_is_visible(c.oid)
  AND c.relkind='r'
  AND pg_catalog.pg_get_userbyid(c.relowner)='docker';



SELECT
    c.relname,
    tc.constraint_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    pg_catalog.pg_class as c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace,
    information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
    WHERE c.relkind IN ('r','v','m','S','f','')
          AND n.nspname <> 'pg_catalog'
          AND n.nspname <> 'information_schema'
          AND n.nspname !~ '^pg_toast'
      AND pg_catalog.pg_table_is_visible(c.oid)
      AND c.relkind='r'
      AND pg_catalog.pg_get_userbyid(c.relowner)='docker'
      AND tc.table_name='trs_users';
