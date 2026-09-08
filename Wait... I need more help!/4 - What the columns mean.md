# What the columns mean

Each row in the spreadsheet is one IFRA Standard.

| Column | What it is |
|---|---|
| `name` | The material or group name, exactly as IFRA shows it in the library. |
| `cas_numbers` | The CAS number, or several CAS numbers separated by spaces if the Standard covers more than one. |
| `cas_list` | The same CAS numbers, but split apart with `; ` between them and checked that each one is a real CAS number (the last digit of a CAS number is a check digit). |
| `type` | A single letter: `R`, `P`, `S`, or blank. |
| `type_label` | The letter written out: Restriction, Prohibition, Specification, or Unspecified. A blank type is usually an older group entry. |
| `amendment` | Which Amendment to the IFRA Standards this Standard was last issued or revised in (for example `49` or `51`). |
| `publication_date` | Year and month the Standard was published, as `YYYY-MM`. |
| `pdf_url` | A direct link to the Standard's PDF on IFRA's site. Paste it into a browser to open the actual Standard. |
| `retrieved_at` | The date and time (UTC) you fetched the list. Only in the default output; the `--stable` option leaves it out. |

## The "one row per CAS" version

If you used `--explode-cas`, the layout is a little different:

- There is a `cas` column with one CAS number per row.
- A Standard that covers three CAS numbers shows up as three rows, identical
  except for `cas`.
- `cas_numbers` is still there so you can see the full set the Standard covers.

This version is meant for a VLOOKUP or a join: put your own CAS numbers in one
column and look them up against the `cas` column.

## What is not here

This is the list only. It does not include the actual restriction limits or the
category tables. Those are in each Standard's PDF. Use the `pdf_url` column, or
`ifra-standards pdfs` to download them all.
