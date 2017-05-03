# Price per pill calculations

This project compares the price-per-quantity between different clinically comparable products, so we can advise practices and CCGs on potential cost savings.

We work from the monthly [GP Practice prescribing data](http://content.digital.nhs.uk/searchcatalogue?q=title%3A%22presentation+level+data%22&area=&size=10&sort=Relevance). In this, each row of data describes prescribing of a presentation for one practice for that month. For example, for a given practice we might see two rows of data for tramadol: one for Tramadol Hydrochloride 300mg tablets where it was prescribed generically; and one for Tramulief 300mg tablets where it was prescribed by brand.

Within a single month, we calculate the average price-per-dose achieved by each practice for each presentation (generic and branded combined).  We then approximate a realistic, best-case price-per-dose by finding the average price-per-dose which is at the cheapest decile for that presentation.

We then work out what each GP Practice or CCG could save if it prescribed that presentation at the best decile.

* We only consider data from a single month, because the Drug Tariff changes monthly, making price-per-dose comparisons meaningless between months
* We cover data from standard GP Practices only
* When summing total possible savings, for a given practice or CCG, we don't consider savings that they are already making
* We use the NIC cost rather than the actual cost for these calculations
* When calculating a price-per-dose, we combine all formluations (e.g. tablets and capsules) that we consider to be clinically equivalent.

# Interpretation

The current model assumes that if pill A1 is expensive and pill A2 is
cheap, the perfect practice could switch to prescribing 100%
of pill A2.

## Types of savings

Most saving opportunities are possible because:


### The Drug Tariff prices do not reflect low-cost alternatives that are on the market

The Tariff price is usually based on the list prices of one or more supplier. Particularly in a crowded market where many brands and manufactured generics are available, the Tariff price may not reflect the cheapest prices available.

This happens most frequently in Category C, where the Tariff price is usually based on the list price of the originator brand. For example, as of Jan 2016, the Tariff price for generic Flucitasone/Salmeterol is based on the GSK list price for Seretide, which is up to 25% higher than the cheapest brand available.

The quickest way to make a cost saving in such cases is to switch to prescribing by the cheapest brand.

### Different formulations may vary hugely in price

This is a variation of the list-price phenomenon described above. Where (for example) both tablets and capsules are available for a Category C drug, the originator brands may have abritrarily different list prices, which are then reflected in the Tariff.

For example, the Tariff price of Venlafaxine 150mg MR capsules is
twice that of the equivalent tablets. There is no underlying market
logic to the cost differential: the cheapest brand available is, in
fact, capsules.

In this case, a large cost saving could be achieved by prescribing tablets generically, but an even larger cost saving could be achieved by prescribing a specific brand of capsulte.

### Sometimes, GPs prescribe expensive brands

For example, at the time of writing there is widespread prescribing of Nasonex, which is more than 3 times the price of the manufactured generic equivalent listed in the Tariff.

The cost saving here would be achieved by switching to prescribing by
the generic presentation (for which cheap manufactured generics are
available).

Expensive brands may be prescribed out of patient preference, or for
historic reasons, or occasionally for clinical reasons (e.g. in the
case of many antiepileptic drugs).

### Suppliers invent incentives for pharmacies to dispense at uncompetitive prices

This is a price-gouging practice which can be applied to any presentation not listed in the Drug Tariff ("NP8").

A generic presentation which isn't in the Tariff can be invoiced by
the dispenser at any available list price. There are various
contractual mechanisms which allow a dispenser and a supplier to
collude in sharing the profit for arbitrarily-priced drugs.

The fix is either to prescribe a specific, cheaper brand; or wait for
the drug to be placed in the Tariff. Sometimes one formulation
(e.g. tablets) will be in the Tariff, but another (e.g. capsules)
isn't. In these cases keeping the prescription generic but switching
the formulation will also realise a saving.

### No official non-propriety name exists

Two kinds of testing strips (Blood glucose, and Urine) will never
appear in the tariff as products in the tariff must be listed against
an official non-proprietary name, and these don't have one.

Such categories typicaly contain a very large range of functionally
equivalent products with a correspondingly large range of prices.


### Resource scarcity or monpolies

Many drugs are only available from one supplier. In these cases,
particularly where the supplier is outside the PPRS, the list price of
a drug is liable to go up unexpectedly for a range of reasons, the simplest being  market forces such as resource scarcity, or reducing efficiencies of scale for items with reducing demand.

Sometimes it is alleged that monopoly positions are exploited by arbitrarily inflating costs, as happened in the [case of Epanutin](https://www.gov.uk/government/news/cma-fines-pfizer-and-flynn-90-million-for-drug-price-hike-to-nhs). When the drug has a very narrow therapeutic index (such as Epanutin), the supplier will often include their name in the authorised marketing name of the product (e.g. *Phenytoin Sodium Flynn*). This means GPs are able to continue to prescribe the product by name (as they must for drugs with such a narrow therapeutic index), but despite being generic, [no identical imported drugs can be substituted](http://www.wpt.co.uk/resources/news/parallel-imports-into-the-uk/) as the name as prescribed includes a trade mark.

It is very difficult to detect the difference between these two
reasons for price hikes in the data, and the potential savings are
similarly hard to identify from data.  Sometimes there is a clinically
equivalent alternative drug available, but in drugs with a very narrow
therapeutic index (e.g. Epanutin) a switch is not possible.

Examples of drugs which (1) are only available from a single supplier; (2) have relatively small but significant spending; (3) have seen recent, extreme price hikes (>300%); and (4) for which there are realistically no therapeutic substitution, include:

* Trimipramine Mal Cap 50mg
* Clonazepam Tab 500mcg
* Anytriptyline Hydrochloride Tab 50ms

## Achievability of savings

As can be seen from the above, in most cases a saving should be
achievable by switching to the cheapest brand available, rather than
leaving the selection to pharmacists.  In some cases a saving will
also be possible by switching formulation (e.g. from capsules to
tablets). Where we have included formulation swaps in our calculation,
we indicate this in the data.

However, the variability in price-per-dose is sometimes outside the
influence of the prescriber. As a result, it is likely that many of
the projected savings will not be 100% achievable. Some of the reasons
include (in rough order of their relative likely effect):

* Licensing differences. Two drugs which are bioequivalent may not be licensed for all possible uses, so cannot be switched.
* Non-bioequivalence. Some drugs within a generic class cannot always be considered clinically equivalent.
* Imported drugs often vary wildly in costs due to different import routes, and the prescriber may not be able to specify an imported version (or, of course, an import route)
* Inconsistencies in the data. We have tried to address these where we have found them (see below for details)
* Our calculations use NIC cost, which is based on the list / tariff prices for that drug. However, the actual costs paid by the NHS to dispensers include bulk discounts and other adjustments. Usually, this means we will slightly overestinate the possible savings (because we are not including the effect of bulk discounts).
* The prescribing data rarely distinguishes between pack sizes.  Larger pack sizes tend to be cheaper per-dose than smaller pack sizes.  A prescriber has no influence over the pack size used to fulfill a prescription. This effect should usually be minimal.
* In some cases, dispensers can charge the cost of an entire pack for medicines where the prescribed quantity is smaller than an entire pack ("broken bulk"). It is unlikely that this happens systematically, and therefore this effect is likely to be small and semi-random

Due to these variables, an element of judgement is likely to be
required to decide how much of a theorical saving is possible in
practice. We flag where products may be subject to any of these
conditions where it is possible to do so automatically.

## Less conservative model

We have mitigated some of this effect by assuming that the
best-peforming practices are already achieving all the practically
possible savings, and selecting the price-per-dose achieved by the
practice at the cheapest decile.  An alternative, less conservative
approach, is to define a best-case price-per-dose by taking the
average price-per-dose at the cheapest decile for a presentation
(brands and generic) across the entire dataset. This has the effect of
removing the assumption that the best-performing practices are already
achieving the best real-world savings possible.

Compare the two approaches:

 * [Default scenario](https://github.com/ebmdatalab/price-per-dose/blob/7d9d2c5ebb22875ce3442fcec08ab65f8a28fed0/Price%20per%20dose.ipynb): assuming the best performing practices are already doing the realistic best that can be done
 * [Alternative scenario](https://github.com/ebmdatalab/price-per-dose/blob/5be742773f866f9c184f1db86e569ccba45d5429/Price%20per%20dose.ipynb): assuming that the best performing practice could theoretically achieve a price-per-dose that is based only on the chemicals and not what practices are already doing


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

# Implications of prescribing by brand

Most cost savings can be realised by prescribing by brand. This is (to some extent) problematic, as it goes against historic clinical recommendations and the way the system was originally set up to promote competitive markets.

Also, because dispensing contractors' profits are guaranteed, any savings to the NHS made by switching to cheap brands will ultimately be offset by increased costs for Category M medicines or decreased discount reductions.

However, in a situation where CCGs are the primary gatekeepers of spending it is unavoidable that they have the most incentives to become the market driver of costs.  In the current situation, where some CCGs have more information and capability to act on it than others, then those CCGs will benefit disproportionately. Conversely, pharmacy contractors in such areas will have their profits reduced disproportionately to other contractors.

Therefore, any system which equalises access to cost-saving opportunities increases equity across the country in terms of CCG funding.

However, because prescriptions are "sticky" (patients and GPs are reluctant to switch them), CCGs are likely to be inefficient market actors, compared with the dispensing contractors when dealing with generically prescribed items.


## Clinical issues

Clinically, generic prescribing is recommended to avoid unecessary cognitive overhead which may lead to confusion or mistakes. For example:

* GPs have to think about fewer drug names, so there are likely to be fewer errors
* Patients get drugs in consistently branded boxes, reducing the risk of confusion (e.g. "double dipping")

## Market efficiency issues

In terms of market incentives, branded prescribing is not optimal because:

* the main mechanism by which pharmacists are guaranteed their profit is by arbitrary margins added by the DH to the list price in Category M drugs. Removing their ability to make a margin reduces their incentive to push wholesalers for better prices, which can be expected drive up overall costs for the NHS.
  * against this argument, if GPs were to prescribe according to current market conditions by switching to the cheapest alternatives (i.e. they were willing to switch products in response to price changes), this would in theory maintain the pressure on manufacturers and wholesalers to offer competitive prices
* when paying pharmacies, the NHS assumes a discount rate which reflects assumed bulk discounts negotiated by pharmacists. Because the overall pharmacy profit is guaranteed, drug companies have responded by removing discounts on some branded drugs (where the contractor has no choice about what to dispense), which increases their own profits at a cost to the NHS (see [this OFT report](http://webarchive.nationalarchives.gov.uk/20140402142426/http:/www.oft.gov.uk/shared_oft/reports/comp_policy/oft967.pdf) and [this PSNC webpage](https://psnc.org.uk/funding-and-statistics/funding-distribution/dispensing-at-a-loss/) for more on this).

On the other hand, there are market efficiency problems around generic prescribing too - most significantly in "NP8" products (see above for more).

## Contractor fairness

The practice of branded prescribing, when evenly applied across the country, should not unduly affect contractor profits as these are guaranteed and applied via Category M and bulk discount deductions.

However, when unevenly applied, some contractors will be significantly disadvantaged compared with others.

For this reason, the PSNC is ["completely against"](http://psnc.org.uk/funding-and-statistics/funding-distribution/retained-margin-category-m/) the practice of generic prescribing.

On the other hand, if branded prescribing cost-saving opportunities were applied evenly across the country, this would no longer be an issue.

# Special handling of specific codes

## Products which can't be substituted but the data implies they can

Our algorithm assumes all products coded as equivalent in the BNF can be considered as possible substitutions.

However, there are some inconsistencies in the BNF coding which break this assumption.  For example, all Gluten Free Breads are coded as equivalent (sliced bread, wholemeal bread, etc).

There are currently four such classes we know of; these are completely excluded from our analysis. The problem is fully described in [issue #9](https://github.com/ebmdatalab/price-per-dose/issues/9).


## Products which can be substituted but the data implies they can't

### Formulation swaps

Many different formulations (with different BNF coding) are bioequivalent, so should be considered as alternatives when considering potential cost savings.

For example, 100mg Tramadol M/R capsules and tablets have different generic BNF codes, but could be substituted; in Sept 2016, tablets cost on average 38p each in capsules 24p each.

Therefore, we consider a range of formulations as equivalent.  We've created a manually-curated [spreadsheet of mappings](https://docs.google.com/spreadsheets/d/1SvMGCKrmqsNkZYuGW18Sf0wTluXyV4bhyZQaVLcO41c/edit#gid=1784930737), using the following guidelines:

* Any normal cap/tab pair is swappable. There may be some non-bioequivalent formatulions in this list such as diltiazem MR, but we have included these as there are still potentially large benefits to not prescribing them generically
* Generally consider orodispersible as interchangeable with solid-dose forms. This is because they have often got poor evidence for their use and are sometimes used for patent protection purposes.
* Effervescent/soluble tablets are considered to be non-interchangeable.
* Everything with a different route (e.g. tabs vs suppositories) has been left out.

See [issue #11](https://github.com/ebmdatalab/price-per-dose/issues/11) (and [issue #8](https://github.com/ebmdatalab/price-per-dose/issues/8)) for discussion.

### Other uncoded equivalents

There are over 1000 products without a generic equivalent listed in the BNF (identified by codes ending in `A0`; and in dm+d with a *Basis of name: Other* for their VMP).

Some of these can be meaningfully compared with each other, despite not having a formally coded generic equivalent. For example, Blood Glucose Test Strips are clinically equivalent but have no generic equivalency coded in the BNF (though they are grouped with the [*Blood glucose biosensor testing strips* VMP](http://dmd.medicines.org.uk/DesktopDefault.aspx?VMP=3432511000001102&toc=nofloat) in dm+d.

We can group them together by BNF subparagraph (*Glucose Blood Testing Reagents*) as every product within that paragraph is a blood glucose test strip, and the quantity field consistently refers to number of strips.

We have identified one other subparagraph that can be treated in the same way -- *Urine Testing Reagents*).

See [issue #1](https://github.com/ebmdatalab/price-per-dose/issues/1) for a full discussion.

## Products with an inconsistent definition of `quantity`

To calculate possible savings, we work out a price-per-dose by dividing the net cost for each product by its quantity.

However, in a handful of products, the definition of `quantity` is not consistent, giving false positives for price variation.  We exclude these completely from our analysis.

See [issue #12](https://github.com/ebmdatalab/price-per-dose/issues/) for discussion.

## "Unspecified" products

Various special products are coded as being in "unspecified" categories. We exclude these. See issue #14 for discussion.

# See also

* [Comparing relative performance over time against a specific BNF paragraph](https://github.com/ebmdatalab/price-per-dose/blob/master/Comparing%20performance%20of%20entities%20over%20time.ipynb) (jupyter notebook)
* [How would I scalp the NHS?](https://github.com/ebmdatalab/price-per-dose/blob/master/How%20would%20I%20scalp%20the%20NHS%3F.ipynb) (jupyter notebook) - looking at how we might discover NP8 drugs which are possibly being sold at artificially inflated prices

# Important development notes

The current calculation relies on a table "tariff" for the tariff categories. This was correct as of September 2016, but changes monthly. That table should be updated before doing any analyses by tariff category.

Tests can be run with

    py.test tests/test.py
