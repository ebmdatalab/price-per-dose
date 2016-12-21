from lxml import etree
import glob
import sqlite3


PRIMARY_KEYS = {
    'AMP': 'APID',
    'AMPP': 'APPID',
    'VMP': 'VPID',
    'VMPP': 'VPPID'
}

SQLLITE_TYPE_MAP = {
    'xs:date': 'TEXT',
    'xs:string': 'TEXT',
    'xs:integer': 'INTEGER',
    'xs:float': 'REAL',
}

def connection():
    return sqlite3.connect('dmd.db')


def create_table(conn, info):
    sql = "DROP TABLE IF EXISTS %s" % info['table_name']
    conn.execute(sql)
    conn.commit()
    sql = "CREATE TABLE %s (" % info['table_name']
    cols = []
    indexes = []
    for name, coltype in info['columns']:
        row_sql = "%s %s" % (name, coltype)
        if name == PRIMARY_KEYS.get(info['table_name'], ''):
            row_sql += " PRIMARY KEY"
        elif any([name in x for x in PRIMARY_KEYS.values()]):
            indexes.append(name)
        cols.append(row_sql)
    sql += ', '.join(cols)
    sql += ");"
    conn.execute(sql)
    for i in indexes:
        sql = "CREATE INDEX IF NOT EXISTS i_%s ON %s(%s);" % (i, info['table_name'], i)
        conn.execute(sql)
    conn.commit()


def insert_row(conn, table_info, row_data):
    sql = "INSERT INTO %s(%s) VALUES (%s)"
    table_name = table_info['table_name']
    cols = []
    vals = []
    for col, val in row_data:
        cols.append(col)
        vals.append(val)
    sql = sql % (table_name, ','.join(cols), ','.join('?' * len(vals)))
    conn.execute(sql, vals)


def get_table_info(conn, schema_names):
    all_tables = {}
    for schema_name in schema_names:
        xmlschema_doc = etree.parse("./files/%s" % schema_name)
        ns = {"xs": "http://www.w3.org/2001/XMLSchema"}
        root = xmlschema_doc.getroot()
        tables = root.findall(
            'xs:element/xs:complexType/xs:sequence/xs:element', ns)
        root_name = root.find('xs:element', ns).attrib['name']
        for table in tables:
            current_table_def = {'root': root_name}
            schema_name = None
            # does it contain references to other bits of schema?
            if len(root.findall('.//xs:all', ns)) > 0:
                current_table_def['long_name'] = table.attrib['name']
                table_metadata = table.find(
                    './xs:complexType/xs:sequence/xs:element', ns)
                schema_name = table_metadata.attrib['type']
                if schema_name == 'InfoType':  # special case for info
                    current_table_def['table_name'] = 'LOOKUP_' + table.attrib['name']
                    current_table_def['node_name'] = "%s/INFO" % table.attrib['name']
                else:
                    current_table_def['table_name'] = table_metadata.attrib['name']
                    current_table_def['node_name'] = table_metadata.attrib['name']

                columns = root.findall(
                    ".//xs:complexType[@name='%s']/xs:all/xs:element" %
                    schema_name, ns)
            else:
                current_table_def['long_name'] = None
                current_table_def['table_name'] = table.attrib['name']
                current_table_def['node_name'] = table.attrib['name']
                columns = table.findall('.//xs:element', ns)
            current_table_def['columns'] = []

            # Add column info to the current table definition
            for column in columns:
                col_name = column.attrib['name']
                col_type = column.attrib['type']
                current_table_def['columns'].append((col_name, SQLLITE_TYPE_MAP[col_type]))

            # Now, if it aleady exists having been described elsewhere,
            if current_table_def['table_name'] in all_tables:
                for new_col in current_table_def['columns']:
                    if new_col not in all_tables[current_table_def['table_name']]['columns']:
                        all_tables[current_table_def['table_name']]['columns'].append(new_col)
            else:
                all_tables[current_table_def['table_name']] = current_table_def
    return all_tables


def create_all_tables(conn):
    # We have to do them all at once because some schemas are split
    # over multiple files!
    files = [x.split('/')[-1] for x in glob.glob("./files/*xsd")]
    table_info = get_table_info(conn, files)
    for name, info in table_info.items():
        create_table(conn, info)


def create_dmd_product():
    import re
    conn = connection()
    for f in sorted(glob.glob("lib/dmd_sql/*sql"),
                    key=lambda x: int(re.findall(r'\d+', x)[0])):
        print "Post-processing", f
        with open(f, "rb") as sql:
            sql = sql.read()
            conn.executescript(sql)
            conn.commit()
    conn.close()


def add_bnf_codes():
    conn = connection()
    from openpyxl import load_workbook
    # 113.831 rows in the spreadsheet
    wb = load_workbook(filename='files/Converted_DRUG_SNOMED_BNF.xlsx')
    rows = wb.get_active_sheet().rows
    rows.next()  # header
    for row in rows:
        bnf_code = row[0].value
        # atc_code = row[1].value
        snomed_code = row[4].value
        sql = "UPDATE dmd_product SET BNF_CODE = ? WHERE DMDID = ? "
        success = conn.execute(sql, [bnf_code, snomed_code]).rowcount
        if not success:
            print "Could not find", snomed_code
    conn.commit()


def process_datafiles(to_process):
    conn = connection()
    create_all_tables(conn)

    for f in to_process:
        print "Processing %s" % f
        doc = etree.parse(f)
        root = doc.getroot()
        schema = root.attrib['{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation']
        table_info = get_table_info(conn, [schema])
        for table_name, info in table_info.items():
            rows = root.findall(".//%s" % info['node_name'])
            for row in rows:
                row_data = []
                for name, col_type in info['columns']:
                    val = row.find(name)
                    if val is not None:
                        val = val.text
                    row_data.append((name, val))
                insert_row(conn, info, row_data)
            conn.commit()
    conn.close()


if __name__ == '__main__2':
    import sys
    if len(sys.argv) > 1:
        to_process = [sys.argv[1]]
    else:
        to_process = glob.glob("./files/*xml")
    process_datafiles(to_process)
    create_dmd_product()
    add_bnf_codes()

if __name__ == '__main__':
    add_bnf_codes()
