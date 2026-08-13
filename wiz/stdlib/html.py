try:
    from bs4 import BeautifulSoup

    HTML_AVAILABLE = True
except Exception:
    HTML_AVAILABLE = False

from errors import WizError


class HtmlModule:

    def __init__(self):

        if not HTML_AVAILABLE:
            return

        self.functions = {
            "title": self.title,
            "text": self.text,
            "find": self.find,
            "find_all": self.find_all,
            "select": self.select,
            "get": self.get,
            "tag": self.tag,
            "children": self.children,
            "parent": self.parent,
            "attrs": self.attrs,
            "pretty": self.pretty,
            "extract": self.extract,
            "parse": self.parse,
        }

    def _check(self):
        if not HTML_AVAILABLE:
            raise WizError("The 'html' module requires beautifulsoup4.")

    def _soup(self, document):
        from bs4 import BeautifulSoup
        return BeautifulSoup(str(document), "html.parser")

    def title(self, document):
        self._check()
        soup = self._soup(document)
        return soup.title.string if soup.title else None

    def text(self, document, separator=""):
        self._check()
        soup = self._soup(document)
        return soup.get_text(separator)

    def find(self, document, tag, attrs=None, text=None):

        self._check()

        soup = self._soup(document)

        result = soup.find(str(tag), attrs=attrs, string=text)

        if result is None:
            return None

        return {
            "tag": result.name,
            "text": result.get_text(),
            "attrs": dict(result.attrs),
            "html": str(result),
        }

    def find_all(self, document, tag, attrs=None, limit=None):

        self._check()

        soup = self._soup(document)

        results = soup.find_all(str(tag), attrs=attrs, limit=limit)

        return [
            {
                "tag": result.name,
                "text": result.get_text(),
                "attrs": dict(result.attrs),
                "html": str(result),
            }
            for result in results
        ]

    def select(self, document, selector):

        self._check()

        soup = self._soup(document)

        results = soup.select(str(selector))

        return [
            {
                "tag": result.name,
                "text": result.get_text(),
                "attrs": dict(result.attrs),
                "html": str(result),
            }
            for result in results
        ]

    def get(self, document, selector, attribute=None):

        self._check()

        soup = self._soup(document)

        result = soup.select_one(str(selector))

        if result is None:
            return None

        return result.get(str(attribute)) if attribute else result.get_text()

    def tag(self, document, selector=None):

        self._check()

        soup = self._soup(document)

        if selector is None:
            return soup.name

        result = soup.select_one(str(selector))

        return result.name if result else None

    def children(self, document):

        self._check()

        soup = self._soup(document)

        return [
            str(child)
            for child in soup.children
            if getattr(child, "name", None)
        ]

    def parent(self, document, selector):

        self._check()

        soup = self._soup(document)

        result = soup.select_one(str(selector))

        if result is None or result.parent is None:
            return None

        return {
            "tag": result.parent.name,
            "attrs": dict(result.parent.attrs),
        }

    def attrs(self, document, selector):

        self._check()

        soup = self._soup(document)

        result = soup.select_one(str(selector))

        if result is None:
            return None

        return dict(result.attrs)

    def pretty(self, document):

        self._check()

        soup = self._soup(document)

        return soup.prettify()

    def extract(self, document, selector):

        self._check()

        soup = self._soup(document)

        result = soup.select_one(str(selector))

        if result is None:
            return None

        html = str(result)

        result.decompose()

        return {
            "html": html,
            "left": str(soup),
        }

    def parse(self, document):

        self._check()

        soup = self._soup(document)

        return {
            "tag": soup.name,
            "children": len(list(soup.children)),
            "text": soup.get_text(),
        }