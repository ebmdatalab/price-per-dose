# Price per pill calculations

This project compares the price-per-quantity between different clinically comparable products, so we can advise practices and CCGs on potential cost savings.

We work from the monthly NHS dataset. In this, each row of data summarises all prescribing by a single BNF code (i.e. presentation, be it generic or branded) for one practice. For example, for a given practice we might see two rows of data for tramadol: one for Tramadol Hydrochloride 300mg tablets where it was prescribed generically; and one for Tramulief 300mg tablets where it was prescribed by brand.

Within a single month, for each row of data, we calculate a price-per-dose (in the case of Tramadol tablets, this is a price-per-pill).  We then approximate a realistic, best-case price-per-pill by calculating the cheapest decile across all brands (and generics) for that presentation.

We then work out what each GP Practice or CCG could save if it prescribed that presentation at the best decile.

* We only consider data from a single month, because the Drug Tariff changes monthly, making price-per-dose comparisons meaningless between months
* We cover data from GP Practices only
* When summing total possible savings, for a given practice or CCG, we don't consider savings that they are already making
* We use the NIC cost rather than the actual cost for these calculations

# Interpretation

The current model assumes that if pill A1 is expensive and pill A2 is
cheap, the perfect practice could switch to prescribing 100%
of pill A2.

Accordingly, in most cases, a saving should be achievable by switching to the cheapest brand available, rather than leaving the selection to pharmacists.  In some cases a saving will also be possible by switching formulation.

However, the variability in price-per-dose is often
outside the influence of the prescriber. As a result, it is likely
that many of the projected savings will not be 100% achievable. Some of the reasons include:

* Imported drugs often vary wildly in costs due to different import routes
* The prescribing data rarely distinguishes between pack sizes.  Larger pack sizes tend to be cheaper per-dose than smaller pack sizes.  A prescriber has no influence over the pack size used to fulfill a prescription
* In some cases, dispensers can charge the cost of an entire pack for medicines where the prescribed quantity is smaller than an entire pack ("broken bulk")
* Inconsistencies in the data. We have tried to address these where we have found them (see below for details)
* Non-bioequivalence. Some drugs within a generic class cannot always be considered clinically equivalent.
* Licensing differences. Two drugs which are bioequivalent may not be licensed for all possible uses, so cannot be switched.

An element of judgement is likely to be required in many cases to
decide how much of a theorical saving is possible in practice. We will
flag where products may be subject to any of these conditions where it is possible to do so automatically.

We have considered mitigating some of this effect by defining
achievable savings in terms of the best-peforming practices for a
presentation overall; i.e. assuming that the best-peforming practices
are already achieving all the practically possible savings.
Currently, however, the best achievable price is based on all prices
of all brands, across all practices.

This is discussed further in issues #2 and #16.


# Interpreting the spreadsheet

The per-CCG spreadsheet has the following column names:

* `bnf_code`: the code for the generic equivalent of that presentation
* `bnf_presentation`: the name of that presentation
* `bnf_chemical`: the chemical of the presentation
* `category`: the NHS Drug Tariff category of the presentation
* `lowest_decile`: the best price-per-dose we take as achievable
* `quantity`: the quantity of that presentation prescribed in the given month
* `price_per_dose`: the achieved price per dose in the given month
* `possible_savings`: the total possible savings for the given month
* `formulation_swap`: formulations we have considered equivalent for the analysis (see **Formulation Swaps**, below)
* `flag_imported`: set to `1` if the product is an import
* `flag_broken_bulk`: set to `1` if the product can have broken bulk rules applied
* `flag_non_bioequivance`: set to `1` if there are biolequivance issues between products with the generic category

# Special handling of specific codes

## Products which can't be substituted but the data implies they can

Our algorithm assumes all products coded as equivalent in the BNF can be considered as possible substitutions.

However, there are some inconsistencies in the BNF coding which break this assumption.  For example, all Gluten Free Breads are coded as equivalent (sliced bread, wholemeal bread, etc).

There are currently four such classes we know of; these are completely excluded from our analysis. The problem is fully described in issue #9.


## Products which can be substituted but the data implies they can't

### Formulation swaps

Many different formulations (with different BNF coding) are bioequivalent, so should be considered as alternatives when considering potential cost savings.

For example, 100mg Tramadol M/R capsules and tablets have different generic BNF codes, but could be substituted; in Sept 2016, tablets cost on average 38p each in capsules 24p each.

Therefore, we consider a range of formulations as equivalent.  We've created a manually-curated [spreadsheet of mappings](https://docs.google.com/spreadsheets/d/1SvMGCKrmqsNkZYuGW18Sf0wTluXyV4bhyZQaVLcO41c/edit#gid=1784930737), using the following guidelines:

* Any normal cap/tab pair is swappable. There may be some non-bioequivalent formatulions in this list such as diltiazem MR, but we have included these as there are still potentially large benefits to not prescribing them generically
* Generally consider orodispersible as interchangeable with solid-dose forms. This is because they have often got poor evidence for their use and are sometimes used for patent protection purposes.
* Effervescent/soluble tablets are considered to be non-interchangeable.
* Everything with a different route (e.g. tabs vs suppositories) has been left out.

See #11 (and #8) for discussion.

### Other uncoded equivalents

There are over 1000 products without a generic equivalent listed in the BNF (identified by codes ending in `A0`).

Some of these can be meaningfully compared with each other, despite not having a formally coded generic equivalent. For example, Blood Glucose Test Strips are clinically equivalent but have no generic equivalency coded in the BNF.

We can group them together by BNF subparagraph (*Glucose Blood Testing Reagents*) as every product within that paragraph is a blood glucose test strip, and the quantity field consistently refers to number of strips.

We have identified one other subparagraph that can be treated in the same way -- *Urine Testing Reagents*).

See issue #1 for a full discussion.

## Products with an inconsistent definition of `quantity`

To calculate possible savings, we work out a price-per-dose by dividing the net cost for each product by its quantity.

However, in a handful of products, the definition of `quantity` is not consistent, giving false positives for price variation.  We exclude these completely from our analysis.

See issue #12 for discussion.

## "Unspecified" products

Various special products are coded as being in "unspecified" categories. We exclude these. See issue #14 for discussion.

# See also

* [Comparing relative performance over time against a specific BNF paragraph](https://github.com/ebmdatalab/price-per-dose/blob/master/Comparing%20performance%20of%20entities%20over%20time.ipynb) (jupyter notebook)
* [How would I scalp the NHS?](https://github.com/ebmdatalab/price-per-dose/blob/master/How%20would%20I%20scalp%20the%20NHS%3F.ipynb) (jupyter notebook) - looking at how we might discover NP8 drugs which are possibly being sold at artificially inflated prices

# Important development notes

The current calculation relies on a table "tariff" for the tariff categories. This was correct as of September 2016, but changes monthly. That table should be updated before doing any analyses by tariff category.

Tests can be run with

    py.test tests/test.py
