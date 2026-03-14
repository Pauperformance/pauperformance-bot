from deprecated import deprecated


@deprecated(reason="Migrated")
class WebPage:
    def __init__(self, page_name: str) -> None:
        self.page_name = page_name

    def as_markdown(self) -> str:
        return f"{self.page_name}.md"

    def as_html(self) -> str:
        return f"{self.page_name}.html"
