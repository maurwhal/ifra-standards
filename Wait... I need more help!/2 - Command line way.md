# The command line way, step by step

This works on Windows, Mac, and Linux. It is more setup than the double-click
app, but it gives you the extra formats (Excel, one row per CAS, the PDFs).

The instructions below are for Windows. Mac and Linux are the same idea, using
Terminal instead of PowerShell.

## Step 1: Install Python (skip if you already have it)

1. Go to <https://www.python.org/downloads/>.
2. Click the big yellow button that says **Download Python 3.x.x**.
3. Open the file it downloads.
4. On the first screen of the installer, **check the box at the bottom that says
   "Add python.exe to PATH"**. This matters. If you miss it, the later steps will
   not work.
5. Click **Install Now**. Wait for it to finish. Click **Close**.

## Step 2: Open PowerShell

1. Press the **Windows key** on your keyboard.
2. Type `powershell`.
3. Press **Enter**. A window with a dark background opens. This is where you type
   the commands below.

## Step 3: Install the tool

Copy the line below. Click in the PowerShell window, paste it (right-click, or
Ctrl+V), and press **Enter**.

```
pip install "git+https://github.com/maurwhal/ifra-standards"
```

It prints a lot of lines and takes a minute. When it stops and you get your
prompt back, it is done. If it says `pip is not recognized`, close PowerShell,
open it again, and try once more. If it still says that, Python was installed
without the "Add to PATH" box checked; reinstall it and check that box.

You only do Step 1 and Step 3 once.

## Step 4: Get the spreadsheet

Still in PowerShell, paste this and press **Enter**:

```
ifra-standards fetch -o "$HOME\Desktop\ifra_standards.csv"
```

After a few seconds it prints `Saved 263 standards to ...`. The file is on your
Desktop, named `ifra_standards.csv`. Open it in Excel.

## The other formats

An Excel file instead of a plain CSV:

```
ifra-standards fetch -o "$HOME\Desktop\ifra_standards.xlsx"
```

One row per CAS number (a Standard covering several CAS numbers is repeated,
which is handy for a VLOOKUP against your own list):

```
ifra-standards fetch --explode-cas -o "$HOME\Desktop\by_cas.csv"
```

Every Standard PDF, into a new folder on your Desktop:

```
ifra-standards pdfs "$HOME\Desktop\IFRA PDFs"
```

## Updating the tool later

When IFRA publishes a new Amendment, or if the tool stops working because IFRA
changed their website, get the newest version with:

```
pip install --upgrade "git+https://github.com/maurwhal/ifra-standards"
```
