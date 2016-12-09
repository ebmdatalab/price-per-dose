import pandas as pd


def get_savings(for_entity='', group_by='', month='',
                sql_only=False, limit=1000, order_by_savings=True):
    assert month
    assert group_by or for_entity
    assert group_by in ['', 'ccg', 'practice']
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
            print "%s: %s" % (n, line)
        raise


def top_savings_per_practice(top_n=3):
    sql = get_savings(group_by='practice', sql_only=True,
                      limit=None, month='2016-09-01', order_by_savings=False)
    sql_top = "SELECT practice, "
    select_sum = []
    select_partition = []
    for n in range(0, top_n):
        select_sum.append("COALESCE(MAX(top_%s), 0)" % n)
        select_partition.append(
            "NTH_VALUE(possible_savings, %s) "
            "OVER (PARTITION BY practice ORDER BY possible_savings DESC "
            "ROWS BETWEEN UNBOUNDED PRECEDING AND %s FOLLOWING) "
            "AS top_%s" % (n+1, top_n, n))
    sql_top += " + ".join(select_sum) + "AS top_savings_sum"
    sql = ("%s FROM (SELECT practice, %s FROM (%s)) "
           "GROUP BY practice ORDER BY practice" % (
               sql_top, ", ".join(select_partition), sql))
    return run_gbq(sql)
