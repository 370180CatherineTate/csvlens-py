# csvlens-py

A lightweight Python CLI for interactively exploring and filtering large CSV files with column statistics and regex search.

---

## Installation

```bash
pip install csvlens-py
```

Or install from source:

```bash
git clone https://github.com/yourname/csvlens-py.git
cd csvlens-py
pip install .
```

---

## Usage

```bash
csvlens data.csv
```

**Filter rows using regex:**

```bash
csvlens data.csv --filter "email" --pattern ".*@gmail\.com"
```

**Show column statistics:**

```bash
csvlens data.csv --stats
```

**Limit output rows:**

```bash
csvlens data.csv --head 50
```

### Options

| Flag | Description |
|------|-------------|
| `--filter <col>` | Column name to apply regex filter on |
| `--pattern <regex>` | Regex pattern to match against filtered column |
| `--stats` | Display summary statistics for each column |
| `--head <n>` | Show only the first N rows |
| `--delimiter <char>` | Specify a custom delimiter (default: `,`) |

---

## Requirements

- Python 3.8+
- `pandas`
- `rich`

---

## License

This project is licensed under the [MIT License](LICENSE).