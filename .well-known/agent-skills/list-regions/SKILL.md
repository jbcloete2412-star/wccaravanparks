# List Regions — southafricacamp.com Skill

## Description
Return all geographic regions covered in the Western Cape caravan park directory, with the park count for each.

## How to Use
Use the WebMCP `list-regions` tool when the page is loaded in a browser, or navigate to [https://southafricacamp.com](https://southafricacamp.com) to browse all regions.

## Output
An array of region objects (`id`, `name`, `count`) and the overall `total` park count across the directory.

## Example Output
```json
{
  "regions": [
    { "id": "cape-peninsula", "name": "Cape Peninsula", "count": 3 },
    { "id": "garden-route", "name": "Garden Route", "count": 8 }
  ],
  "total": 37
}
```
