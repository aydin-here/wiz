class TableModule:

    def __init__(self):
        self.functions = {
            "render": self.render,
            "print": self.print_table,
            "md": self.markdown,
            "markdown": self.markdown,
            "csv": self.csv,
        }

    def _cell(self, value):
        return str(value)

    def render(self, rows, headers=None, padding=1, separator=" | ",
               align=None):

        rows = [list(map(self._cell, row)) for row in rows]

        headers = [self._cell(h) for h in (headers or [])]

        columns = max(
            [len(headers)] + [len(row) for row in rows]
        ) or 1

        headers = headers + [""] * (columns - len(headers))

        normalized = []

        for row in rows:
            row = row + [""] * (columns - len(row))
            normalized.append(row)

        widths = []

        for column in range(columns):

            values = [headers[column]] + [row[column] for row in normalized]

            widths.append(max(len(value) for value in values))

        pad = " " * int(padding)

        def line(row):
            cells = [
                cell.ljust(widths[index])
                for index, cell in enumerate(row)
            ]
            return pad + separator.join(cells).rstrip() + pad

        output = []

        output.append(line(headers))

        divider_width = (
            sum(widths) + max(0, columns - 1) * len(separator)
        )

        output.append(pad + "=" * divider_width + pad)

        for row in normalized:
            output.append(line(row))

        return "\n".join(output)

    def print_table(self, rows, headers=None, padding=1, separator=" | "):
        print(self.render(rows, headers, padding, separator))
        return True

    def markdown(self, rows, headers=None):

        rows = [list(map(self._cell, row)) for row in rows]

        headers = headers or []

        columns = max(
            [len(headers)] + [len(row) for row in rows]
        ) or 1

        headers = headers + [""] * (columns - len(headers))

        normalized = []

        for row in rows:
            row = row + [""] * (columns - len(row))
            normalized.append(row)

        widths = []

        for column in range(columns):

            values = [headers[column]] + [row[column] for row in normalized]

            widths.append(max(len(value) for value in values))

        def line(row):
            return "| " + " | ".join(
                cell.ljust(widths[index])
                for index, cell in enumerate(row)
            ) + " |"

        output = [line(headers)]

        output.append("| " + " | ".join(
            "-" * width for width in widths
        ) + " |")

        for row in normalized:
            output.append(line(row))

        return "\n".join(output)

    def csv(self, rows):
        import csv
        import io

        buffer = io.StringIO()

        writer = csv.writer(buffer)

        writer.writerows(rows)

        return buffer.getvalue()