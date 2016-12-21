UPDATE dmd_product
SET AVAIL_RESTRICTCD = 1
WHERE DMDID IN (
  SELECT DMDID
  FROM dmd_product
  INNER JOIN AMP
  ON AMP.VPID = DMDID
  WHERE AMP.AVAIL_RESTRICTCD = 1
);


REPLACE INTO dmd_product
 SELECT
   dmd_product.DMDID, dmd_product.BNF_CODE, dmd_product.VPID,
   dmd_product.DISPLAY_NAME, dmd_product.EMA, dmd_product.PRES_STATCD,
   AMP.AVAIL_RESTRICTCD, dmd_product.product_type, dmd_product.NON_AVAILCO,
   dmd_product.concept_class, dmd_product.NURSE_F, dmd_product.DENT_F,
   dmd_product.PROD_ORDER_NO, dmd_product.SCHED_1, dmd_product.SCHED_2,
   dmd_product.PADM, dmd_product.FP10_MDA, dmd_product.ACBS,
   dmd_product.assort_flav, dmd_product.CATCD, dmd_product.tariff_category
 FROM dmd_product
 INNER JOIN AMP
   ON AMP.VPID = DMDID
  WHERE AMP.AVAIL_RESTRICTCD != 1
  AND AMP.AVAIL_RESTRICTCD != 9
  AND dmd_product.AVAIL_RESTRICTCD IS NULL;


UPDATE dmd_product
SET AVAIL_RESTRICTCD = 9
WHERE DMDID IN (
  SELECT DMDID
  FROM dmd_product
  WHERE dmd_product.AVAIL_RESTRICTCD IS NULL
);
