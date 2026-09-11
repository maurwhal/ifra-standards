# How it works

Short version: the tool loads the IFRA Standards Library page, reads a short-lived
access token out of it, then loads the page's table endpoint once more asking for
every row at once. It reads the standards out of that response. No login, nothing
private, one or two page loads per run.

The rest of this file is the detail, for anyone who wants to check the method or
fix the tool if IFRA changes their site.

## The page

The [IFRA Standards Library](https://ifrafragrance.org/standards-library) is a
Craft CMS page. Its table is a [Sprig](https://putyourlightson.com/plugins/sprig)
component: the page ships a small amount of markup plus an
[htmx](https://htmx.org/) attribute that tells the browser how to ask the server
to re-render the table (when you page, filter, or search).

## The one request

That re-render endpoint is:

```
GET https://ifrafragrance.org/index.php/actions/sprig-core/components/render
```

with two query parameters:

- `sprig:config` - a signed token describing which component to render (see below)
- `limit` - rows per page

The page uses `limit=24`. Ask for `limit=2000` instead and the endpoint returns
**every** standard in one HTML table, with no pagination footer. That single
response is all this tool needs.

## The signed token

`sprig:config` is not a random string you can reuse forever. It is an HMAC,
signed by the site with a server-side key, over a small JSON blob:

```json
{
  "id": "component-xxxxxx",
  "siteId": 1,
  "template": "_sprig\/standards-library",
  "variables": { "section": "standards", "page": 1, "limit": 24, ... }
}
```

Two things matter:

1. **The token rotates.** The `id` and the signature change on every deploy (in
   practice, very often). A token captured yesterday returns `400 Bad Request`
   today. So the tool scrapes a fresh one from the library page on each run:
   it downloads `/standards-library`, finds the `hx-vals` attribute that carries
   `sprig:config` and mentions `standards-library`, and reads the token out of
   it.
2. **The token must be sent byte-for-byte.** The signature covers the exact
   string, including the backslash before the template slash
   (`_sprig\/standards-library`). The tool keeps that backslash and lets
   `urllib.parse.urlencode` percent-encode it (`%5C%2F`). Re-format the token
   (drop the backslash, reorder keys) and the signature no longer matches.

Sprig merges request parameters over the token's `variables`, so appending
`&limit=2000` overrides the baked-in `limit=24` without needing a new signature.

## Reading a row

Every `<tr>` in the returned table carries a `data-layer` attribute (the site
uses it for analytics on the download button). It is a JSON object with exactly
the fields shown in the visible cells:

```json
{
  "event": "download",
  "document_id": 16999,
  "document_name": "\"Acetic acid, anhydride, ...\"",
  "document_type": "standards",
  "cas_number": "144020-22-4 28371-99-5",
  "publication_date": "2020-01",
  "type": "R",
  "amendment": "49"
}
```

The tool parses that (rather than scraping individual `<td>` cells, which is more
fragile) and takes the PDF link from the row's download button
(`.../docs/standards/IFRA_STD_XXX.pdf`).

## If it breaks

The likely failure is IFRA changing the page so the token or the `data-layer`
attribute can't be found. The tool raises a clear error in that case. Please
[open an issue](https://github.com/maurwhal/ifra-standards/issues) with the
date and the message, and as a fallback you can always copy the table off the
website by hand.
