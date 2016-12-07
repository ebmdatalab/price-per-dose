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

def top_savings_per_practice():
    sql = """
SELECT
  practice,
  MAX(first) + MAX(second) + MAX(third) AS top_savings_sum
FROM (
  SELECT
    practice,
    NTH_VALUE(possible_savings, 1) OVER (PARTITION BY practice ORDER BY possible_savings DESC ROWS BETWEEN UNBOUNDED PRECEDING AND 3 FOLLOWING) AS first,
    NTH_VALUE(possible_savings, 2) OVER (PARTITION BY practice ORDER BY possible_savings DESC ROWS BETWEEN UNBOUNDED PRECEDING AND 3 FOLLOWING) AS second,
    NTH_VALUE(possible_savings, 3) OVER (PARTITION BY practice ORDER BY possible_savings DESC ROWS BETWEEN UNBOUNDED PRECEDING AND 3 FOLLOWING) AS third
  FROM (
    SELECT
      bnf.presentation,
      savings.presentations.practice AS practice,
      savings.presentations.pct AS pct,
      savings.generic_presentation AS generic_presentation,
      savings.category AS category,
      savings.brand_count AS brand_count,
      savings.deciles.lowest_decile AS lowest_decile,
      savings.quantity AS quantity,
      savings.price_per_dose AS price_per_dose,
      savings.possible_savings AS possible_savings
    FROM (
      SELECT
        presentations.pct,
        presentations.practice,
        presentations.generic_presentation AS generic_presentation,
        COUNT(DISTINCT bnf_code) AS brand_count,
        MAX(presentations.category) AS category,
        deciles.lowest_decile,
        SUM(presentations.quantity) AS quantity,
        SUM(presentations.actual_cost)/SUM(presentations.quantity) AS price_per_dose,
        SUM(presentations.actual_cost) - (SUM(presentations.quantity) * deciles.lowest_decile) AS possible_savings
      FROM (
        SELECT
          *
        FROM (
            -- Create table for joining individual data
          SELECT
            practice,
            pct,
            p.bnf_code AS bnf_code,
            t.category AS category,
            IF(SUBSTR(p.bnf_code, 14, 15) != 'A0', CONCAT(SUBSTR(p.bnf_code, 1, 9), 'AA', SUBSTR(p.bnf_code, 14, 2), SUBSTR(p.bnf_code, 14, 2)), p.bnf_code) AS generic_presentation,
            actual_cost,
            quantity
          FROM
            ebmdatalab.hscic.prescribing AS p
          LEFT JOIN
            ebmdatalab.hscic.tariff t
          ON
            p.bnf_code = t.bnf_code
          WHERE
            month = TIMESTAMP("2016-09-01")
            AND LENGTH(RTRIM(p.bnf_code)) >= 15
            AND p.bnf_code NOT LIKE '1902%' -- 'Selective Preparations'
            ) ) presentations
      JOIN (
          -- Calculate the top decile of price per dose for each generic presentation
        SELECT
          generic_presentation,
          MAX(lowest_decile) AS lowest_decile
        FROM (
          SELECT
            generic_presentation,
            PERCENTILE_CONT(0.1) OVER (PARTITION BY generic_presentation ORDER BY price_per_dose ASC) AS lowest_decile
          FROM (
              -- Calculate price per dose for each presentation, normalising the codes across brands/generics
            SELECT
              IF(SUBSTR(bnf_code, 14, 15) != 'A0', CONCAT(SUBSTR(bnf_code, 1, 9), 'AA', SUBSTR(bnf_code, 14, 2), SUBSTR(bnf_code, 14, 2)), bnf_code) AS generic_presentation,
              actual_cost/quantity AS price_per_dose
            FROM
              ebmdatalab.hscic.prescribing AS p
            WHERE
              month = TIMESTAMP("2016-09-01")
              AND LENGTH(RTRIM(p.bnf_code)) >= 15
              AND p.bnf_code NOT LIKE '1902%' -- 'Selective Preparations'
              ))
        GROUP BY
          generic_presentation) deciles
      ON
        deciles.generic_presentation = presentations.generic_presentation
      GROUP BY
        presentations.practice,
        presentations.pct,
        generic_presentation,
        deciles.lowest_decile ) savings
    LEFT JOIN
      ebmdatalab.hscic.bnf bnf
    ON
      bnf.presentation_code = savings.generic_presentation ))
GROUP BY
  practice
ORDER BY
  practice"""
    df = pd.io.gbq.read_gbq(
        sql, project_id="ebmdatalab", verbose=False, dialect='legacy')
    return df
