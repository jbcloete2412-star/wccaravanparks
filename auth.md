# auth.md — southafricacamp.com

The South Africa Camp website (`https://southafricacamp.com`) is fully public.
No agent registration or authentication is required to access any resource.

## Agent Access

All agent-facing endpoints are open with no credentials needed:

| Resource | URL |
|---|---|
| Agent skills index | `/.well-known/agent-skills/index.json` |
| MCP server card | `/.well-known/mcp/server-card.json` |
| API catalog | `/.well-known/api-catalog` |
| Markdown homepage | `/` (with `Accept: text/markdown`) |

## Registration

No registration is required. Agents may call any skill, read any resource, and use
WebMCP tools without obtaining credentials or creating an account.

## Contact

For questions about programmatic access, contact via [https://southafricacamp.com](https://southafricacamp.com).
