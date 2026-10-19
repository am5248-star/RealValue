# Dataset audit

## Files supplied

| File | Rows | What it contains | Decision |
|---|---:|---|---|
| `Chennai houseing sale.csv` | 7,109 | Chennai sales, property attributes, sale/build dates, price | Primary training/evaluation source |
| `chennai-properties.csv` | 699 | Chennai listings; asking price in lakhs, area and BHK | Keep separate; listing prices and schema are not transaction prices |
| `Real estate.csv` | 414 | Taiwan transactions, MRT distance, price per unit area | Exclude from Chennai model; geography/currency/target differ |
| `clean_data.csv` | 6,617 | Tree measurements and biomass | Not property data; exclude |

The four sources are not interchangeable samples of one target. Pooling them would produce invalid training labels.

## Primary source findings

- 7,109 rows and 7,109 unique `PRT_ID` values; no exact duplicate rows.
- Sale dates parse from 16 Jan 2004 through 17 Feb 2015.
- Target `SALES_PRICE`: ₹2,156,875 minimum, ₹10,335,050 median, ₹23,667,340 maximum.
- Missing: `N_BEDROOM` 1, `N_BATHROOM` 5, `QS_OVERALL` 48. Numeric missing values are imputed from the training split only.
- Locality spellings include variants such as `Chrompet`, `Chrompt`, `Chrmpet`, `Chormpet`, `Karapakkam`/`Karapakam`, and `T Nagar`/`TNagar`; automatic merging needs domain review and is not silently assumed.
- `REG_FEE` and `COMMIS` are excluded because they may encode the transaction price. ID and raw build date are also excluded; age is calculated using the sale date.

The table above records observed facts from the supplied CSVs. Main-model assumptions and known gaps are described in the root README.
