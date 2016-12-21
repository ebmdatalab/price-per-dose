UPDATE dmd_product
SET product_type = 3
WHERE DMDID IN (SELECT
  DMDID
FROM dmd_product
INNER JOIN AMP
  ON AMP.APID = dmd_product.DMDID
INNER JOIN VMP
  ON AMP.VPID = VMP.VPID
WHERE VMP.NM = AMP.NM
AND product_type = 2)
