# Technical notes

See tags:

```bash
jq -r '.tags[]' .tags
```

Filter notes by tag:

```bash
jq -r '.notes[] | select(.tags[] == "concurrency") | .path' .tags
```
