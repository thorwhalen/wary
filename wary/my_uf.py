"""Extensions to uf for features we wish existed.

This module provides utilities for creating web UIs that we'd like
to see in uf. These can be moved to uf later.
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class ComponentType(Enum):
    """Types of UI components."""

    HEADING = "heading"
    TEXT = "text"
    TABLE = "table"
    CARD = "card"
    STATS = "stats"
    CHART = "chart"
    FORM = "form"
    BUTTON = "button"
    LIST = "list"
    BADGE = "badge"


@dataclass
class Component:
    """Base UI component."""

    type: ComponentType
    content: Any
    props: dict = None

    def __post_init__(self):
        if self.props is None:
            self.props = {}

    def to_html(self) -> str:
        """Convert component to HTML."""
        if self.type == ComponentType.HEADING:
            level = self.props.get('level', 1)
            return f"<h{level}>{self.content}</h{level}>"

        elif self.type == ComponentType.TEXT:
            return f"<p>{self.content}</p>"

        elif self.type == ComponentType.TABLE:
            return self._table_to_html()

        elif self.type == ComponentType.CARD:
            return self._card_to_html()

        elif self.type == ComponentType.STATS:
            return self._stats_to_html()

        elif self.type == ComponentType.LIST:
            return self._list_to_html()

        elif self.type == ComponentType.BADGE:
            return self._badge_to_html()

        else:
            return f"<div>{self.content}</div>"

    def _table_to_html(self) -> str:
        """Convert table to HTML."""
        columns = self.props.get('columns', [])
        rows = self.content

        html = ['<table class="table">']
        html.append('<thead><tr>')
        for col in columns:
            html.append(f'<th>{col}</th>')
        html.append('</tr></thead>')

        html.append('<tbody>')
        for row in rows:
            html.append('<tr>')
            for cell in row:
                html.append(f'<td>{cell}</td>')
            html.append('</tr>')
        html.append('</tbody>')
        html.append('</table>')

        return '\n'.join(html)

    def _card_to_html(self) -> str:
        """Convert card to HTML."""
        title = self.props.get('title', '')
        html = ['<div class="card">']
        if title:
            html.append(f'<div class="card-header">{title}</div>')
        html.append(f'<div class="card-body">{self.content}</div>')
        html.append('</div>')
        return '\n'.join(html)

    def _stats_to_html(self) -> str:
        """Convert stats to HTML."""
        stats = self.content
        html = ['<div class="stats-container">']

        for stat in stats:
            label = stat.get('label', '')
            value = stat.get('value', '')
            html.append(f'<div class="stat-item">')
            html.append(f'<div class="stat-value">{value}</div>')
            html.append(f'<div class="stat-label">{label}</div>')
            html.append('</div>')

        html.append('</div>')
        return '\n'.join(html)

    def _list_to_html(self) -> str:
        """Convert list to HTML."""
        items = self.content
        ordered = self.props.get('ordered', False)
        tag = 'ol' if ordered else 'ul'

        html = [f'<{tag}>']
        for item in items:
            html.append(f'<li>{item}</li>')
        html.append(f'</{tag}>')
        return '\n'.join(html)

    def _badge_to_html(self) -> str:
        """Convert badge to HTML."""
        color = self.props.get('color', 'gray')
        return f'<span class="badge badge-{color}">{self.content}</span>'


@dataclass
class Page:
    """A web page with components."""

    title: str
    components: list[Component]
    styles: Optional[str] = None

    def to_html(self) -> str:
        """Convert page to full HTML."""
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            f'<title>{self.title}</title>',
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            self._get_default_styles(),
        ]

        if self.styles:
            html.append(f'<style>{self.styles}</style>')

        html.extend(
            [
                '</head>',
                '<body>',
                '<div class="container">',
            ]
        )

        for component in self.components:
            html.append(component.to_html())

        html.extend(['</div>', '</body>', '</html>'])

        return '\n'.join(html)

    def _get_default_styles(self) -> str:
        """Get default CSS styles."""
        return """
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
h1, h2, h3, h4, h5, h6 {
    color: #333;
    margin-top: 0;
}
.table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}
.table th, .table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
.table th {
    background-color: #f8f9fa;
    font-weight: 600;
}
.card {
    border: 1px solid #ddd;
    border-radius: 4px;
    margin: 10px 0;
}
.card-header {
    padding: 12px 16px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #ddd;
    font-weight: 600;
}
.card-body {
    padding: 16px;
}
.stats-container {
    display: flex;
    gap: 20px;
    margin: 20px 0;
    flex-wrap: wrap;
}
.stat-item {
    flex: 1;
    min-width: 150px;
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 4px;
    text-align: center;
}
.stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #007bff;
}
.stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 8px;
}
.badge {
    display: inline-block;
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 4px;
    font-weight: 600;
}
.badge-green {
    background-color: #28a745;
    color: white;
}
.badge-red {
    background-color: #dc3545;
    color: white;
}
.badge-gray {
    background-color: #6c757d;
    color: white;
}
.badge-blue {
    background-color: #007bff;
    color: white;
}
</style>
"""


class SimpleApp:
    """A simple web app builder."""

    def __init__(self, title: str = "App"):
        self.title = title
        self.routes = {}

    def page(self, path: str, title: str = None):
        """Register a page route."""

        def decorator(func: Callable) -> Callable:
            page_title = title or self.title
            self.routes[path] = {'handler': func, 'title': page_title}
            return func

        return decorator

    def get_page(self, path: str) -> Optional[str]:
        """Get rendered HTML for a path."""
        route = self.routes.get(path)
        if not route:
            return None

        handler = route['handler']
        page = handler()

        if isinstance(page, Page):
            return page.to_html()
        else:
            # Assume it's already HTML
            return str(page)


def make_table(columns: list[str], rows: list[list]) -> Component:
    """Helper to create a table component."""
    return Component(type=ComponentType.TABLE, content=rows, props={'columns': columns})


def make_stats(stats: list[dict]) -> Component:
    """Helper to create a stats component."""
    return Component(type=ComponentType.STATS, content=stats)


def make_card(title: str, content: str) -> Component:
    """Helper to create a card component."""
    return Component(type=ComponentType.CARD, content=content, props={'title': title})


def make_badge(text: str, color: str = 'gray') -> Component:
    """Helper to create a badge component."""
    return Component(type=ComponentType.BADGE, content=text, props={'color': color})
