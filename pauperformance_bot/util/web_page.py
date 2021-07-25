class WebPage:
    def __init__(self, page_name):
        self.page_name = page_name

    def as_markdown(self):
        return f"{self.page_name}.md"

    def as_html(self):
        return f"{self.page_name}.html"
