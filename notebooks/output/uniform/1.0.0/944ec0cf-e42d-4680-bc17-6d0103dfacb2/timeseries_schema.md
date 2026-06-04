| name | dtype | required | description | unit | constraints | source | formula |
| --- | --- | --- | --- | --- | --- | --- | --- |
| day_index | int64 | False | Zero-based day index within the allocation window. |  | >=0, strictly increasing by 1 | framework |  |
| date | datetime64[ns] | True | Calendar day for this allocation row. |  | unique, sorted ascending, daily grain | framework |  |
| weight | float64 | True | Final feasible daily allocation after clipping, lock preservation, and remaining-budget constraints. |  | finite, >=0, sum ~= 1.0 | framework |  |
| price_usd | float64 | True | BTC price in USD for the given date when available. | USD | finite when present, nullable for future dates | framework |  |
| locked | bool | False | True when a row belongs to an immutable locked history prefix. |  | boolean values only | framework |  |
| PriceUSD | float64 | False | Raw BRK BTC price column when preserved in payloads. | USD | finite when present | brk | raw PriceUSD |
| mvrv | float64 | False | BRK MVRV ratio when retained in strategy payloads. |  | finite when present | brk |  |
| time | datetime64[ns] | False | BRK daily timestamp column. |  | valid datetime when present | brk | raw time |
| AdrActCnt | float64 | False | BRK active addresses count. |  | finite when present | brk |  |
| AdrBalCnt | float64 | False | BRK addresses with non-zero balance. |  | finite when present | brk |  |
| AssetCompletionTime | datetime64[ns] | False | BRK ingestion completion timestamp for asset-day data. |  | valid datetime when present | brk |  |
| AssetEODCompletionTime | datetime64[ns] | False | BRK end-of-day completion timestamp for asset metrics. |  | valid datetime when present | brk |  |
| BlkCnt | float64 | False | BRK blocks mined during the day. |  | finite when present | brk |  |
| CapMrktCurUSD | float64 | False | BRK current market capitalization in USD. | USD | finite when present | brk |  |
| CapMrktEstUSD | float64 | False | BRK estimated market capitalization in USD. | USD | finite when present | brk |  |
| FeeTotNtv | float64 | False | BRK total transaction fees in native BTC units. | BTC | finite when present | brk |  |
| FlowInExNtv | float64 | False | BRK exchange inflow in native BTC units. | BTC | finite when present | brk |  |
| FlowInExUSD | float64 | False | BRK exchange inflow valued in USD. | USD | finite when present | brk |  |
| FlowOutExNtv | float64 | False | BRK exchange outflow in native BTC units. | BTC | finite when present | brk |  |
| FlowOutExUSD | float64 | False | BRK exchange outflow valued in USD. | USD | finite when present | brk |  |
| HashRate | float64 | False | BRK network hash rate estimate. |  | finite when present | brk |  |
| IssTotNtv | float64 | False | BRK total daily issuance in native BTC units. | BTC | finite when present | brk |  |
| IssTotUSD | float64 | False | BRK total daily issuance valued in USD. | USD | finite when present | brk |  |
| PriceBTC | float64 | False | BRK BTC reference price quoted in BTC. | BTC | finite when present | brk |  |
| ROI1yr | float64 | False | BRK trailing 1-year return metric. |  | finite when present | brk |  |
| ROI30d | float64 | False | BRK trailing 30-day return metric. |  | finite when present | brk |  |
| ReferenceRate | float64 | False | BRK reference rate for BTC. |  | finite when present | brk |  |
| ReferenceRateETH | float64 | False | BRK reference rate for BTC quoted in ETH. |  | finite when present | brk |  |
| ReferenceRateEUR | float64 | False | BRK reference rate for BTC quoted in EUR. |  | finite when present | brk |  |
| ReferenceRateUSD | float64 | False | BRK reference rate for BTC quoted in USD. | USD | finite when present | brk |  |
| SplyCur | float64 | False | BRK current circulating BTC supply. | BTC | finite when present | brk |  |
| SplyExNtv | float64 | False | BRK supply held on exchanges in native BTC units. | BTC | finite when present | brk |  |
| SplyExUSD | float64 | False | BRK supply held on exchanges valued in USD. | USD | finite when present | brk |  |
| SplyExpFut10yr | float64 | False | BRK projected BTC supply 10 years ahead. | BTC | finite when present | brk |  |
| TxCnt | float64 | False | BRK on-chain transaction count. |  | finite when present | brk |  |
| TxTfrCnt | float64 | False | BRK transfer transaction count. |  | finite when present | brk |  |
| volume_reported_spot_usd_1d | float64 | False | BRK reported spot exchange volume in USD for 1 day. | USD | finite when present | brk |  |