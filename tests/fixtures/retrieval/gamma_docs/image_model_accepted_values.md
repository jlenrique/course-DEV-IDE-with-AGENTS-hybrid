> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/reference/image-model-accepted-values.md).

# Image models

{% hint style="info" %}
**Looking for general Gamma help?** This page lists image models for the API. For general guidance on choosing visuals and image styles in the Gamma app, see [How do I use the visuals menu in Gamma?](https://help.gamma.app/en/articles/11856101-how-do-i-use-the-visuals-menu-in-gamma) in the Help Center.
{% endhint %}

### Quick reference

* Set `imageOptions.source` to `aiGenerated` when using any of the model strings below.
* If `imageOptions.model` is omitted, Gamma selects a model automatically.
* Higher-tier, HD, and video models usually take longer to complete, so longer polling windows may be helpful.
* The tables below list the image-generation model strings currently documented for the REST API. Video-capable model strings also appear in the OpenAPI enum, but this page does not document them yet.
* See [Access and Pricing](/get-started/access-and-pricing.md) for plan and credit details.

### Standard models

| Model Name            | String                    | Credits/Image |
| --------------------- | ------------------------- | ------------- |
| Flux 1 Quick          | `flux-1-quick`            | 2             |
| Flux 2 Fast           | `flux-2-klein`            | 2             |
| Flux Kontext Fast     | `flux-kontext-fast`       | 2             |
| Imagen 3 Fast         | `imagen-3-flash`          | 2             |
| GPT Image Mini Low    | `gpt-image-1-mini-low`    | 2             |
| Luma Photon Flash     | `luma-photon-flash-1`     | 2             |
| GPT Image 2 Mini      | `gpt-image-2-mini`        | 5             |
| Flux 1 Pro            | `flux-1-pro`              | 8             |
| Imagen 3 Pro          | `imagen-3-pro`            | 8             |
| Flux 2 Pro            | `flux-2-pro`              | 8             |
| GPT Image Mini Medium | `gpt-image-1-mini-medium` | 8             |
| Ideogram 3 Turbo      | `ideogram-v3-turbo`       | 6             |
| Luma Photon           | `luma-photon-1`           | 10            |
| Recraft V4            | `recraft-v4`              | 12            |
| Leonardo Phoenix      | `leonardo-phoenix`        | 15            |

### Advanced models

| Model Name                           | String                   | Credits/Image |
| ------------------------------------ | ------------------------ | ------------- |
| Flux 2 Flex                          | `flux-2-flex`            | 20            |
| Flux 2 Max                           | `flux-2-max`             | 20            |
| Flux Kontext Pro                     | `flux-kontext-pro`       | 20            |
| Ideogram 3                           | `ideogram-v3`            | 20            |
| Imagen 4                             | `imagen-4-pro`           | 20            |
| Recraft V3                           | `recraft-v3`             | 20            |
| Nano Banana Flash (Gemini 2.5 Flash) | `gemini-2.5-flash-image` | 20            |
| GPT Image Mini High                  | `gpt-image-1-mini-high`  | 20            |
| GPT Image                            | `gpt-image-1-medium`     | 30            |
| GPT Image 2                          | `gpt-image-2`            | 20            |
| Flux 1 Ultra                         | `flux-1-ultra`           | 30            |
| Imagen 4 Ultra                       | `imagen-4-ultra`         | 30            |
| Dall-E 3                             | `dall-e-3`               | 33            |

### Premium models

| Model Name                     | String                        | Credits/Image |
| ------------------------------ | ----------------------------- | ------------- |
| Nano Banana 2 Mini             | `gemini-3.1-flash-image-mini` | 34            |
| Flux Kontext Max               | `flux-kontext-max`            | 40            |
| Recraft V3 Vector              | `recraft-v3-svg`              | 40            |
| Recraft V4 Vector              | `recraft-v4-svg`              | 40            |
| Ideogram 3 Quality             | `ideogram-v3-quality`         | 45            |
| Nano Banana 2                  | `gemini-3.1-flash-image`      | 50            |
| Nano Banana Pro (Gemini 3 Pro) | `gemini-3-pro-image`          | 70            |
| Nano Banana 2 HD               | `gemini-3.1-flash-image-hd`   | 75            |

### Ultra models

| Model Name                           | String                  | Credits/Image |
| ------------------------------------ | ----------------------- | ------------- |
| GPT Image 2 HD                       | `gpt-image-2-hd`        | 115           |
| GPT Image Detailed                   | `gpt-image-1-high`      | 120           |
| Nano Banana Pro HD (Gemini 3 Pro HD) | `gemini-3-pro-image-hd` | 120           |
| Recraft V4 Pro                       | `recraft-v4-pro`        | 125           |

### Output dimensions

Quality tiers (`low` / `medium` / `high`) affect detail and cost — not pixel count. Aspect ratio is the only parameter that changes output dimensions.

| Provider | Model(s)                                                                                               | 1:1       | 16:9      | 9:16      | Max side |
| -------- | ------------------------------------------------------------------------------------------------------ | --------- | --------- | --------- | -------- |
| OpenAI   | `gpt-image-2-mini`, `gpt-image-2`, `gpt-image-2-hd`                                                    | 1024×1024 | 1536×1024 | 1024×1536 | 1536 px  |
| OpenAI   | `gpt-image-1-medium`, `gpt-image-1-high`                                                               | 1024×1024 | 1536×1024 | 1024×1536 | 1536 px  |
| OpenAI   | `gpt-image-1-mini-low`, `gpt-image-1-mini-medium`, `gpt-image-1-mini-high`                             | 1024×1024 | 1536×1024 | 1024×1536 | 1536 px  |
| Google   | `imagen-3-flash`, `imagen-3-pro`, `imagen-4-pro`, `imagen-4-ultra`                                     | 1024×1024 | 1408×768  | 768×1344  | 1408 px  |
| Ideogram | `ideogram-v3`, `ideogram-v3-turbo`, `ideogram-v3-quality`                                              | 1024×1024 | 1280×768  | 768×1344  | 1344 px  |
| Flux     | `flux-1-quick`, `flux-1-pro`, `flux-1-ultra`                                                           | 1024×1024 | 1376×768  | 768×1376  | 1376 px  |
| Flux     | `flux-2-pro`, `flux-2-flex`, `flux-2-max`, `flux-kontext-fast`, `flux-kontext-pro`, `flux-kontext-max` | 1440×1440 | 1920×1088 | 1088×1920 | 1920 px  |
| Leonardo | `leonardo-phoenix`                                                                                     | 1024×1024 | 1376×768  | 768×1376  | 1376 px  |
| Recraft  | `recraft-v3`, `recraft-v3-svg`                                                                         | 1024×1024 | 1820×1024 | 1024×1820 | 1820 px  |
| Luma     | `luma-photon-1`, `luma-photon-flash-1`                                                                 | 1536×1536 | 2048×1152 | 1152×2048 | 2048 px  |
| Gemini   | `gemini-3.1-flash-image-mini`, `gemini-3.1-flash-image`, `gemini-3.1-flash-image-hd`                   | 1024×1024 | 1920×1080 | 1080×1920 | 1920 px  |
| Gemini   | `gemini-3-pro-image`                                                                                   | 2048×2048 | 2752×1536 | 1536×2752 | 2752 px  |
| Gemini   | `gemini-3-pro-image-hd`                                                                                | 2048×2048 | 3840×2160 | 2160×3840 | 3840 px  |
| Gemini   | `gemini-2.5-flash-image`                                                                               | 1024×1024 | 1920×1080 | 1080×1920 | 1920 px  |

{% hint style="info" %}
OpenAI models output 3:2 / 2:3 when 16:9 / 9:16 is requested. Other providers match the requested ratio exactly.
{% endhint %}

### Related

* [Generate from text](/guides/generate-api-parameters-explained.md) for `imageOptions` guidance
* [Poll for results](/guides/async-patterns-and-polling.md) if you need longer polling windows for slower models
* [Access and Pricing](/get-started/access-and-pricing.md) for plan and credit details


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation dynamically by asking a question.

Perform an HTTP GET request on the current page URL with the `ask` query parameter, and the optional `goal` query parameter:

```
GET https://developers.gamma.app/reference/image-model-accepted-values.md?ask=<question>&goal=<endgoal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is optional and describes the broader end goal you are ultimately trying to accomplish on behalf of the user. GitBook uses it to tailor the answer towards what is most useful for that goal.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
