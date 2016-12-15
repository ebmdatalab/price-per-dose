import pandas as pd


def get_savings(for_entity='', group_by='', month='', cost_field='net_cost',
                sql_only=False, limit=1000, order_by_savings=True):
    assert month
    assert group_by or for_entity
    assert group_by in ['', 'ccg', 'practice', 'product']
    restricting_condition = (
        "AND LENGTH(RTRIM(p.bnf_code)) >= 15 "
        "AND p.bnf_code NOT LIKE '1902%' -- 'Selective Preparations' \n")
    if len(for_entity) == 3:
        restricting_condition += 'AND pct = "%s"' % for_entity
        group_by = 'ccg'
    elif len(for_entity) > 3:
        restricting_condition += 'AND practice = "%s"' % for_entity
        group_by = 'practice'
    if limit:
        limit = "LIMIT %s" % limit
    else:
        limit = ''
    if group_by == 'ccg':
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


def top_savings_per_entity(top_n=3, entity='practice', month='2016-09-01'):
    assert entity in ['practice', 'pct']
    sql = get_savings(group_by=entity, sql_only=True,
                      limit=None, month=month, order_by_savings=False)
    numbered_savings = ("SELECT %s, possible_savings, ROW_NUMBER() OVER "
                        "(PARTITION BY %s ORDER BY possible_savings DESC) "
                        "AS row_number FROM (%s)" % (entity, entity, sql))
    grouped = ("SELECT %s, SUM(possible_savings) AS top_savings_sum "
               "FROM (%s) "
               "WHERE row_number <= %s"
               "GROUP BY %s ORDER BY %s" %
               (entity, numbered_savings, top_n, entity, entity))
    return run_gbq(grouped)


def all_presentations_in_per_entity_top_n(
        top_n=3, entity='practice', month='2016-09-01'):
    assert entity in ['practice', 'pct']
    sql = get_savings(group_by=entity, sql_only=True,
                      limit=None, month=month, order_by_savings=False)
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
               "ORDER BY presentation" %
               (numbered_savings, top_n))
    return run_gbq(grouped)


def cost_savings_at_minimum_for_practice(minimum, month='2016-09-01'):
    entity = 'practice'
    sql = get_savings(group_by=entity, sql_only=True,
                      limit=None, month=month, order_by_savings=False)
    grouped = ("SELECT bnf.presentation AS presentation, "
               "bnf.chemical AS chemical, generic_presentation, "
               "SUM(possible_savings) AS top_savings_sum "
               "FROM (%s) "
               "WHERE possible_savings >= %s"
               "GROUP BY presentation, generic_presentation, chemical "
               "ORDER BY presentation" %
               (sql, minimum))
    return run_gbq(grouped)
