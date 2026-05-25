import os
import json

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class ItineraryExporter:
    """
    Utility module for exporting detailed tourist itineraries into beautiful formats:
    - HTML (Visual travel brochure style)
    - PDF (Standard professional academic report style, using ReportLab)
    """
    
    @staticmethod
    def export_to_html(path, graph, file_path, distance, cost, time_mins, success_prob, algorithm_name):
        """Exports a premium styled HTML travel itinerary brochure."""
        stops_html = ""
        for index, loc_id in enumerate(path):
            loc = graph.get_location(loc_id)
            if not loc:
                continue
            
            # Formulate hotel list
            hotels_html = ""
            for h in loc.hotels:
                hotels_html += f"<li><b>{h['name']}</b> (Rating: {h['rating']} ⭐, Approx: ₹{h['price']}/night)</li>"
            
            stops_html += f"""
            <div class="stop-card">
                <div class="stop-header">
                    <span class="stop-badge">Stop {index + 1}</span>
                    <h3>{loc.name}</h3>
                    <span class="rating-badge">{loc.rating} ⭐</span>
                </div>
                <p class="description">{loc.description}</p>
                <div class="hotels-section">
                    <h4>Recommended Accommodations:</h4>
                    <ul>
                        {hotels_html}
                    </ul>
                </div>
            </div>
            """
            
            if index < len(path) - 1:
                curr_loc = graph.get_location(loc_id)
                conn = curr_loc.get_connection(path[index+1]) if curr_loc else None
                if conn:
                    stops_html += f"""
                    <div class="route-connector">
                        <div class="connector-line"></div>
                        <span class="connector-info">🛣️ {conn.distance} km | 💰 ₹{conn.cost} | ⏱️ {conn.base_time} mins</span>
                        <div class="connector-line"></div>
                    </div>
                    """

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Tourist Route Planner - Itinerary</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f0f15;
            color: #e2e8f0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #1a1a24;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            border: 1px solid #2e2e3f;
        }}
        h1 {{
            text-align: center;
            color: #00f0ff;
            margin-bottom: 5px;
            font-size: 2.5em;
        }}
        .subtitle {{
            text-align: center;
            color: #a0aec0;
            margin-top: 0;
            margin-bottom: 25px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            background-color: #12121a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px dashed #4a5568;
        }}
        .summary-card {{
            text-align: center;
        }}
        .summary-card label {{
            display: block;
            font-size: 0.85em;
            color: #a0aec0;
            text-transform: uppercase;
        }}
        .summary-card value {{
            display: block;
            font-size: 1.3em;
            font-weight: bold;
            color: #2ec4b6;
            margin-top: 5px;
        }}
        .stop-card {{
            background-color: #20202e;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid #00f0ff;
        }}
        .stop-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #2d3748;
            padding-bottom: 10px;
        }}
        .stop-badge {{
            background-color: #00f0ff;
            color: #1a1a24;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        .rating-badge {{
            background-color: #ecc94b;
            color: #1a1a24;
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: bold;
        }}
        h3 {{
            margin: 0;
            color: #fff;
            flex-grow: 1;
            margin-left: 15px;
        }}
        .description {{
            color: #cbd5e0;
            line-height: 1.6;
        }}
        .hotels-section {{
            margin-top: 15px;
            background-color: #12121a;
            padding: 10px 15px;
            border-radius: 6px;
        }}
        .hotels-section h4 {{
            margin-top: 0;
            color: #00f0ff;
            font-size: 0.95em;
        }}
        .hotels-section ul {{
            margin: 0;
            padding-left: 20px;
            color: #a0aec0;
        }}
        .route-connector {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 15px 0;
        }}
        .connector-line {{
            flex-grow: 1;
            height: 2px;
            background: linear-gradient(90deg, transparent, #4a5568, transparent);
        }}
        .connector-info {{
            padding: 5px 15px;
            background-color: #12121a;
            border-radius: 20px;
            font-size: 0.85em;
            color: #2ec4b6;
            border: 1px solid #4a5568;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 0.8em;
            color: #718096;
            border-top: 1px solid #2d3748;
            padding-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>TOURIST ITINERARY</h1>
        <p class="subtitle">AI-Optimized Route Plan via {algorithm_name}</p>
        
        <div class="summary-grid">
            <div class="summary-card">
                <label>Distance</label>
                <value>{round(distance, 1)} km</value>
            </div>
            <div class="summary-card">
                <label>Budget Cost</label>
                <value>₹{round(cost, 1)}</value>
            </div>
            <div class="summary-card">
                <label>Est. Travel Time</label>
                <value>{int(time_mins // 60)}h {int(time_mins % 60)}m</value>
            </div>
            <div class="summary-card">
                <label>Success Probability</label>
                <value>{round(success_prob * 100, 1)}%</value>
            </div>
        </div>
        
        <div class="itinerary-flow">
            {stops_html}
        </div>
        
        <div class="footer">
            Generated completely offline by Tourist Route Planner AI Core &copy; 2026.
        </div>
    </div>
</body>
</html>
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    @staticmethod
    def export_to_pdf(path, graph, file_path, distance, cost, time_mins, success_prob, algorithm_name):
        """Exports a professional PDF itinerary document."""
        if not PDF_AVAILABLE:
            # Graceful fallback: Export as beautiful TXT report instead
            txt_path = file_path.replace(".pdf", ".txt")
            ItineraryExporter.export_to_txt(path, graph, txt_path, distance, cost, time_mins, success_prob, algorithm_name)
            return False, txt_path

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styled ParagraphStyles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                textColor=colors.HexColor('#1a365d'),
                fontSize=24,
                leading=28,
                alignment=1, # Center
                spaceAfter=6
            )
            subtitle_style = ParagraphStyle(
                'SubTitleStyle',
                parent=styles['Normal'],
                textColor=colors.HexColor('#4a5568'),
                fontSize=11,
                leading=14,
                alignment=1, # Center
                spaceAfter=20
            )
            h3_style = ParagraphStyle(
                'H3Style',
                parent=styles['Heading3'],
                textColor=colors.HexColor('#2b6cb0'),
                fontSize=14,
                leading=18,
                spaceBefore=10,
                spaceAfter=6
            )
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                textColor=colors.HexColor('#2d3748'),
                fontSize=10,
                leading=14,
                spaceAfter=6
            )
            table_header_style = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                textColor=colors.white,
                fontSize=10,
                leading=12,
                fontName='Helvetica-Bold'
            )
            table_cell_style = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                textColor=colors.HexColor('#2d3748'),
                fontSize=9,
                leading=12
            )

            story = []
            story.append(Paragraph("AI TOURIST ROUTE PLANNER", title_style))
            story.append(Paragraph(f"Optimized Travel Itinerary using {algorithm_name}", subtitle_style))
            story.append(Spacer(1, 10))

            # Summary Table
            summary_data = [
                [Paragraph("<b>Metric</b>", table_header_style), Paragraph("<b>Value</b>", table_header_style)],
                [Paragraph("Total Route Distance", table_cell_style), Paragraph(f"{round(distance, 1)} km", table_cell_style)],
                [Paragraph("Estimated Transport Cost", table_cell_style), Paragraph(f"INR {round(cost, 1)}", table_cell_style)],
                [Paragraph("Estimated Travel Time", table_cell_style), Paragraph(f"{int(time_mins // 60)} hrs {int(time_mins % 60)} mins", table_cell_style)],
                [Paragraph("Route Traversal Safety Probability", table_cell_style), Paragraph(f"{round(success_prob * 100, 1)}%", table_cell_style)]
            ]
            
            t = Table(summary_data, colWidths=[200, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2b6cb0')),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('TOPPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f7fafc')]),
                ('BOTTOMPADDING', (0,1), (-1,-1), 6),
                ('TOPPADDING', (0,1), (-1,-1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 20))

            # Stops Flow
            story.append(Paragraph("Route Breakdown", h3_style))
            story.append(Spacer(1, 5))

            for index, loc_id in enumerate(path):
                loc = graph.get_location(loc_id)
                if not loc:
                    continue
                
                stop_title = f"<b>Stop {index+1}: {loc.name} (Rating: {loc.rating} ⭐)</b>"
                story.append(Paragraph(stop_title, h3_style))
                story.append(Paragraph(loc.description, body_style))
                
                # Accommodations details
                hotels_list = []
                for h in loc.hotels:
                    hotels_list.append(f"{h['name']} (Rating: {h['rating']} ⭐, Tariff: INR {h['price']}/night)")
                hotels_para = f"<i>Suggested Hotels:</i> {', '.join(hotels_list)}"
                story.append(Paragraph(hotels_para, body_style))
                story.append(Spacer(1, 10))
                
                # Connection line (if not final stop)
                if index < len(path) - 1:
                    curr_loc = graph.get_location(loc_id)
                    conn = curr_loc.get_connection(path[index+1]) if curr_loc else None
                    if conn:
                        conn_text = f"<b>Road Travel:</b> -> {conn.distance} km | INR {conn.cost} | Time: {conn.base_time} minutes"
                        story.append(Paragraph(conn_text, body_style))
                        story.append(Spacer(1, 10))

            doc.build(story)
            return True, file_path
        except Exception as e:
            print(f"Error compiling PDF: {e}")
            txt_path = file_path.replace(".pdf", ".txt")
            ItineraryExporter.export_to_txt(path, graph, txt_path, distance, cost, time_mins, success_prob, algorithm_name)
            return False, txt_path

    @staticmethod
    def export_to_txt(path, graph, file_path, distance, cost, time_mins, success_prob, algorithm_name):
        """Exports a clean plain text itinerary."""
        content = "="*60 + "\n"
        content += "             TOURIST TRAVEL ITINERARY REPORT\n"
        content += f"      Generated via AI Routing Engine ({algorithm_name})\n"
        content += "="*60 + "\n\n"
        content += f"Total Route Distance  : {round(distance, 1)} km\n"
        content += f"Estimated Travel Cost : INR {round(cost, 1)}\n"
        content += f"Estimated Time        : {int(time_mins // 60)} hours {int(time_mins % 60)} minutes\n"
        content += f"Safety Probability    : {round(success_prob * 100, 1)}%\n\n"
        content += "="*60 + "\n\n"
        
        for index, loc_id in enumerate(path):
            loc = graph.get_location(loc_id)
            if not loc:
                continue
            content += f"STOP {index + 1}: {loc.name}\n"
            content += f"Rating  : {loc.rating} / 5.0 ⭐\n"
            content += f"History : {loc.description}\n"
            content += "Recommended Lodging:\n"
            for h in loc.hotels:
                content += f" - {h['name']} (Rating: {h['rating']} ⭐, Price: INR {h['price']}/night)\n"
            content += "\n"
            
            if index < len(path) - 1:
                curr_loc = graph.get_location(loc_id)
                conn = curr_loc.get_connection(path[index+1]) if curr_loc else None
                if conn:
                    content += f"  >>> Travel along highway: {conn.distance} km | Cost: INR {conn.cost} | Time: {conn.base_time} mins <<<\n\n"
        
        content += "="*60 + "\n"
        content += "Generated Completely Offline. Have a safe journey!\n"
        content += "="*60 + "\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
