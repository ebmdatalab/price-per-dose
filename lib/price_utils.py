import pandas as pd


def get_savings(for_entity='', group_by='', month=''):
    assert month
    assert group_by or for_entity
    assert group_by in ['', 'ccg', 'practice']
    restricting_condition = (
        "AND LENGTH(RTRIM(p.bnf_code)) >= 15 "
        "AND p.bnf_code NOT LIKE '1902%' -- 'Selective Preparations' \n")
    limit = ''
    if len(for_entity) == 3:
        restricting_condition += 'AND pct = "%s"' % for_entity
        group_by = 'ccg'
    elif len(for_entity) > 3:
        restricting_condition += 'AND practice = "%s"' % for_entity
        group_by = 'practice'
    else:
        group_by = 'practice'
        limit = 'LIMIT 1000'
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
    with open("./lib/savings_for_decile.sql", "r") as f:
        sql = f.read()
        substitutions = (
            ('{{ restricting_condition }}', restricting_condition),
            ('{{ limit }}', limit),
            ('{{ month }}', month),
            ('{{ group_by }}', group_by),
            ('{{ select }}', select),
            ('{{ inner_select }}', inner_select)
        )
        for key, value in substitutions:
            sql = sql.replace(key, value)
        try:
            df = pd.io.gbq.read_gbq(
                sql, project_id="ebmdatalab", verbose=False, dialect='legacy')
            # Rename null values in category, so we can group by it
            df.loc[df['category'].isnull(), 'category'] = 'NP8'
            return df
        except:
            print sql
            raise
