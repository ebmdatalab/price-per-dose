update dmd_product
set fp10_mda = 1
where dmdid in (
  select dmdid
  from dmd_product
  inner join dmd_amp
    on dmd_amp.vpid = dmdid
    or dmd_amp.apid = dmdid
  inner join dmd_ampp
    on dmd_amp.apid = dmd_ampp.apid
  inner join dmd_prescrib_info
    on dmd_prescrib_info.appid = dmd_ampp.appid
  where dmd_prescrib_info.fp10_mda = 1)
