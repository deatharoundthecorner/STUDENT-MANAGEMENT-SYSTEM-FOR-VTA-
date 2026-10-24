# services/export_service.py
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
from models.student import Student
from services.audit_service import AuditService

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ExportService:
    def __init__(self):
        self.audit = AuditService()

    def _prepare_dataframe(self, students: list) -> pd.DataFrame:
        """Converts list of Student objects to a structured pandas DataFrame."""
        data = []
        for s in students:
            data.append({
                "ID_NUMBER": s.id_number,
                "YEAR_OF_REGISTERED": s.year_of_registered,
                "NAME_OF_THE_STUDENT": s.name_of_the_student,
                "PRIVATE_ADDRESS": s.private_address,
                "PHONE_NUMBER": s.phone_number,
                "DROP_OUT": s.drop_out,
                "THEORY_PASS": s.theory_pass,
                "NVQ_L3": s.nvq_l3,
                "NVQ_L4": s.nvq_l4,
                "OJT_PLACE": s.ojt_place,
                "OJT_ADDRESS": s.ojt_address,
                "OJT_PHONE_NUMBER": s.ojt_phone_number,
                "JOB_PLACE": s.job_place,
                "JOB_PLACE_ADDRESS": s.job_place_address,
                "CREATED_AT": s.created_at,
                "UPDATED_AT": s.updated_at
            })
        return pd.DataFrame(data)

    def export_to_csv(self, students: list, target_path_str: str):
        """Exports list of students to a CSV file."""
        df = self._prepare_dataframe(students)
        df.to_csv(target_path_str, index=False)
        self.audit.log_event("export.csv", summary={"record_count": len(students)})

    def export_to_excel(self, students: list, target_path_str: str):
        """Exports list of students to an Excel (.xlsx) file."""
        df = self._prepare_dataframe(students)
        df.to_excel(target_path_str, index=False)
        self.audit.log_event("export.xlsx", summary={"record_count": len(students)})

    def export_all_to_pdf(self, students: list, target_path_str: str):
        """Generates a landscape A4 PDF report with all student records."""
        doc = SimpleDocTemplate(
            target_path_str,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=35,
            bottomMargin=30
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1E2A38'), # Navy
            alignment=0, # Left
            spaceAfter=5
        )
        
        meta_style = ParagraphStyle(
            name='ReportMeta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#5A6A85'),
            spaceAfter=20
        )

        cell_style = ParagraphStyle(
            name='TableCell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#2E3A4E')
        )

        header_cell_style = ParagraphStyle(
            name='TableHeaderCell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )

        # Title and Meta info
        story.append(Paragraph("Student Records Summary Report", title_style))
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated: {date_str}  |  Total Records: {len(students)}", meta_style))
        
        # Table columns
        headers = [
            Paragraph("ID Number", header_cell_style),
            Paragraph("Name", header_cell_style),
            Paragraph("Year", header_cell_style),
            Paragraph("Phone", header_cell_style),
            Paragraph("Drop Out", header_cell_style),
            Paragraph("Theory Pass", header_cell_style),
            Paragraph("NVQ L3", header_cell_style),
            Paragraph("NVQ L4", header_cell_style),
            Paragraph("OJT Place", header_cell_style),
            Paragraph("Job Place", header_cell_style)
        ]
        
        data = [headers]
        
        for s in students:
            data.append([
                Paragraph(s.id_number, cell_style),
                Paragraph(s.name_of_the_student, cell_style),
                Paragraph(s.year_of_registered, cell_style),
                Paragraph(s.phone_number, cell_style),
                Paragraph(s.drop_out, cell_style),
                Paragraph(s.theory_pass, cell_style),
                Paragraph(s.nvq_l3, cell_style),
                Paragraph(s.nvq_l4, cell_style),
                Paragraph(s.ojt_place, cell_style),
                Paragraph(s.job_place, cell_style)
            ])
            
        # Total A4 width in landscape is 842 points. With margins of 30, printable area is 782 points.
        # Define relative column widths
        col_widths = [80, 130, 40, 75, 50, 60, 50, 50, 120, 127]
        
        student_table = Table(data, colWidths=col_widths, repeatRows=1)
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E2A38')), # Navy Header
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        
        story.append(student_table)
        doc.build(story)
        self.audit.log_event("export.pdf", summary={"record_count": len(students)})

    def export_profile_to_pdf(self, student: Student, photo_absolute_path: str, target_path_str: str):
        """Generates a detailed single-page Student Profile PDF report."""
        # Use standard A4 Portrait
        doc = SimpleDocTemplate(
            target_path_str,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            name='ProfileTitle',
            parent=styles['Heading1'],
            fontSize=24,
            leading=28,
            textColor=colors.HexColor('#1E2A38'),
            spaceAfter=2
        )
        
        subtitle_style = ParagraphStyle(
            name='ProfileSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#5A6A85'),
            spaceAfter=25
        )

        section_heading = ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#1E2A38'),
            spaceBefore=15,
            spaceAfter=8,
            keepWithNext=True
        )

        label_style = ParagraphStyle(
            name='ProfileLabel',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#4A5568')
        )

        value_style = ParagraphStyle(
            name='ProfileValue',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor('#1A202C')
        )

        # Header Block
        story.append(Paragraph("Student Profile Document", title_style))
        story.append(Paragraph(f"System Record Generated On: {datetime.now().strftime('%Y-%m-%d')}", subtitle_style))
        
        # Photo + Key details table
        # We will split top section into Photo (Left) and Basic Info (Right)
        basic_info_data = [
            [Paragraph("Student Name:", label_style), Paragraph(student.name_of_the_student, value_style)],
            [Paragraph("ID Number:", label_style), Paragraph(student.id_number, value_style)],
            [Paragraph("Registered Year:", label_style), Paragraph(student.year_of_registered or "N/A", value_style)],
            [Paragraph("Phone Number:", label_style), Paragraph(student.phone_number or "N/A", value_style)],
            [Paragraph("Private Address:", label_style), Paragraph(student.private_address or "N/A", value_style)]
        ]
        basic_info_table = Table(basic_info_data, colWidths=[100, 260])
        basic_info_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))

        # Load Student Photo
        try:
            # Scale photo to width 120, maintain aspect ratio
            photo_img = Image(photo_absolute_path, width=120, height=140)
        except Exception:
            # Fallback if image fails to load
            photo_img = Paragraph("No Image Available", label_style)

        # Main header layout table: Column 1 = Photo, Column 2 = basic_info_table
        header_layout_data = [[photo_img, basic_info_table]]
        header_layout_table = Table(header_layout_data, colWidths=[140, 372])
        header_layout_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        
        story.append(header_layout_table)
        story.append(Spacer(1, 10))

        # Horizontal separator line
        sep_table = Table([[""]], colWidths=[512])
        sep_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#E2E8F0')),
            ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('TOPPADDING', (0,0), (-1,0), 5),
        ]))
        story.append(sep_table)

        # Academic & Training Status Section
        story.append(Paragraph("Academic & Training Status", section_heading))
        academic_data = [
            [
                Paragraph("Drop Out Status:", label_style), Paragraph(student.drop_out, value_style),
                Paragraph("Theory Exam Pass:", label_style), Paragraph(student.theory_pass, value_style)
            ],
            [
                Paragraph("NVQ Level 3 Status:", label_style), Paragraph(student.nvq_l3, value_style),
                Paragraph("NVQ Level 4 Status:", label_style), Paragraph(student.nvq_l4, value_style)
            ]
        ]
        academic_table = Table(academic_data, colWidths=[120, 136, 120, 136])
        academic_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(academic_table)
        story.append(Spacer(1, 10))

        # OJT Details Section
        story.append(Paragraph("On the Job Training (OJT) Placement", section_heading))
        ojt_data = [
            [Paragraph("OJT Organisation:", label_style), Paragraph(student.ojt_place or "N/A", value_style)],
            [Paragraph("Contact Number:", label_style), Paragraph(student.ojt_phone_number or "N/A", value_style)],
            [Paragraph("Postal Address:", label_style), Paragraph(student.ojt_address or "N/A", value_style)]
        ]
        ojt_table = Table(ojt_data, colWidths=[120, 392])
        ojt_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(ojt_table)
        story.append(Spacer(1, 10))

        # Job Details Section
        story.append(Paragraph("Employment Details", section_heading))
        job_data = [
            [Paragraph("Employment Place:", label_style), Paragraph(student.job_place or "N/A", value_style)],
            [Paragraph("Postal Address:", label_style), Paragraph(student.job_place_address or "N/A", value_style)]
        ]
        job_table = Table(job_data, colWidths=[120, 392])
        job_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(job_table)

        # Build PDF
        doc.build(story)
