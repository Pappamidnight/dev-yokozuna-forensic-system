from __future__ import annotations

import os
import sys
import re
from pathlib import Path
from datetime import datetime

PROJ_ROOT = Path(__file__).resolve().parent
VAULT_DIR = PROJ_ROOT / "vault"
SITE_DIR = PROJ_ROOT / "site"
ARTICLES_DIR = SITE_DIR / "articles"


def parse_markdown_to_html(md_content: str, filename_to_url: dict) -> str:
    html = md_content

    # Substituir links [[artigo]] por links HTML
    def replace_wikilink(match):
        target = match.group(1).strip()
        url = filename_to_url.get(target, f"{target}.html")
        return f'<a href="{url}" class="wiki-link">[[{target}]]</a>'

    html = re.sub(r'\[\[(.*?)\]\]', replace_wikilink, html)

    # Titulos
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Negrito e Codigo
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)

    # Listas
    lines = html.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        if line.startswith('- '):
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
            new_lines.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            new_lines.append(f'<p>{line}</p>' if line.strip() and not line.startswith('<h') and not line.startswith('<table') else line)
    if in_list:
        new_lines.append('</ul>')

    return "\n".join(new_lines)


def generate_wiki():
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    articles = []
    filename_to_url = {}

    for md_file in sorted(VAULT_DIR.rglob("*.md")):
        slug = md_file.stem
        filename_to_url[slug] = f"{slug}.html"
        articles.append((slug, md_file))

    # Renderizar cada artigo
    for slug, md_file in articles:
        content = md_file.read_text(encoding="utf-8", errors="replace")
        body_html = parse_markdown_to_html(content, filename_to_url)

        full_html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{slug} — LLM Knowledge Wiki</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0b0f19;
            --bg-card: #151d30;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-emerald: #10b981;
            --accent-purple: #a855f7;
            --border-color: #263352;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-primary);
            padding: 2rem 1.5rem;
            line-height: 1.7;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        nav {{ margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); }}
        nav a {{ color: var(--accent-blue); text-decoration: none; font-weight: 600; }}
        h1 {{ color: var(--accent-blue); margin-bottom: 1rem; font-size: 2rem; }}
        h2 {{ color: var(--text-primary); margin-top: 2rem; margin-bottom: 0.8rem; font-size: 1.4rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3rem; }}
        h3 {{ color: var(--accent-purple); margin-top: 1.5rem; font-size: 1.1rem; }}
        p {{ margin-bottom: 1rem; color: var(--text-primary); }}
        ul {{ margin-left: 1.5rem; margin-bottom: 1.5rem; color: var(--text-secondary); }}
        li {{ margin-bottom: 0.4rem; }}
        code {{ font-family: 'JetBrains Mono', monospace; color: var(--accent-emerald); background: rgba(16, 185, 129, 0.1); padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.85rem; }}
        .wiki-link {{ color: var(--accent-purple); text-decoration: none; font-weight: 600; background: rgba(168, 85, 247, 0.1); padding: 0.1rem 0.4rem; border-radius: 4px; }}
        .wiki-link:hover {{ text-decoration: underline; background: rgba(168, 85, 247, 0.2); }}
    </style>
</head>
<body>
    <div class="container">
        <nav><a href="../index.html">← Voltar ao Indice Geral da Wiki</a></nav>
        <article>
            {body_html}
        </article>
    </div>
</body>
</html>
"""
        out_path = ARTICLES_DIR / f"{slug}.html"
        out_path.write_text(full_html, encoding="utf-8")

    # Renderizar Index Geral (site/index.html)
    index_html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Wiki & Knowledge Vault — Dev Yokozuna</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0b0f19;
            --bg-card: #151d30;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-emerald: #10b981;
            --accent-purple: #a855f7;
            --border-color: #263352;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-primary);
            padding: 2rem 1.5rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{
            background: linear-gradient(135deg, #151d30 0%, #0b0f19 100%);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2.5rem;
            margin-bottom: 2rem;
        }}
        h1 {{ font-size: 2rem; color: var(--accent-blue); margin-bottom: 0.5rem; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1.5rem;
            transition: transform 0.2s, border-color 0.2s;
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        .card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent-blue);
        }}
        .card h3 {{ font-size: 1.2rem; color: var(--accent-blue); margin-bottom: 0.5rem; }}
        .card p {{ color: var(--text-secondary); font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>LLM Knowledge Wiki & Vault Forense</h1>
            <p style="color: var(--text-secondary);">Enciclopedia Estruturada de Processos Judiciais, Entidades Societarias e Doutrina | Compilado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <div class="grid">
"""
    for slug, md_file in articles:
        category = md_file.parent.name.replace("_", " ").title()
        index_html += f"""            <a href="articles/{slug}.html" class="card">
                <div style="font-size: 0.8rem; color: var(--accent-emerald); font-weight: 600; margin-bottom: 0.4rem;">{category}</div>
                <h3>{slug.replace('_', ' ').title()}</h3>
                <p>Artigo estruturado com links e referencias de direito material e factual.</p>
            </a>\n"""

    index_html += """        </div>
    </div>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"[SUCESSO] Wiki compilada com {len(articles)} artigos em: {SITE_DIR / 'index.html'}")


if __name__ == "__main__":
    generate_wiki()
