REPLACE INTO dmd_product
 SELECT
   dmd_product.DMDID, dmd_product.BNF_CODE, dmd_product.VPID,
   dmd_product.DISPLAY_NAME, dmd_product.EMA, dmd_product.PRES_STATCD,
   dmd_product.AVAIL_RESTRICTCD, dmd_product.product_type, dmd_product.NON_AVAILCO,
   dmd_product.concept_class, dmd_product.NURSE_F, dmd_product.DENT_F,
   dmd_product.PROD_ORDER_NO, dmd_product.SCHED_1, dmd_product.SCHED_2,
   dmd_product.PADM, dmd_product.FP10_MDA, dmd_product.ACBS,
   dmd_product.assort_flav, dmd_product.CATCD, DTINFO.PAY_CATCD
 FROM dmd_product
 INNER JOIN VMPP
   ON dmd_product.VPID = VMPP.VPID
 INNER JOIN DTINFO
   ON VMPP.VPPID = DTINFO.VPPID
