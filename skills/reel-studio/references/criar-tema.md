# Criar um tema (marca)

Copie `themes/exemplo.json`, salve como `themes/<seu-nome>.json` (ou em `~/.config/reel-studio/themes/`, fora do plugin) e ajuste contra `contracts/theme.schema.json`:

- `colors`: fundo, superfície, texto, texto fraco, acento (e opcional acento2, sucesso).
- `fonts`: título e corpo; mono é opcional.
- `caption`: `word-highlight` (palavra atual em destaque) ou `line` (linha inteira); posição `bottom`, `center` ou `lower-third`.
- `cta`: texto e, opcional, `@seuperfil`.

Valide com:
```
cd engine && uv run reel-studio validate
```

Estilo e tema são independentes: qualquer tema combina com qualquer estilo.
