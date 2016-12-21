REPLACE INTO dmd_product
 SELECT
   dmd_product.DMDID, dmd_product.BNF_CODE, dmd_product.VPID,
   dmd_product.DISPLAY_NAME, dmd_product.EMA, dmd_product.PRES_STATCD,
   dmd_product.AVAIL_RESTRICTCD, dmd_product.product_type, dmd_product.NON_AVAILCO,
   dmd_product.concept_class, dmd_product.NURSE_F, dmd_product.DENT_F,
   dmd_product.PROD_ORDER_NO, dmd_product.SCHED_1, dmd_product.SCHED_2,
   dmd_product.PADM, dmd_product.FP10_MDA, dmd_product.ACBS,
   dmd_product.assort_flav, CONTROL_INFO.CATCD, dmd_product.tariff_category
 FROM dmd_product
 INNER JOIN VMP
   ON VMP.VPID = dmd_product.VPID
 INNER JOIN CONTROL_INFO
   ON CONTROL_INFO.VPID = VMP.VPID
