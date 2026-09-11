# ifra-standards

This makes a spreadsheet of every IFRA Standard.

IFRA lists all of their Standards on their website, but there is no button to
download the whole list. You can only see 24 at a time, across about 11 pages.
This gets all of them at once and saves them as a spreadsheet you can open in
Excel.

Each row has the material name, its CAS number(s), the Standard type
(Restriction, Prohibition, or Specification), which Amendment it came in on, the
publication date, and a link to the Standard's PDF.

## The easy way (nothing to install)

1. Open the [**Releases** page](https://github.com/maurwhal/ifra-standards/releases).
2. Under the latest release, download the file named `IFRA-Standards.exe`.
3. Double-click it.
4. A small black window opens. Give it a few seconds. When it says **Done**, it
   has saved a file to your Desktop.
5. Open that file from your Desktop in Excel.

The first time you run it, Windows may say **"Windows protected your PC"**. That
message shows up for any small program that has not paid for a signing
certificate. Click **More info**, then **Run anyway**. If you would rather not,
use the other way below.

There is a click-by-click version of these steps, with what each screen looks
like, in the [**Wait... I need more help!**](Wait...%20I%20need%20more%20help!)
folder.

## The other way (command line)

If you have Python, or are willing to install it, this works on Windows, Mac,
and Linux.

```
pip install "git+https://github.com/maurwhal/ifra-standards"
```

Then:

```
ifra-standards fetch -o ifra_standards.csv
```

The step-by-step version, starting from installing Python, is in the
[**Wait... I need more help!**](Wait...%20I%20need%20more%20help!) folder.

### Other things it can do (command line only)

Save as an Excel file instead of CSV:

```
ifra-standards fetch -o ifra_standards.xlsx
```

One row per CAS number, so a Standard that covers several CAS numbers is
repeated (useful for a VLOOKUP against your own list):

```
ifra-standards fetch --explode-cas -o by_cas.csv
```

Download every Standard PDF into a folder:

```
ifra-standards pdfs ./pdfs
```

Compare two lists you saved at different times, to see what changed:

```
ifra-standards fetch -o old.json
ifra-standards fetch -o new.json
ifra-standards diff old.json new.json
```

## What a row looks like

```
name,cas_numbers,type,type_label,amendment,publication_date,pdf_url
Citral,5392-40-5 141-27-5 106-26-3,R,Restriction,49,2020-01,https://.../IFRA_STD_021.pdf
Benzyl alcohol,100-51-6,R,Restriction,49,2020-01,https://.../IFRA_STD_014.pdf
```

The full list of columns and what they mean is in the help folder.

## Want the actual limits too?

This tool gives you the list: which Standards exist, their CAS numbers, and a
link to each PDF. It does not open those PDFs.

For the actual Maximum Acceptable Concentrations (the numbers IFRA sets per
category) and the rest of what is inside each Standard's PDF, see
[**ifra-standards-maximum-acceptable-concentrations-MAC**](https://github.com/maurwhal/ifra-standards-maximum-acceptable-concentrations-MAC),
a separate tool built on top of this one.

## About the data

The IFRA Standards are published by IFRA on their website for the fragrance
industry to use. This tool opens that public page, the same page a web browser
opens, and copies the list. It does not log in, it does not use a password, and
it does not reach anything that is not already public. It loads the page once or
twice each time it runs. IFRA's file for automated visitors (robots.txt) allows
that page.

This tool does not contain or share any IFRA documents. It only helps you get
the list that IFRA already publishes. For the Standards themselves, go to
[ifrafragrance.org](https://ifrafragrance.org).

Not affiliated with or endorsed by IFRA.

## About this project

This is a personal project. The code was written with help from Claude Sonnet 5,
an AI assistant. It is my own independent work and is not connected to my
employer or any organization. For any issue or concern, please
[open an issue](https://github.com/maurwhal/ifra-standards/issues) on this page.

## License

MIT. Free to use, change, and share. See [LICENSE](LICENSE).
