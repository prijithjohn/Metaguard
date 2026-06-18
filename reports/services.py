import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from metadata.models import DatasetColumn
from quality.models import QualityReport
from governance.models import SensitiveDataReport


class PdfReportService:
    @staticmethod
    def _format_date(value):
        return value.strftime("%Y-%m-%d %H:%M") if value else "N/A"

    @staticmethod
    def build_dataset_report(dataset):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("MetaGuard Dataset Report", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Dataset: {dataset.name}", styles["Heading2"]))
        story.append(Spacer(1, 8))

        summary_data = [
            ["Uploaded", PdfReportService._format_date(dataset.uploaded_at)],
            ["File name", dataset.file_name],
            ["Rows", str(dataset.row_count)],
            ["Columns", str(dataset.column_count)],
            ["Risk level", dataset.risk_level or "Unclassified"],
            ["Quality score", f"{dataset.quality_score:.1f}" if dataset.quality_score is not None else "N/A"],
        ]
        summary_table = Table(summary_data, colWidths=[150, 330], hAlign="LEFT")
        summary_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ])
        )
        story.append(summary_table)
        story.append(Spacer(1, 16))

        quality_report = QualityReport.objects.filter(dataset=dataset).first()
        story.append(Paragraph("Quality Summary", styles["Heading3"]))
        story.append(Spacer(1, 8))
        if quality_report:
            quality_data = [
                ["Missing values", str(quality_report.missing_values)],
                ["Duplicate rows", str(quality_report.duplicates)],
                ["Invalid records", str(quality_report.invalid_records)],
                ["Computed score", f"{quality_report.score:.1f}"],
            ]
        else:
            quality_data = [["No quality report available", ""]]

        quality_table = Table(quality_data, colWidths=[150, 330], hAlign="LEFT")
        quality_table.setStyle(
            TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ])
        )
        story.append(quality_table)
        story.append(Spacer(1, 16))

        sensitive_report = SensitiveDataReport.objects.filter(dataset=dataset).first()
        story.append(Paragraph("Sensitive Data Discovery", styles["Heading3"]))
        story.append(Spacer(1, 8))
        if sensitive_report and sensitive_report.total_sensitive_columns > 0:
            sensitive_data = [
                ["Sensitive columns", str(sensitive_report.total_sensitive_columns)],
                ["Total matches", str(sensitive_report.total_matches)],
                ["Last scanned", PdfReportService._format_date(sensitive_report.scanned_at)],
            ]
        else:
            sensitive_data = [["No sensitive data detected", ""]]

        sensitive_table = Table(sensitive_data, colWidths=[150, 330], hAlign="LEFT")
        sensitive_table.setStyle(
            TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ])
        )
        story.append(sensitive_table)
        story.append(Spacer(1, 16))

        columns = DatasetColumn.objects.filter(dataset=dataset)
        story.append(Paragraph("Column Metadata", styles["Heading3"]))
        story.append(Spacer(1, 8))
        if columns.exists():
            metadata_data = [["Column", "Type", "Nulls", "Uniques", "Classification"]]
            for column in columns:
                metadata_data.append([
                    column.column_name,
                    column.data_type,
                    str(column.null_count),
                    str(column.unique_count),
                    column.classification or "-",
                ])
            metadata_table = Table(metadata_data, colWidths=[140, 100, 70, 70, 100], hAlign="LEFT")
            metadata_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ])
            )
            story.append(metadata_table)
        else:
            story.append(Paragraph("No metadata available for this dataset.", styles["Normal"]))

        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))

        doc.build(story)
        buffer.seek(0)
        return buffer
