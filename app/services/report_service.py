# app/services/report_service.py
class ReportService:
    def generate_inventory_report(self, format='pdf'):
        items = Item.query.all()
        if format == 'pdf':
            return self._generate_pdf_report(items)
        elif format == 'excel':
            return self._generate_excel_report(items)
        else:
            raise ValueError(f"Unsupported format: {format}")