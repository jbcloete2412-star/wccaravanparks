# Search Caravan Parks — southafricacamp.com Skill

## Description
Search the Western Cape caravan park directory by region, keyword, or tag. Returns matching parks with names, towns, regions, and features.

## How to Use
Query the site at [https://southafricacamp.com](https://southafricacamp.com) using the search and filter tools, or use the WebMCP `search-parks` tool when the page is loaded in a browser.

## Available Regions
| ID | Name | Parks |
|---|---|---|
| cape-peninsula | Cape Peninsula | 3 |
| west-coast | West Coast | 5 |
| winelands | Cape Winelands | 2 |
| breede | Breede River Valley | 2 |
| overberg | Overberg | 2 |
| karoo | Karoo | 2 |
| garden-route | Garden Route | 8 |
| cederberg | Cederberg & West Coast Mountains | 2 |
| hartenbos | Hartenbos & Mossel Bay | 3 |
| sedgefield | Sedgefield | 1 |
| stillbay | Still Bay / Stilbaai | 1 |
| paternoster | Paternoster & Cape Columbine | 1 |
| overberg-ext | Overberg — Hermanus, Gansbaai & Kleinmond | 5 |

## Input Parameters
- `region` (optional): One of the region IDs above, or `all` (default)
- `keyword` (optional): Free-text search matched against park name, town, and tags
- `pets` (optional, boolean): If `true`, return only pet-friendly parks

## Output
A list of matching parks, each with `name`, `town`, `region`, `tags`, and `petFriendly` flag, plus a total `count`.
