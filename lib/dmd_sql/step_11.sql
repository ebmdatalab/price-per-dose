UPDATE dmd_product
SET SCHED_2 = 1
WHERE DMDID IN (
  SELECT DMDID
  FROM dmd_product
  INNER JOIN AMP
    ON AMP.VPID = DMDID
    OR AMP.APID = DMDID
  INNER JOIN AMPP
    ON AMPP.APID = AMP.APID
  INNER JOIN PRESCRIB_INFO
    ON AMPP.APPID = PRESCRIB_INFO.APPID
  WHERE PRESCRIB_INFO.SCHED_2= 1)
