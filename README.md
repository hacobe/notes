# Technical notes

See the 5 most recently modified posts:

```bash
git ls-files | xargs -I{} git log -1 --format="%aI {}" {} | sort -nr | head -n 5
```

See tags:

```bash
jq -r '.tags[]' .tags
```

Filter notes by tag:

```bash
jq -r '.notes[] | select(.tags[] == "concurrency") | .path' .tags
```

Find notes that do not have tags:

```bash
comm -23 <(ls *.py *.md *.ipynb | sort) <(jq -r '.notes[].path' .tags | sort)
```
