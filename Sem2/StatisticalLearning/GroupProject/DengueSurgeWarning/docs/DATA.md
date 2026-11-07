# Data documentation: provenance, dictionary, checks

All data are public, aggregated, national-level series. **No personal data (PII) is used or
stored.** The case data are weekly national counts and the weather data are station or grid
measurements. The NEA dengue-cluster snapshot is fetched for context only and is not used in
any model. It contains locality polygons and cluster case counts, never individual records.

Retrieval is fully scripted with `pipeline/run.py fetch`. Every download is logged in
[`pipeline/data/raw/MANIFEST.json`](../pipeline/data/raw/MANIFEST.json) with:

* retrieval time;
* URL or API query and its parameters;
* SHA-256 hash;
* licence;
* the data.gov.sg metadata (`lastUpdatedAt`, coverage).

Raw files are not committed. The analysis-ready weekly snapshots are committed:

* `pipeline/data/processed/weekly.csv` and `weather_weekly.csv` (main analysis);
* `pipeline/data/processed_brief/` (2014-2018 analysis).

## 1. Sources

| key | content | provider, persistent link | coverage used | licence | accessed |
|---|---|---|---|---|---|
| `moh_weekly_bulletin` | Weekly Infectious Disease Bulletin: cases per disease per epi week. We keep *Dengue Fever* and *Dengue Haemorrhagic Fever*. | MOH via data.gov.sg, [d_ca168b2cb763640d72c4600a68f9909e](https://data.gov.sg/datasets/d_ca168b2cb763640d72c4600a68f9909e/view) | 2012-W01 to 2022-W52 (**main analysis**) | Singapore Open Data Licence v1.0 | 2026-11-06 |
| `moh_dengue_dhf_2014_2018` | Weekly number of dengue and DHF cases (the project brief's source) | MOH via data.gov.sg, [d_ac1eecf0886ff0bceefbc51556247015](https://data.gov.sg/datasets/d_ac1eecf0886ff0bceefbc51556247015/view) | 2014-W01 to 2018-W52 (cross-check and secondary analysis) | Singapore Open Data Licence v1.0 | 2026-11-06 |
| `mss` | Daily rainfall and mean, max and min temperature at station S24 Changi | Meteorological Service Singapore (NEA), [historical daily records](http://www.weather.gov.sg/climate-historical-daily/) | 2011-06-01 to 2022-12-31 (139 monthly files, 0 missing days) | NEA/MSS terms of use: free use with attribution. Files are not redistributed. | 2026-11-06 |
| `weather_open_meteo` | Daily mean relative humidity at 1.3521 N, 103.8198 E. Its rain and temperature are used only for cross-checks. | Open-Meteo historical archive (ERA5-based), <https://archive-api.open-meteo.com/v1/archive> | 2011-06-01 to 2022-12-31 | CC BY 4.0 | 2026-11-06 |
| `nea_rh_monthly` | Monthly mean relative humidity, Changi | NEA via data.gov.sg, [d_e3b1111a26b2aefef4f386c068d4ca5d](https://data.gov.sg/datasets/d_e3b1111a26b2aefef4f386c068d4ca5d/view) | 2011-06 to 2022-12 (used only to validate humidity) | Singapore Open Data Licence v1.0 | 2026-11-06 |
| `nea_dengue_clusters` | Current dengue cluster polygons (snapshot) | NEA via data.gov.sg, [d_dbfabf16158d1b0e1c420627c0819168](https://data.gov.sg/datasets/d_dbfabf16158d1b0e1c420627c0819168/view) | Snapshot only; used for context, not modelled | Singapore Open Data Licence v1.0 | 2026-11-07 |

**Why MSS station files.** The data.gov.sg "historical daily weather records" dataset
(`d_03bb2eb67ad645d0188342fa74ad7066`) holds only the Admiralty station for 2009 to Nov 2017, so it
cannot cover 2012-2022. NEA/MSS publishes the same kind of records per station and month on
weather.gov.sg. We use Changi (S24), Singapore's main climate station.

**Humidity.** MSS daily files contain no humidity. Humidity therefore comes from Open-Meteo and
is checked against NEA's monthly Changi series.

## 2. Unit of analysis and inclusion

* **Unit**: one epidemiological week, Singapore (national).
  * MOH epi weeks follow the MMWR Sunday-Saturday calendar, so 2014 and 2020 have a week 53.
  * Each week is keyed by `week_start`, the Monday after the Sunday that starts the epi week.
    This aligns case weeks with Monday-Sunday weather weeks.
* **Included**: all 574 weeks from 2012-W01 to 2022-W52. No week is missing or duplicated.
* **Excluded**:
  * In the 2014-2018 file, every year except 2014 has an empty week-53 placeholder row with no
    counts. These rows are dropped.
  * Weather days are aggregated only into complete weeks with at least 5 observed days. MSS has
    no missing days, so this only affects the last, partial week of 2022, which is set to NaN.
* **Target series**: dengue fever (DF) counts. DHF has 0-8 cases a week (mean 0.7). It is kept as
  a separate column and not modelled.
* **End of data**: the bulletin dataset's coverage on data.gov.sg ends on 2022-12-31
  (`coverageEnd` in MANIFEST.json).

## 3. Data dictionary

### `data/processed/weekly.csv` (one row per epi week)

| column | unit | definition |
|---|---|---|
| `week_start` | date | Monday after the Sunday that starts the MOH epi week |
| `epi_week` | text | MOH epi week label, e.g. `2015-W07` |
| `dengue_fever` | cases/week | notified dengue fever cases (target series) |
| `dhf` | cases/week | notified dengue haemorrhagic fever cases |
| `cases` | cases/week | DF + DHF (used only for quality checks) |
| `rain_sum` | mm/week | MSS Changi daily rainfall: mean over observed days × 7 |
| `rain_days` | days/week | days with rainfall ≥ 1 mm (share of observed days × 7) |
| `temp_mean`, `temp_max`, `temp_min` | °C | weekly mean of MSS daily mean, max and min temperature |
| `rh_mean` | % | weekly mean of Open-Meteo daily mean relative humidity |

`weather_weekly.csv` holds the same weather columns starting from 2011-06. This gives up to
12 weeks of weather lags for the first case week.

### `data/processed/model_table.csv` (derived, recreated by `run.py features`)

All predictors are known at the end of week *t*. `y` is weekly DF.

| column(s) | definition |
|---|---|
| `logy`, `logy_lag{1,2,3,4,6,8}` | log(1 + y) at week t and at earlier weeks |
| `logy_rm{4,8}` | rolling mean of log(1 + y) over the last 4 or 8 weeks |
| `growth_1`, `growth_4` | log change over 1 or 4 weeks |
| `thr_mu`, `thr_sd`, `thr_now` | mean and sd of the past 52 weeks, and the threshold mean + 2 sd |
| `seas_now` | 90th percentile of y in the same season (±17 days) of earlier years, using only weeks more than 26 weeks old |
| `marg_thr`, `marg_seas` | log(1 + y) − log(1 + threshold); a value > 0 means y is already above the threshold |
| `woy`, `woy_sin`, `woy_cos` | week of year and its Fourier terms |
| `<var>_lag{0,2,4,6,8,10,12}` | weather variable lagged 0-12 weeks |
| `y_fut_h{1,2,4}` | y at t + h (outcome; never used as a predictor) |
| `fthr_<kind>_h<h>` | threshold that y[t+h] must cross for target `<kind>`, known at t |
| `surge_thr_h<h>` | 1 if y[t+h] > mean + 2 sd of the 52 weeks up to t |
| `surge_seas_h<h>` | 1 if y[t+h] > the seasonal 90th percentile for week t+h |
| `surge_grow_h<h>` | 1 if y[t+h] ≥ (1 + pct_h)·y[t] and y[t+h] ≥ 50, with pct_h = 0.25, 0.30, 0.45 for h = 1, 2, 4 |
| `surge_thronset_h<h>`, `surge_seasonset_h<h>` | same as thr or seas, but defined only where y[t] is not yet above the threshold (onset weeks) |

## 4. Joins

Cases and weather are joined on `week_start` with a left join on the case weeks. Weather lags are
computed on the longer weather series before the join, so no case week loses rows.

## 5. Quality checks (`outputs/build_summary.md`)

* **Duplicates and gaps**: 0 duplicated epi weeks and 0 missing case weeks.
* **Large jumps**: 7 weeks have a week-on-week |log change| above 0.5. All fall around Chinese New
  Year or in low-count weeks (e.g. 2015-02-16 and 2015-02-23). They are kept as genuine reporting
  patterns.
* **Weather ranges**: no weather value is outside its plausible range.
* **Reporting revisions**: the bulletin and the 2014-2018 file are compared on their 261
  overlapping weeks.
  * DF counts are identical in 209 weeks. The largest difference is 8 cases in one week, and the
    totals differ by 0.2% (48,768 vs 48,656).
  * DHF differs by at most 1 case.
* **Weather cross-check** (weekly, MSS vs Open-Meteo, 2011-2022):
  * Mean temperature: r = 0.91, with Open-Meteo 1.3 °C cooler.
  * Rainfall: r = 0.48.
  * Open-Meteo humidity vs NEA monthly Changi RH: r = 0.56, with Open-Meteo 5.8 points higher.
  * Humidity is therefore the least reliable weather input.

## 6. Limitations

* Only national counts are available: no serotype, immunity or spatial data, even though serotype
  switches drive large epidemics.
* Notified counts depend on testing and reporting behaviour, for example during COVID-19 in
  2020-2021.
* Only one weather station is used, and rainfall varies across Singapore.
* The data stop in 2022.
* The 2014-2018 file alone has too few surges in a late test period for reliable evaluation. It is
  therefore used as a cross-check and secondary analysis, not as the main analysis.
