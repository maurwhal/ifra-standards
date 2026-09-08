# If something goes wrong

Find the message that matches what you are seeing.

## "Windows protected your PC" (blue box)

Normal for the double-click app. Click **More info**, then **Run anyway**. See
[Easy way](1%20-%20Easy%20way.md) for detail.

## "ifra-standards is not recognized" (PowerShell)

The tool is not installed, or Python was installed without adding it to your
PATH.

1. Close PowerShell and open it again (it only picks up new programs on start).
2. Try the install command again:
   `pip install "git+https://github.com/maurwhal/ifra-standards"`
3. If `pip` itself is "not recognized", reinstall Python from python.org and
   **check the "Add python.exe to PATH" box** on the first screen.

## "pip is not recognized" (PowerShell)

Python is not installed, or was installed without the PATH box checked. Reinstall
it from <https://www.python.org/downloads/> and check that box.

## "git is not recognized" (during pip install)

The `git+https://` install needs Git. Either:

- Install Git from <https://git-scm.com/download/win> (accept all the defaults),
  close and reopen PowerShell, and try again, or
- Use the double-click app instead, which needs neither Python nor Git.

## "Could not find the sprig:config token" or "The Standards Library table markup may have changed"

IFRA changed their website in a way this tool did not expect.

- Try again in a minute in case it was a temporary glitch.
- If it keeps happening, the tool needs an update. Open an issue at
  <https://github.com/maurwhal/ifra-standards/issues> with the date and the exact
  message. As a stopgap you can always copy the table off the website by hand.

## "GET https://ifrafragrance.org/... failed"

A network problem. Check that you can open
<https://ifrafragrance.org/standards-library> in a browser. If you are on a work
network, a firewall or proxy may be blocking the tool; try from a home
connection.

## "XLSX output needs openpyxl"

The Excel format needs one extra piece. In PowerShell:

```
pip install openpyxl
```

Then run your `ifra-standards fetch ... .xlsx` command again.

## The spreadsheet opened with everything in one column

Excel sometimes does this with CSV files depending on your regional settings.
Open Excel first, then use **Data > From Text/CSV** and pick the file, or save as
`.xlsx` instead:

```
ifra-standards fetch -o output.xlsx
```

## Something else

Open an issue at <https://github.com/maurwhal/ifra-standards/issues>. Say what
you typed or clicked, and copy in the full message you got.
