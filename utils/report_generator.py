import os
import io
import json
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)


def generate_radiology_pdf(prediction, patient, doctor_name="Dr. MediScan AI Specialist"):
    """
    Generates a publication-grade Clinical Radiology Report in PDF format
    using ReportLab Platypus.
    Returns: BytesIO stream containing the PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0d6efd')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#6c757d')
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0b5ed7')
    )
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#212529')
    )
    bold_style = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#212529')
    )
    primary_diag_style = ParagraphStyle(
        'PrimaryDiag',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#dc3545') if prediction.prediction_result != 'Normal' else colors.HexColor('#198754')
    )

    story = []

    # 1. Header / Hospital Banner
    header_data = [
        [
            Paragraph("<b>MEDISCAN AI RADIOLOGY LAB</b><br/><font size='8' color='#6c757d'>Advanced Computer Vision & Diagnostic Decision Support</font>", title_style),
            Paragraph(f"<b>Report ID:</b> MS-RAD-{prediction.id:05d}<br/><b>Date:</b> {prediction.created_at.strftime('%d-%b-%Y %H:%M')}<br/><b>Status:</b> Verified", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0d6efd'), spaceAfter=12))

    # Parse JSON metadata
    try:
        details = json.loads(prediction.additional_info) if prediction.additional_info else {}
    except Exception:
        details = {}

    icd10 = details.get('icd10', 'Z00.00' if prediction.prediction_result == 'Normal' else 'R69')
    severity = details.get('severity', 'Moderate')
    differentials = details.get('differential_diagnosis', [])

    # 2. Patient Demographics & Examination Metadata Table
    patient_info = [
        [
            Paragraph("<b>Patient Name:</b>", bold_style), Paragraph(patient.name, normal_style),
            Paragraph("<b>Patient ID:</b>", bold_style), Paragraph(f"PID-{patient.id:04d}", normal_style)
        ],
        [
            Paragraph("<b>Age / Gender:</b>", bold_style), Paragraph(f"{patient.age} Y / {patient.gender.capitalize()}", normal_style),
            Paragraph("<b>Blood Group:</b>", bold_style), Paragraph(patient.blood_group or "Not Recorded", normal_style)
        ],
        [
            Paragraph("<b>Contact:</b>", bold_style), Paragraph(patient.contact or "N/A", normal_style),
            Paragraph("<b>Emergency Contact:</b>", bold_style), Paragraph(patient.emergency_contact or "N/A", normal_style)
        ],
        [
            Paragraph("<b>Study Body Part:</b>", bold_style), Paragraph(prediction.body_part.title(), normal_style),
            Paragraph("<b>Clinical History:</b>", bold_style), Paragraph(patient.medical_history or "None reported", normal_style)
        ]
    ]
    patient_table = Table(patient_info, colWidths=[100, 170, 110, 160])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 14))

    # 3. Primary Finding Box
    story.append(Paragraph("PRIMARY RADIOLOGICAL IMPRESSION", section_heading))
    conf_pct = round(prediction.confidence_score * 100, 1)
    
    finding_data = [
        [
            Paragraph(f"<b>Diagnosis: {prediction.prediction_result}</b>", primary_diag_style),
            Paragraph(f"<b>Confidence:</b> {conf_pct}%<br/><b>ICD-10 Code:</b> {icd10}<br/><b>Risk Level:</b> {severity}", normal_style)
        ],
        [
            Paragraph(f"<b>Clinical Synopsis:</b> {details.get('description', 'Evaluated using clinical pattern recognition.')}", normal_style),
            Paragraph(f"<b>Anomaly Field Density:</b> {details.get('abnormality_density_pct', 0)}%", normal_style)
        ]
    ]
    diag_box = Table(finding_data, colWidths=[360, 180])
    box_color = colors.HexColor('#e8f5e9') if prediction.prediction_result == 'Normal' else colors.HexColor('#fff3cd')
    border_color = colors.HexColor('#198754') if prediction.prediction_result == 'Normal' else colors.HexColor('#ffc107')
    diag_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), box_color),
        ('BOX', (0, 0), (-1, -1), 1.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(diag_box)
    story.append(Spacer(1, 14))

    # 4. Images Section: Original X-Ray & Heatmap side by side
    upload_folder = os.path.join(os.getcwd(), 'static', 'uploads')
    orig_img_path = os.path.join(upload_folder, prediction.image_path)
    heatmap_filename = details.get('heatmap_image')
    heatmap_path = os.path.join(upload_folder, heatmap_filename) if heatmap_filename else None

    images_row = []
    if os.path.exists(orig_img_path):
        try:
            images_row.append(RLImage(orig_img_path, width=170, height=170))
        except Exception:
            images_row.append(Paragraph("Image rendering error", normal_style))
    else:
        images_row.append(Paragraph("Original Scan on file", normal_style))

    if heatmap_path and os.path.exists(heatmap_path):
        try:
            images_row.append(RLImage(heatmap_path, width=170, height=170))
        except Exception:
            images_row.append(Paragraph("Heatmap unavailable", normal_style))
    else:
        images_row.append(Paragraph("Visual Heatmap attached to electronic record", normal_style))

    # Metric summary column
    metrics = details.get('metrics', {})
    metrics_text = (
        f"<b>Quantitative CV Metrics:</b><br/>"
        f"• Sharpness Variance: {metrics.get('sharpness_score', 'N/A')}<br/>"
        f"• Contrast Index: {metrics.get('contrast_score', 'N/A')}<br/>"
        f"• Bilateral Asymmetry: {metrics.get('bilateral_asymmetry_pct', 'N/A')}%<br/>"
        f"• Mean Attenuation: {metrics.get('mean_intensity', 'N/A')}<br/>"
        f"• Modality: {'DICOM High-Res' if details.get('dicom_metadata') else 'Radiograph (Standard)'}<br/>"
    )
    images_row.append(Paragraph(metrics_text, normal_style))

    img_table = Table(
        [
            [Paragraph("<b>Original X-Ray Scan</b>", bold_style), Paragraph("<b>AI Attention Heatmap</b>", bold_style), Paragraph("<b>Radiological Metrics</b>", bold_style)],
            images_row
        ],
        colWidths=[180, 180, 180]
    )
    img_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f5')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(img_table)
    story.append(Spacer(1, 14))

    # 5. Differential Diagnosis Ranking Table
    if differentials:
        story.append(Paragraph("RANKED DIFFERENTIAL DIAGNOSES", section_heading))
        diff_rows = [
            [
                Paragraph("<b>Condition</b>", bold_style),
                Paragraph("<b>Probability</b>", bold_style),
                Paragraph("<b>ICD-10</b>", bold_style),
                Paragraph("<b>Severity</b>", bold_style),
                Paragraph("<b>Pathology Findings</b>", bold_style)
            ]
        ]
        for diff in differentials[:4]:  # Top 4 differentials
            prob_val = diff.get('probability', 0)
            diff_rows.append([
                Paragraph(diff.get('condition', ''), bold_style),
                Paragraph(f"{prob_val}%", normal_style),
                Paragraph(diff.get('icd10', ''), normal_style),
                Paragraph(diff.get('severity', ''), normal_style),
                Paragraph(diff.get('description', '')[:75] + '...', normal_style)
            ])
        diff_table = Table(diff_rows, colWidths=[95, 65, 55, 65, 260])
        diff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(diff_table)
        story.append(Spacer(1, 14))

    # 6. Clinical Recommendations
    medical_tips = details.get('medical_tips', [])
    if not medical_tips and prediction.medical_tips:
        try:
            medical_tips = json.loads(prediction.medical_tips)
        except Exception:
            medical_tips = []

    if medical_tips:
        story.append(Paragraph("ACTIONABLE CLINICAL RECOMMENDATIONS", section_heading))
        tips_paragraphs = []
        for tip in medical_tips[:4]:
            tips_paragraphs.append(Paragraph(f"• {tip}", normal_style))
        tips_table = Table([[t] for t in tips_paragraphs], colWidths=[540])
        tips_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tips_table)
        story.append(Spacer(1, 14))

    # 7. Doctor's Impressions, Notes, and Signature Block
    doctor_notes = details.get('doctor_notes', 'Clinical correlation recommended. Patient advised regular follow-up.')
    sign_off_data = [
        [
            Paragraph(f"<b>Reviewing Radiologist Impression & Notes:</b><br/>{doctor_notes}", normal_style),
            Paragraph(f"<b>Physician Signature:</b><br/><br/>___________________________<br/><b>{doctor_name}</b><br/>Lic. Radiologist / Medical Officer", normal_style)
        ]
    ]
    sign_off_table = Table(sign_off_data, colWidths=[340, 200])
    sign_off_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#ced4da')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fdfdfe')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([
        sign_off_table,
        Spacer(1, 8),
        Paragraph("<font size='7' color='#6c757d'><b>CONFIDENTIAL MEDICAL DOCUMENT:</b> This AI-generated report is designed as a clinical decision-support tool. Final diagnosis and therapeutic interventions must be validated by a licensed healthcare professional.</font>", normal_style)
    ]))

    doc.build(story)
    buffer.seek(0)
    return buffer
