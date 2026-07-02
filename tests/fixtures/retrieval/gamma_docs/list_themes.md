> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/workspace/list-themes.md).

# GET /themes

List the themes available in the authenticated workspace. Use the returned `id` values as `themeId` in generation requests.

### What themes are

A theme controls the visual style of a generated Gamma — colors, fonts, backgrounds, and layout feel. Every workspace has access to Gamma's standard theme library plus any custom themes created in the workspace. Pass a theme's `id` as `themeId` in `POST /generations` or `POST /generations/from-template` to apply it.

### Pagination

Results are cursor-paginated. Each response includes `hasMore` (boolean) and `nextCursor` (string or null). To fetch the next page, pass the `nextCursor` value as the `after` query parameter. Use `limit` (1-50, default 20) to control page size. Use `query` to filter themes by name, or `type=standard|custom` to limit results to built-in or workspace themes. Keep the same `type` value across paginated requests.

## List themes

> Lists all themes available to the workspace, including standard themes and custom workspace themes.

```json
{"openapi":"3.0.0","info":{"title":"Gamma Public API","version":"1.0"},"tags":[{"name":"public-api","description":"Public API endpoints for external integrations"}],"servers":[{"url":"https://public-api.gamma.app","description":"Production"}],"security":[{"api-key":[]}],"components":{"securitySchemes":{"api-key":{"type":"apiKey","in":"header","name":"X-API-KEY","description":"API key for authentication"}},"schemas":{"ListThemesResponse":{"type":"object","properties":{"data":{"description":"Array of theme items","type":"array","items":{"$ref":"#/components/schemas/ThemeItem"}},"hasMore":{"type":"boolean","description":"Whether more results exist beyond this page"},"nextCursor":{"type":"string","nullable":true,"description":"Cursor for fetching the next page (null if no more results)"}},"required":["data","hasMore","nextCursor"]},"ThemeItem":{"type":"object","properties":{"id":{"type":"string","description":"Unique theme identifier"},"name":{"type":"string","description":"Display name of the theme"},"colorKeywords":{"description":"Keywords describing the theme's color palette","type":"array","items":{"type":"string"}},"toneKeywords":{"description":"Keywords describing the theme's tone/style","type":"array","items":{"type":"string"}},"type":{"type":"string","description":"Theme type: standard (built-in) or custom (workspace-created)","enum":["standard","custom"]}},"required":["id","name","type"]}}},"paths":{"/v1.0/themes":{"get":{"description":"Lists all themes available to the workspace, including standard themes and custom workspace themes.","operationId":"listThemes","parameters":[{"name":"query","required":false,"in":"query","description":"Search query to filter themes by name","schema":{"type":"string"}},{"name":"limit","required":false,"in":"query","description":"Maximum number of themes to return","schema":{"minimum":1,"maximum":50,"type":"number"}},{"name":"after","required":false,"in":"query","description":"Cursor for pagination (from previous response's nextCursor)","schema":{"type":"string"}},{"name":"type","required":false,"in":"query","description":"Filter by theme type: \"standard\" for built-in themes, \"custom\" for workspace-created themes. Must be kept consistent across paginated requests; changing it mid-pagination will yield inconsistent results.","schema":{"type":"string","enum":["standard","custom"]}}],"responses":{"200":{"description":"Themes retrieved successfully","content":{"application/json":{"schema":{"$ref":"#/components/schemas/ListThemesResponse"}}}},"400":{"description":"Invalid request parameters"},"401":{"description":"Invalid or missing API key"}},"summary":"List themes","tags":["public-api"]}}}}
```

{% hint style="info" %}
For guidance on when to fetch theme IDs and how to use them in requests, see [Use themes and folders](/guides/list-themes-and-list-folders-apis-explained.md).
{% endhint %}

## Related

* [Use themes and folders](/guides/list-themes-and-list-folders-apis-explained.md) for workflow guidance
* [POST /generations](/generations/create-generation.md) if you want to apply a returned `themeId`


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation dynamically by asking a question.

Perform an HTTP GET request on the current page URL with the `ask` query parameter, and the optional `goal` query parameter:

```
GET https://developers.gamma.app/workspace/list-themes.md?ask=<question>&goal=<endgoal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is optional and describes the broader end goal you are ultimately trying to accomplish on behalf of the user. GitBook uses it to tailor the answer towards what is most useful for that goal.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
