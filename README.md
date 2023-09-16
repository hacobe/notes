# Technical notes

Filter notes by tag:

```bash
jq -r '.notes[] | select(.tags[] == "concurrency") | .path' .tags
```
