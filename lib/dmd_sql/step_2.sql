insert into dmd_product
select
  dmd_amp.apid as dmdid,
  NULL as bnf_code,
  dmd_amp.vpid,
  dmd_amp."desc" as display_name,
  ema,
  1 as pres_statcd,
  avail_restrictcd,
  2 as product_type,
  0 as non_availcd,
  2 as concept_class,
  0 as nurse_f,
  0 as dent_f,
  prod_order_no,
  0 as sched_1,
  0 as padm,
  0 as sched_2,
  0 as fp10_mda,
  0 as acbs,
  0 as assort_flav,
  0 as catcd,
  NULL as tariff_category
from
  dmd_amp
inner join
  dmd_vmp
on
  dmd_vmp.vpid = dmd_amp.vpid
left join
  dmd_ap_info
on
  dmd_ap_info.apid = dmd_amp.apid
where
  dmd_amp.invalid is NULL
  and (dmd_amp.combprodcd is NULL
    or dmd_amp.combprodcd = 1)
  and (parallel_import is NULL
    or parallel_import = 0);

insert into dmd_product
select
  vpid as dmdid,
  NULL as bnf_code,
  vpid,
  nm as display_name,
  0 as ema,
  pres_statcd,
  NULL as avail_restrictcd,
  1 as product_type,
  non_availcd,
  1 as concept_class,
  0 as nurse_f,
  0 as dent_f,
  NULL as prod_order_no,
  0 as sched_1,
  0 as padm,
  0 as sched_2,
  0 as fp10_mda,
  0 as acbs,
  0 as assort_flav,
  0 as catcd,
  NULL as tariff_category
from
  dmd_vmp
where
  invalid is NULL
  and (combprodcd is NULL
    or combprodcd = 1);
