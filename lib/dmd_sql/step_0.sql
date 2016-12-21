DROP TABLE IF EXISTS dmd_product;
CREATE TABLE dmd_product (
  DMDID INTEGER PRIMARY KEY,
  BNF_CODE INTEGER,
  VPID INTEGER,
  DISPLAY_NAME TEXT,
  EMA TEXT,
  PRES_STATCD INTEGER,
  AVAIL_RESTRICTCD INTEGER,
  product_type INTEGER,
  NON_AVAILCO INTEGER,
  concept_class INTEGER,
  NURSE_F INTEGER,
  DENT_F INTEGER,
  PROD_ORDER_NO INTEGER,
  SCHED_1 INTEGER,
  SCHED_2 INTEGER,
  PADM INTEGER,
  FP10_MDA INTEGER,
  ACBS INTEGER,
  assort_flav INTEGER,
  CATCD INTEGER,
  tariff_category INTEGER
  );
