# OpenAI Model Spec – CSV Format Converter

**Name:** `IBKR_CSV_to_TradeFormat_Converter`

**Purpose:**  
To transform transaction data exported from Interactive Brokers (IBKR) in detailed CSV format into a simplified,
user-friendly trading format used for portfolio analysis or import into other platforms.

---

## 📥 Input Format Example (IBKR CSV, comma-separated)

**Header:**

```
"Symbol","Price","Amount","CurrencyPrimary","ClientAccountID",...,"Buy/Sell","Quantity","Proceeds","NetCash",...,"Commission",...
```

**Sample Row:**

```
"BME","2.761","276.1","GBP",...,"BUY","100","-276.1",...,"-1",...
```

---

## 📤 Target Output Format (CSV)

**Header:**

```
Symbol,Current Price,Date,Time,Change,Open,High,Low,Volume,Trade Date,Purchase Price,Quantity,Commission,High Limit,Low Limit,Comment,Transaction Type
```

**Sample Row:**

```
BME,2.761,2025/07/07,04:34 EDT,,,,,,20250707,2.761,100.0,1.0,,,,BUY
```

---

## 🔁 Transformation Logic from IBRK tp Yahoo finance format

| Output Field                         | Input Source Field(s) | Transformation Rule                               |
|--------------------------------------|-----------------------|---------------------------------------------------|
| `Symbol`                             | `Symbol`              | Copy as-is                                        |
| `Current Price`                      | _Not available_       | Leave blank                                       |
| `Date`                               | `Date/Time`           | Convert from `YYYY-MM-DD,HHMM TZ` to `YYYY/MM/DD` |
| `Time`                               | `Date/Time`           | Extract `HH:MM TZ` from `Date/Time`               |
| `Change`                             | _Not available_       | Leave blank                                       |
| `Open`, `High`, `Low`, `Volume`      | _Not available_       | Leave blank                                       |
| `Trade Date`                         | `TradeDate`           | Convert from `YYYY-MM-DD` to `YYYYMMDD`           |
| `Purchase Price`                     | `Price`               | Copy as-is                                        |
| `Quantity`                           | `Quantity`            | Copy as-is                                        |
| `Commission`                         | `Commission`          | Convert negative to positive, if needed           |
| `High Limit`, `Low Limit`, `Comment` | _Not available_       | Leave blank                                       |
| `Transaction Type`                   | `Buy/Sell`            | Copy as-is (e.g., BUY or SELL)                    |

---

## 🧠 Behavior Instructions for the Model

- Ignore unused columns from the source file.
- Be tolerant of missing or malformed values (e.g., fallback to empty string).
- Format all floats using 2–5 decimal digits.
- Ensure CSV output is clean and valid for spreadsheet import.
- Accept input as either a string of CSV or parsed dict rows.

---

## 🧪 Test Case

**Input Row (CSV):**

```csv
"BME","2.761","276.1","GBP","U17375211",...,"BUY","100","-276.1",...,"-1",...
```

**Expected Output:**

```csv
BME,2.761,2025/07/07,04:34 EDT,,,,,,20250707,2.761,100.0,1.0,,,,BUY
```