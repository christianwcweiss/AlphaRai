import os
import tempfile

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from result import BacktestResult


class PDFReporter:
    def __init__(
        self,
        backtest_result: BacktestResult,
    ) -> None:
        self._backtest_result = backtest_result

    def save_report(self, file_path: str) -> None:
        template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "jinja")
        env = Environment(loader=FileSystemLoader(template_dir))

        template = env.get_template("report.html")
        with tempfile.TemporaryDirectory as temp_dir:
            self._backtest_result.generate_graphs(temp_dir)
            html_content = template.render(**self._backtest_result.to_report_data(temp_dir))

            HTML(string=html_content).write_pdf(file_path)


if __name__ == "__main__":
    result = BacktestResult("test")
    reporter = PDFReporter(result)
    reporter.save_report(os.path.join(os.path.dirname(__file__), "test.pdf"))
