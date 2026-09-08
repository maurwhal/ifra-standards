# The easy way, step by step

This uses the double-click app. It only works on Windows. Nothing to install.

## Get the app

1. Go to <https://github.com/maurwhal/ifra-standards/releases>.
2. You will see a heading with a version number, like **v0.1.0**. Under it there
   is a section called **Assets**. Click **Assets** if it is not already open.
3. In that list, click **`IFRA-Standards.exe`**. It downloads to your Downloads
   folder, like any other file.

## Run it

1. Open your Downloads folder.
2. Double-click **`IFRA-Standards.exe`**.

### If Windows shows a blue box that says "Windows protected your PC"

This is normal. It shows up for any small program that has not paid a company a
few hundred dollars a year for a signing certificate. The app is safe, but
Windows cannot tell that on its own.

1. In that blue box, click the small link that says **More info**.
2. A button appears at the bottom that says **Run anyway**. Click it.

You only have to do this the first time.

### If your antivirus blocks it or deletes it

Some antivirus programs flag brand-new small programs by mistake. If yours does
and you are not comfortable telling it to allow the file, do not fight it. Use
[the command line way](2%20-%20Command%20line%20way.md) instead.

## What happens

1. A small black window opens.
2. It prints a couple of lines about getting the list from the IFRA website.
3. After a few seconds it prints **Done** and the full location of the file it
   saved.
4. The file is on your **Desktop**, named something like
   **`IFRA Standards 2026-09-15.csv`**.
5. Press **Enter** to close the black window.

## Open the spreadsheet

Double-click the file on your Desktop. It opens in Excel (or whatever opens
`.csv` files on your computer). Each row is one IFRA Standard.

## Doing it again later

Run the app again any time. It always gets the current list. It will save a new
file with today's date, so your older ones are not overwritten.

When IFRA publishes a new Amendment, come back to the Releases page and download
the newest `IFRA-Standards.exe`. The old one keeps working, it just will not know
about any changes IFRA made to their website after it was built.
