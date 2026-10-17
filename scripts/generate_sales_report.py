import hashlib
_md5 = hashlib.md5
def _safe_md5(*a, **k):
    k.pop("usedforsecurity", None)
    return _md5(*a, **k)
hashlib.md5 = _safe_md5
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime

def read_results(filepath):
    rows = []
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split('\t')
                    if len(parts) == 2:
                        rows.append((parts[0], parts[1]))
    except:
        pass
    return rows

doc = SimpleDocTemplate("/opt/results/sales_report.pdf", pagesize=A4)
styles = getSampleStyleSheet()
elements = []

title_style = ParagraphStyle('Title', fontSize=18,
    textColor=colors.HexColor('#1a1a2e'),
    spaceAfter=6, fontName='Helvetica-Bold', alignment=1)
sub_style = ParagraphStyle('Sub', fontSize=9,
    textColor=colors.grey, spaceAfter=4, alignment=1)

elements.append(Paragraph("Retail Sales & Inventory Analysis Report", title_style))
elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", sub_style))
elements.append(Paragraph("Apache Hadoop MapReduce | 3-Node Distributed Cluster on Docker", sub_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Distributed Cluster Configuration", styles['Heading2']))
cluster_data = [
    ['Component', 'Details'],
    ['NameNode',   'namenode - Master (HDFS + YARN ResourceManager)'],
    ['DataNode 1', 'datanode1 - Worker (Storage + Map tasks)'],
    ['DataNode 2', 'datanode2 - Worker (Storage + Map tasks)'],
    ['DataNode 3', 'datanode3 - Worker (Storage + Map tasks)'],
    ['Replication','3 - fault tolerance across nodes'],
    ['Reducers',   '3 - parallel output partitions'],
]
ct = Table(cluster_data, colWidths=[2*inch, 4*inch])
ct.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1a2e')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,-1), 9),
    ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4ff')]),
]))
elements.append(ct)
elements.append(Spacer(1, 0.3*inch))

elements.append(Paragraph("Job 1: Revenue Analysis by Category", styles['Heading2']))
sales = read_results('/opt/results/sales_final.txt')
t1_data = [['Category', 'Total Revenue']]
for key, val in sales:
    try:
        revenue = val.split('=')[1].strip()
        t1_data.append([key, revenue])
    except:
        continue
t1 = Table(t1_data, colWidths=[3*inch, 2*inch])
t1.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1a2e')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,-1), 9),
    ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4ff')]),
    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
]))
elements.append(t1)
elements.append(Spacer(1, 0.3*inch))

elements.append(Paragraph("Job 2: Inventory Gap Analysis (Stock vs Demand)", styles['Heading2']))
stock = read_results('/opt/results/stock_final.txt')
t2_data = [['Product ID', 'Avg Gap', 'Status']]
style_list = [
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1a2e')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,-1), 9),
    ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
]
for key, val in stock:
    try:
        gap_part = val.split('(')[0]
        status = val.split('(')[1].replace(')', '').strip()
        gap = gap_part.split('=')[1].strip()
        t2_data.append([key, gap, status])
        i = len(t2_data) - 1
        if 'Understock' in status:
            style_list.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor('#ffe0e0')))
        elif 'Overstock' in status:
            style_list.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor('#fff3cd')))
        else:
            style_list.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor('#d4edda')))
    except:
        continue
t2 = Table(t2_data, colWidths=[2*inch, 1.5*inch, 2*inch], repeatRows=1)
t2.setStyle(TableStyle(style_list))
elements.append(t2)
elements.append(Spacer(1, 0.3*inch))

elements.append(Paragraph(
    "Distributed Retail Analytics Project - Hadoop + Docker + MapReduce",
    ParagraphStyle('footer', fontSize=8, textColor=colors.grey, alignment=1)))

doc.build(elements)
print("PDF generated: /opt/results/sales_report.pdf")
