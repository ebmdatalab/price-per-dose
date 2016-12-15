SELECT
  bnf.presentation,
  bnf.chemical,
  {{ select }}
  savings.generic_presentation AS generic_presentation,
  savings.category AS category,
  savings.brand_count AS brand_count,
  savings.deciles.lowest_decile AS lowest_decile,
  savings.quantity AS quantity,
  savings.price_per_dose AS price_per_dose,
  savings.possible_savings AS possible_savings
FROM (
  SELECT
    {{ inner_select }}
    presentations.generic_presentation AS generic_presentation,
    COUNT(DISTINCT bnf_code) AS brand_count,
    MAX(presentations.category) AS category,
    deciles.lowest_decile,
    SUM(presentations.quantity) AS quantity,
    SUM(presentations.{{ cost_field }})/SUM(presentations.quantity) AS price_per_dose,
    GREATEST((SUM(presentations.{{ cost_field }}) - (SUM(presentations.quantity) * deciles.lowest_decile)), 0) AS possible_savings
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
        {{ cost_field }},
        quantity
      FROM
        ebmdatalab.hscic.prescribing AS p
      LEFT JOIN ebmdatalab.hscic.tariff t
        ON p.bnf_code = t.bnf_code
      LEFT JOIN ebmdatalab.hscic.practices practices
        ON p.practice = practices.code
      WHERE
        practices.setting = 4 AND
        month = TIMESTAMP("{{ month }}")
        {{ restricting_condition }}
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
          {{ cost_field }}/quantity AS price_per_dose
        FROM
          ebmdatalab.hscic.prescribing AS p
        LEFT JOIN ebmdatalab.hscic.practices practices
          ON p.practice = practices.code
        WHERE
          practices.setting = 4 AND
          month = TIMESTAMP("{{ month }}")
          {{ restricting_condition }}
          ))
    GROUP BY
      generic_presentation) deciles
  ON
    deciles.generic_presentation = presentations.generic_presentation
  GROUP BY
    {{ group_by }}
    generic_presentation,
    deciles.lowest_decile
    {{ order_by }}
    {{ limit }}
) savings
LEFT JOIN
  ebmdatalab.hscic.bnf bnf
ON
  bnf.presentation_code = savings.generic_presentation
