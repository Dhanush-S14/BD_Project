import csv
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

sales = read_results('/opt/results/sales_final.txt')
with open('/opt/results/sales_analysis.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Category', 'TotalRevenue', 'GeneratedAt'])
    for key, val in sales:
        try:
            revenue = val.split('=')[1].strip()
            writer.writerow([key.strip(), revenue, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        except:
            continue
print("sales_analysis.csv generated")

stock = read_results('/opt/results/stock_final.txt')
with open('/opt/results/stock_analysis.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ProductID', 'AverageGap', 'StockStatus', 'GeneratedAt'])
    for key, val in stock:
        try:
            gap_part = val.split('(')[0]
            status_part = val.split('(')[1].replace(')', '').strip()
            gap = gap_part.split('=')[1].strip()
            writer.writerow([key.strip(), gap, status_part, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        except:
            continue
print("stock_analysis.csv generated")
print("Both CSVs saved to /opt/results/")
