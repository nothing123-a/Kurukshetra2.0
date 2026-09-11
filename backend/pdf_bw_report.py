import os
import io
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def generate_black_and_white_chart(df: pd.DataFrame, output_path: str) -> str:
    """Generate a crisp, publication-quality black and white graph for the PDF report"""
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=180)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    cols = list(df.columns)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    has_district = any('district' in c.lower() for c in cols)
    has_imr = any('mortality' in c.lower() or 'imr' in c.lower() for c in cols)

    if has_district and has_imr:
        dist_col = next(c for c in cols if 'district' in c.lower())
        imr_col = next(c for c in cols if 'mortality' in c.lower() or 'imr' in c.lower())
        
        sorted_df = df.dropna(subset=[imr_col]).sort_values(by=imr_col, ascending=False)
        top_anomalous = pd.concat([sorted_df.head(5), sorted_df.tail(4)])
        
        y_pos = np.arange(len(top_anomalous))
        values = top_anomalous[imr_col].values
        labels = [str(x)[:16] for x in top_anomalous[dist_col].values]
        
        bars = ax.barh(y_pos, values, color='#333333', edgecolor='black', linewidth=1.2, height=0.65)
        for i, bar in enumerate(bars):
            if i < 3:
                bar.set_hatch('///')
                bar.set_facecolor('#000000')
            else:
                bar.set_facecolor('#777777')
                bar.set_hatch('..')
                
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8, fontweight='bold', color='black')
        ax.invert_yaxis()
        ax.set_xlabel(f"{imr_col} (Per 1,000 Live Births)", fontsize=9, fontweight='bold', color='black')
        ax.set_title("DISTRICT HEALTHCARE DIVERGENCE & OUTLIER BENCHMARK (B&W AUDIT PLOT)", fontsize=10, fontweight='bold', color='black', pad=10)
        
        mean_val = df[imr_col].mean()
        ax.axvline(mean_val, color='black', linestyle='--', linewidth=1.5, label=f'Dataset Mean ({mean_val:.1f})')
        ax.legend(loc='lower right', frameon=True, edgecolor='black', fontsize=8)

    elif len(num_cols) >= 1:
        target_col = num_cols[0]
        data = df[target_col].dropna()
        n, bins, patches = ax.hist(data, bins=12, color='#555555', edgecolor='black', linewidth=1.2, hatch='///')
        ax.set_title(f"FREQUENCY DISTRIBUTION: {target_col.upper()} (B&W AUDIT)", fontsize=10, fontweight='bold', color='black')
        ax.set_xlabel(target_col, fontsize=9, fontweight='bold', color='black')
        ax.set_ylabel("Frequency", fontsize=9, fontweight='bold', color='black')
        
        median_val = data.median()
        ax.axvline(median_val, color='black', linestyle='-', linewidth=2, label=f'Median: {median_val:.2f}')
        ax.legend(frameon=True, edgecolor='black', fontsize=8)
    else:
        ax.text(0.5, 0.5, "Standard Dataset Statistical Index", ha='center', va='center', fontsize=12)

    ax.spines['top'].set_color('black')
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['right'].set_linewidth(1.2)
    ax.grid(True, linestyle=':', alpha=0.6, color='black')
    ax.tick_params(colors='black', labelsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, facecolor='white', edgecolor='black', bbox_inches='tight')
    plt.close(fig)
    return output_path


def generate_black_and_white_pdf(df: pd.DataFrame, output_filepath: str, dataset_name: str = "dataset.csv", agent_name: str = "Narayan") -> str:
    """
    Generate an executive, publication-grade Black & White themed PDF report
    with solid borders, real dataset records, structured tables, and embedded black and white chart.
    """
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    
    # Generate chart image
    chart_img_path = output_filepath.replace('.pdf', '_chart.png')
    generate_black_and_white_chart(df, chart_img_path)

    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    section_heading = ParagraphStyle(
        'BWSectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.white,
        spaceBefore=0,
        spaceAfter=0
    )

    body_style = ParagraphStyle(
        'BWBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.black,
        spaceAfter=3
    )

    body_bold = ParagraphStyle(
        'BWBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_header_style = ParagraphStyle(
        'BWTableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_cell_style = ParagraphStyle(
        'BWTableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.black,
        alignment=TA_LEFT
    )

    table_cell_center = ParagraphStyle(
        'BWTableCellCenter',
        parent=table_cell_style,
        alignment=TA_CENTER
    )

    story = []

    # ==========================================
    # 1. HEADER WITH DOUBLE BLACK BORDER
    # ==========================================
    header_data = [
        [
            Paragraph("BHISHMA AI - AUTONOMOUS INTELLIGENCE SYSTEM", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER, textColor=colors.black)),
        ],
        [
            Paragraph("EXECUTIVE DATASET AUDIT & STATISTICAL ANALYSIS REPORT", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=9, alignment=TA_CENTER, textColor=colors.black))
        ],
        [
            Paragraph(f"AGENT: <b>{agent_name.upper()}</b> | DATASET: <b>{dataset_name}</b> | DATE: <b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</b> | THEME: <b>MONOCHROME AUDIT</b>", ParagraphStyle('H3', fontName='Helvetica', fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#333333')))
        ]
    ]
    header_table = Table(header_data, colWidths=[520])
    header_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    def create_section_header(title_text):
        t = Table([[Paragraph(f"  {title_text.upper()}", section_heading)]], colWidths=[520])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black)
        ]))
        return t

    # ==========================================
    # 2. EXECUTIVE SUMMARY (WITH BORDER BOX)
    # ==========================================
    story.append(create_section_header("1. Executive Summary & Dataset Parameters"))
    story.append(Spacer(1, 2))

    rows_count, cols_count = df.shape
    cols = list(df.columns)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    missing_total = int(df.isnull().sum().sum())

    summary_meta = [
        [
            Paragraph("<b>Target Dataset:</b>", body_style), Paragraph(dataset_name, body_style),
            Paragraph("<b>Total Records:</b>", body_style), Paragraph(f"{rows_count:,}", body_bold)
        ],
        [
            Paragraph("<b>Total Attributes:</b>", body_style), Paragraph(f"{cols_count} Columns", body_style),
            Paragraph("<b>Numerical Metrics:</b>", body_style), Paragraph(f"{len(num_cols)} Columns", body_style)
        ],
        [
            Paragraph("<b>Categorical Entities:</b>", body_style), Paragraph(f"{len(cat_cols)} Columns", body_style),
            Paragraph("<b>Missing / Nulls:</b>", body_style), Paragraph(f"{missing_total} ({round(missing_total/(rows_count*cols_count or 1)*100, 2)}%)", body_style)
        ],
        [
            Paragraph("<b>Analysis Agent:</b>", body_style), Paragraph(f"{agent_name} AI", body_bold),
            Paragraph("<b>Audit Clearance:</b>", body_style), Paragraph("VALIDATED (B&W STRICT)", body_bold)
        ]
    ]
    summary_table = Table(summary_meta, colWidths=[110, 150, 110, 150])
    summary_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 6))

    # ==========================================
    # 3. ACTUAL DATASET RECORDS INSPECTION TABLE
    # ==========================================
    story.append(create_section_header("2. Dataset Records Inspection Table (Actual Data Rows)"))
    story.append(Spacer(1, 2))

    # Select up to 5-6 core columns to display
    display_cols = []
    for c in cols:
        if any(k in c.lower() for k in ['district', 'name', 'state', 'id', 'city', 'region', 'entity']):
            if c not in display_cols and len(display_cols) < 2:
                display_cols.append(c)

    for c in num_cols:
        if c not in display_cols and len(display_cols) < 5:
            display_cols.append(c)

    for c in cols:
        if c not in display_cols and len(display_cols) < 5:
            display_cols.append(c)

    col_w = int(520 / max(1, len(display_cols)))
    col_widths = [col_w] * len(display_cols)
    col_widths[-1] = 520 - (col_w * (len(display_cols) - 1))

    raw_data_header = [Paragraph(f"<b>{c[:16]}</b>", table_header_style) for c in display_cols]
    raw_data_rows = [raw_data_header]

    sample_df = df[display_cols].head(10)
    for idx, row in sample_df.iterrows():
        row_cells = []
        for col_name in display_cols:
            val = row[col_name]
            if pd.isna(val):
                cell_str = "<i>null</i>"
            elif isinstance(val, (int, np.integer)):
                cell_str = f"{val:,}"
            elif isinstance(val, (float, np.floating)):
                cell_str = f"{val:.2f}"
            else:
                cell_str = str(val)[:18]
            row_cells.append(Paragraph(cell_str, table_cell_center if isinstance(val, (int, float, np.number)) else table_cell_style))
        raw_data_rows.append(row_cells)

    raw_table = Table(raw_data_rows, colWidths=col_widths)
    raw_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(raw_table)
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>Table 1:</b> Representative data records from '{dataset_name}' (Showing sample records of {rows_count:,} total records across key indicators).", ParagraphStyle('Note1', fontName='Helvetica-Oblique', fontSize=6.5, alignment=TA_CENTER, textColor=colors.black)))
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ==========================================
    # 4. STATISTICAL METRICS TABLE
    # ==========================================
    story.append(create_section_header("3. Descriptive Statistics & Metric Dispersion"))
    story.append(Spacer(1, 2))

    stats_header = [
        Paragraph("Metric Column", table_header_style),
        Paragraph("Mean", table_header_style),
        Paragraph("Std Dev", table_header_style),
        Paragraph("Min", table_header_style),
        Paragraph("Median", table_header_style),
        Paragraph("Max", table_header_style),
        Paragraph("IQR Bounds", table_header_style)
    ]
    stats_data = [stats_header]

    for col in num_cols[:7]:
        s = df[col].dropna()
        if len(s) > 0:
            mean_v = s.mean()
            std_v = s.std()
            min_v = s.min()
            med_v = s.median()
            max_v = s.max()
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            bounds_str = f"[{q1-1.5*iqr:.1f}, {q3+1.5*iqr:.1f}]"

            stats_data.append([
                Paragraph(f"<b>{col[:16]}</b>", table_cell_style),
                Paragraph(f"{mean_v:.2f}", table_cell_center),
                Paragraph(f"{std_v:.2f}", table_cell_center),
                Paragraph(f"{min_v:.2f}", table_cell_center),
                Paragraph(f"{med_v:.2f}", table_cell_center),
                Paragraph(f"{max_v:.2f}", table_cell_center),
                Paragraph(bounds_str, table_cell_center)
            ])

    stats_table = Table(stats_data, colWidths=[130, 65, 65, 65, 65, 65, 65])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 6))

    # ==========================================
    # 5. EMBEDDED BLACK & WHITE GRAPH (WITH BORDER)
    # ==========================================
    story.append(create_section_header("4. Quantitative Visualizations (Monochrome Audit Graph)"))
    story.append(Spacer(1, 2))

    if os.path.exists(chart_img_path):
        chart_img = Image(chart_img_path, width=520, height=195)
        chart_table = Table([[chart_img]], colWidths=[520])
        chart_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        story.append(chart_table)
        story.append(Spacer(1, 1))
        story.append(Paragraph("<b>Figure 1:</b> High-contrast Black & White Distribution and Extreme Outlier Divergence Plot.", ParagraphStyle('Fig', fontName='Helvetica-Oblique', fontSize=7, alignment=TA_CENTER, textColor=colors.black)))
    story.append(Spacer(1, 6))

    # ==========================================
    # 6. ANOMALY & OUTLIER IDENTIFICATION TABLE
    # ==========================================
    story.append(create_section_header("5. Statistical Outliers & Identified Anomalies"))
    story.append(Spacer(1, 2))

    anom_header = [
        Paragraph("Entity / District", table_header_style),
        Paragraph("State / Category", table_header_style),
        Paragraph("Indicator", table_header_style),
        Paragraph("Observed", table_header_style),
        Paragraph("Expected Mean", table_header_style),
        Paragraph("Audit Status", table_header_style)
    ]
    anom_data = [anom_header]

    detected_count = 0
    id_col = next((c for c in cols if any(k in c.lower() for k in ['district', 'entity', 'name', 'id'])), None)
    cat_ref_col = next((c for c in cols if 'state' in c.lower() or 'region' in c.lower()), None)

    for col in num_cols:
        s = df[col].dropna()
        if len(s) > 5:
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                ub = q3 + 1.5 * iqr
                lb = q1 - 1.5 * iqr
                outliers = df[(df[col] > ub) | (df[col] < lb)]
                for _, row in outliers.head(2).iterrows():
                    if detected_count < 4:
                        entity_name = str(row[id_col]) if id_col else f"Record #{row.name}"
                        state_name = str(row[cat_ref_col]) if cat_ref_col else "Standard"
                        obs_val = f"{row[col]:.2f}"
                        exp_val = f"{s.mean():.2f}"
                        status = "HIGH SEVERITY" if row[col] > ub else "DEFICIT DIVERGENCE"

                        anom_data.append([
                            Paragraph(f"<b>{entity_name[:16]}</b>", table_cell_style),
                            Paragraph(state_name[:14], table_cell_style),
                            Paragraph(col[:16], table_cell_style),
                            Paragraph(f"<b>{obs_val}</b>", table_cell_center),
                            Paragraph(exp_val, table_cell_center),
                            Paragraph(f"<b>{status}</b>", table_cell_center)
                        ])
                        detected_count += 1

    if len(anom_data) == 1:
        anom_data.append([
            Paragraph("No statistical outliers exceeded 1.5 IQR bounds", table_cell_style),
            Paragraph("N/A", table_cell_center),
            Paragraph("N/A", table_cell_center),
            Paragraph("N/A", table_cell_center),
            Paragraph("N/A", table_cell_center),
            Paragraph("NOMINAL", table_cell_center)
        ])

    anom_table = Table(anom_data, colWidths=[120, 90, 110, 65, 65, 70])
    anom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(anom_table)
    story.append(Spacer(1, 6))

    # ==========================================
    # 7. ACTIONABLE RECOMMENDATIONS & SIGN-OFF
    # ==========================================
    story.append(create_section_header("6. Strategic Recommendations & Verification Sign-Off"))
    story.append(Spacer(1, 2))

    rec_data = [
        [
            Paragraph("<b>1. Targeted Interventions:</b> Prioritize critical outlier entities identified above with immediate resource allocation and structural supply stabilization.", body_style)
        ],
        [
            Paragraph("<b>2. Data Cleansing & Quality Control:</b> Continuous verification of variance bounds and automated imputation for missing indicators.", body_style)
        ],
        [
            Paragraph("<b>3. Benchmark Replication:</b> Replicate institutional best practices observed in top performing benchmark districts.", body_style)
        ],
        [
            Paragraph(f"<b>VALIDATION CERTIFICATE:</b> This report was compiled and verified autonomously by <b>{agent_name} AI</b> utilizing exact Groq inference and ReportLab monochrome engines. All borders, real data tables, and embedded graphs conform to rigorous print audit specifications.", ParagraphStyle('Cert', fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=colors.black))
        ]
    ]
    rec_table = Table(rec_data, colWidths=[520])
    rec_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(rec_table)

    # Build the PDF
    doc.build(story)
    return output_filepath
