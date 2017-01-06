import datetime
import time
import json
import pandas as pd
import peakutils
import numpy
import csv
import requests
from sets import Set

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def make_table_for_month(month='2016-09-01',
                         namespace='hscic',
                         prescribing_table='prescribing'):
    url = ("https://docs.google.com/spreadsheets/d/"
           "1SvMGCKrmqsNkZYuGW18Sf0wTluXyV4bhyZQaVLcO41c/"
           "pub?gid=1784930737&single=true&output=csv")
    cases = []
    seen = Set()

    with requests.Session() as s:
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        cr.next()
        for row in cr:
            should_merge = row[5].strip() == "Y"
            if should_merge:
                source_code = row[1].strip()
                code_to_merge = row[8].strip()
                if source_code not in seen and code_to_merge not in seen:
                    cases.append((source_code, code_to_merge))
                seen.add(source_code)
                seen.add(code_to_merge)

    query = """
      SELECT
        practice,
        pct,
      CASE bnf_code
        %s
        ELSE bnf_code
      END AS bnf_code,
        month,
        actual_cost,
        net_cost,
        quantity
      FROM
        ebmdatalab.%s.%s
      WHERE month = TIMESTAMP('%s')
    """ % (''.join(["WHEN '%s' THEN '%s'" % (code_to_merge, source_code)
            for (source_code, code_to_merge) in cases]),
           namespace,
           prescribing_table,
           month)
    target_table_name = 'prescribing_%s' % month.replace('-', '_')
    query_and_return('ebmdatalab', namespace,
                     target_table_name,
                     query, legacy=False)
    return target_table_name


def get_savings(for_entity='', group_by='', month='', cost_field='net_cost',
                sql_only=False, limit=1000, order_by_savings=True,
                namespace='hscic', prescribing_table='prescribing'):
    assert month
    assert group_by or for_entity
    assert group_by in ['', 'pct', 'practice', 'product']
    prescribing_table = 'ebmdatalab.hscic.prescribing_2016_09_01'
    # prescribing_table = "ebmdatalab.%s.%s" % (
    #     namespace,
    #     make_table_for_month(
    #         month=month,
    #         namespace=namespace,
    #         prescribing_table=prescribing_table
    #     )
    # )
    restricting_condition = (
        "AND LENGTH(RTRIM(p.bnf_code)) >= 15 "
        "AND p.bnf_code NOT LIKE '0302000C0____BE' "  # issue #10
        "AND p.bnf_code NOT LIKE '0302000C0____BF' "  # issue #10
        "AND p.bnf_code NOT LIKE '0302000C0____BH' "  # issue #10
        "AND p.bnf_code NOT LIKE '0302000C0____BG' "  # issue #10
        "AND p.bnf_code NOT LIKE '0904010H0%' "  # issue #9
        "AND p.bnf_code NOT LIKE '0904010H0%' "  # issue #9
        "AND p.bnf_code NOT LIKE '1311070S0A____AA' "  # issue #9
        "AND p.bnf_code NOT LIKE '1311020L0____BS' "  # issue #9
        "AND p.bnf_code NOT LIKE '0301020S0____AA' "  # issue #12
        "AND p.bnf_code NOT LIKE '190700000BBCJA0' "  # issue #12
        "AND p.bnf_code NOT LIKE '0604011L0BGAAAH' "  # issue #12
        "AND p.bnf_code NOT LIKE '1502010J0____BY' "  # issue #12
        "AND p.bnf_code NOT LIKE '1201010F0AAAAAA' "  # issue #12
        "AND p.bnf_code NOT LIKE '060106000BBAAA0' "  # issue #14
        "AND p.bnf_code NOT LIKE '190201000AABJBJ' "  # issue #14
        "AND p.bnf_code NOT LIKE '190201000AABKBK' "  # issue #14
        "AND p.bnf_code NOT LIKE '190201000AABLBL' "  # issue #14
        "AND p.bnf_code NOT LIKE '190201000AABMBM' "  # issue #14
        "AND p.bnf_code NOT LIKE '190201000AABNBN' "  # issue #14
        "AND p.bnf_code NOT LIKE '190202000AAADAD' "  # issue #14
    )
    if len(for_entity) == 3:
        restricting_condition += 'AND pct = "%s"' % for_entity
        group_by = 'pct'
    elif len(for_entity) > 3:
        restricting_condition += 'AND practice = "%s"' % for_entity
        group_by = 'practice'
    if limit:
        limit = "LIMIT %s" % limit
    else:
        limit = ''
    if group_by == 'pct':
        select = 'savings.presentations.pct AS pct,'
        inner_select = 'presentations.pct, '
        group_by = 'presentations.pct, '
    elif group_by == 'practice':
        select = ('savings.presentations.practice AS practice,'
                  'savings.presentations.pct AS pct,')
        inner_select = ('presentations.pct, '
                        'presentations.practice,')
        group_by = ('presentations.practice, '
                    'presentations.pct,')
    elif group_by == 'product':
        select = ''
        inner_select = ''
        group_by = ''

    if order_by_savings:
        order_by = "ORDER BY possible_savings DESC"
    else:
        order_by = ''

    with open("./lib/savings_for_decile.sql", "r") as f:
        sql = f.read()
        substitutions = (
            ('{{ restricting_condition }}', restricting_condition),
            ('{{ limit }}', limit),
            ('{{ month }}', month),
            ('{{ group_by }}', group_by),
            ('{{ order_by }}', order_by),
            ('{{ select }}', select),
            ('{{ prescribing_table }}', prescribing_table),
            ('{{ cost_field }}', cost_field),
            ('{{ inner_select }}', inner_select)
        )
        for key, value in substitutions:
            sql = sql.replace(key, value)
        if sql_only:
            return sql
        else:
            df = run_gbq(sql)
            # Rename null values in category, so we can group by it
            df.loc[df['category'].isnull(), 'category'] = 'NP8'
            return df


def run_gbq(sql):
    try:
        df = pd.io.gbq.read_gbq(
            sql,
            project_id="ebmdatalab",
            verbose=False,
            dialect='legacy')
        return df
    except:
        for n, line in enumerate(sql.split("\n")):
            print "%s: %s" % (n+1, line)
        raise


def top_savings_per_entity(top_n=3,
                           entity='practice',
                           month='2016-09-01',
                           namespace='hscic',
                           prescribing_table='prescribing',
                           summed=True):
    assert entity in ['practice', 'pct']
    sql = get_savings(group_by=entity, sql_only=True, namespace=namespace,
                      prescribing_table=prescribing_table,
                      limit=None, month=month, order_by_savings=False)
    numbered_savings = ("SELECT %s, possible_savings, ROW_NUMBER() OVER "
                        "(PARTITION BY %s ORDER BY possible_savings DESC) "
                        "AS row_number FROM (%s)" % (entity, entity, sql))
    if summed:
        grouped = ("SELECT %s, SUM(possible_savings) AS top_savings_sum "
                   "FROM (%s) "
                   "WHERE row_number <= %s "
                   "GROUP BY %s ORDER BY %s" %
                   (entity, numbered_savings, top_n, entity, entity))
    else:
        grouped = ("SELECT * "
                   "FROM (%s) "
                   "WHERE row_number <= %s""" %
                   (numbered_savings,  top_n))
    return run_gbq(grouped)


def all_presentations_in_per_entity_top_n(
        top_n=3,
        entity='practice',
        month='2016-09-01',
        namespace='hscic',
        prescribing_table='prescribing'):
    assert entity in ['practice', 'pct']
    sql = get_savings(group_by=entity, sql_only=True,
                      limit=None, month=month, order_by_savings=False,
                      namespace=namespace, prescribing_table=prescribing_table)
    numbered_savings = ("SELECT %s, possible_savings, bnf.presentation, "
                        "bnf.chemical, generic_presentation, "
                        "ROW_NUMBER() OVER "
                        "  (PARTITION BY %s ORDER BY possible_savings DESC) "
                        "AS row_number FROM (%s)" % (entity, entity, sql))
    grouped = ("SELECT presentation, chemical, generic_presentation, "
               "SUM(possible_savings) AS top_savings_sum "
               "FROM (%s) "
               "WHERE row_number <= %s"
               "GROUP BY presentation, generic_presentation, chemical "
               "ORDER BY top_savings_sum DESC" %
               (numbered_savings, top_n))
    return run_gbq(grouped)


def cost_savings_at_minimum_for_practice(
        minimum,
        month='2016-09-01',
        namespace='hscic',
        prescribing_table='prescribing'):
    entity = 'practice'
    sql = get_savings(group_by=entity, sql_only=True,
                      limit=None, month=month, order_by_savings=False,
                      namespace=namespace, prescribing_table=prescribing_table)
    grouped = ("SELECT bnf.presentation AS presentation, "
               "bnf.chemical AS chemical, generic_presentation, "
               "SUM(possible_savings) AS top_savings_sum "
               "FROM (%s) "
               "WHERE possible_savings >= %s "
               "GROUP BY presentation, generic_presentation, chemical "
               "ORDER BY top_savings_sum DESC" %
               (sql, minimum))
    return run_gbq(grouped)


def count_peaks(code):
    sql = """  SELECT
        *
      FROM
        ebmdatalab.tmp_eu.prescribing_sept
      WHERE
        bnf_code = '%s'""" % code
    df = pd.io.gbq.read_gbq(
        sql, project_id="ebmdatalab", verbose=False, dialect='standard')
    df['ppq'] = df['actual_cost'] / df['quantity']
    df = df.sort_values('ppq')
    max_val = df['ppq'].max() * 1.5
    if numpy.isfinite(max_val):
        y, bin_edges = numpy.histogram(
            df['ppq'], range=(-5, max_val))
        return len(peakutils.indexes(y, thres=0.01, min_dist=len(y)/3.0))
    else:
        return None


def get_bq_service():
    """Returns a bigquery service endpoint
    """
    # We've started using the google-cloud library since first writing
    # this. When it settles down a bit, start using that rather than
    # this low-level API. See
    # https://googlecloudplatform.github.io/google-cloud-python/
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('bigquery', 'v2',
                           credentials=credentials)


def query_and_return(project_id, dataset_id, table_id, query, legacy=False):
    """Send query to BigQuery, wait, write it to table_id, and return
    response object when the job has completed.

    """
    payload = {
        "configuration": {
            "query": {
                "query": query,
                "flattenResuts": False,
                "allowLargeResults": True,
                "timeoutMs": 100000,
                "useQueryCache": True,
                "useLegacySql": legacy,
                "destinationTable": {
                    "projectId": project_id,
                    "tableId": table_id,
                    "datasetId": dataset_id
                },
                "createDisposition": "CREATE_IF_NEEDED",
                "writeDisposition": "WRITE_TRUNCATE"
            }
        }
    }
    # We've started using the google-cloud library since first
    # writing this. TODO: decide if we can use that throughout
    bq = get_bq_service()
    start = datetime.datetime.now()
    response = bq.jobs().insert(
        projectId=project_id,
        body=payload).execute()
    counter = 0
    job_id = response['jobReference']['jobId']
    while True:
        time.sleep(1)
        response = bq.jobs().get(
            projectId=project_id,
            jobId=job_id).execute()
        counter += 1
        if response['status']['state'] == 'DONE':
            if 'errors' in response['status']:
                query = str(response['configuration']['query']['query'])
                for i, l in enumerate(query.split("\n")):
                    # print SQL query with line numbers for debugging
                    print "{:>3}: {}".format(i + 1, l)
                raise StandardError(
                    json.dumps(response['status']['errors'], indent=2))
            else:
                break
    bytes_billed = float(
        response['statistics']['query']['totalBytesBilled'])
    gb_processed = round(bytes_billed / 1024 / 1024 / 1024, 2)
    est_cost = round(bytes_billed / 1e+12 * 5.0, 2)
    # Add our own metadata
    elapsed = (datetime.datetime.now() - start).total_seconds()
    response['openp'] = {'query': query,
                         'est_cost': est_cost,
                         'time': elapsed,
                         'gb_processed': gb_processed}
    return response
