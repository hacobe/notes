# Technical notes

Publish notes to https://hacobe.github.io/notes:

```
jb build --all notes
cd notes
ghp-import -n -p -f _build/html
```

See https://jupyterbook.org/start/publish.html for setup details.