update dmd_product
set assort_flav = 1
where dmdid in (
  select dmdid
  from dmd_product
  inner join dmd_amp
    on dmd_product.dmdid = dmd_amp.apid
  where dmd_amp.suppcd = 21014611000001102
  and dmd_amp.avail_restrictcd != 9
  and acbs = 1)
