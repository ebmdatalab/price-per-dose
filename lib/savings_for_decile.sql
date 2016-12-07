SELECT
  bnf.presentation,
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
      LEFT JOIN ebmdatalab.hscic.tariff t
        ON p.bnf_code = t.bnf_code
      WHERE
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
          actual_cost/quantity AS price_per_dose
        FROM
          ebmdatalab.hscic.prescribing AS p
        WHERE
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
  ORDER BY
    possible_savings DESC
    {{ limit }}
) savings
LEFT JOIN
  ebmdatalab.hscic.bnf bnf
ON
  bnf.presentation_code = savings.generic_presentation
ORDER BY
  savings.possible_savings DESC
