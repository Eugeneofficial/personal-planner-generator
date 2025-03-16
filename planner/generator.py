import os
import datetime
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, ListFlowable, ListItem
from planner.config import Config

def get_quote():
    """Fetch a random inspirational quote from the Quotable API."""
    try:
        response = requests.get(Config.QUOTABLE_API_URL)
        if response.status_code == 200:
            data = response.json()
            return f'"{data["content"]}" - {data["author"]}'
    except Exception as e:
        print(f"Error fetching quote: {e}")
    
    # Default quotes if API fails
    default_quotes = [
        '"The future depends on what you do today." - Mahatma Gandhi',
        '"The only way to do great work is to love what you do." - Steve Jobs',
        '"Believe you can and you\'re halfway there." - Theodore Roosevelt'
    ]
    import random
    return random.choice(default_quotes)

def get_weather_forecast(city):
    """Fetch weather forecast from OpenWeatherMap API."""
    if not Config.OPENWEATHERMAP_API_KEY:
        return None
    
    try:
        params = {
            'q': city,
            'appid': Config.OPENWEATHERMAP_API_KEY,
            'units': 'metric'
        }
        response = requests.get(Config.OPENWEATHERMAP_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching weather: {e}")
    
    return None

def generate_planner(name, time_range, quote, theme, style, components, habits=None):
    """Generate a personalized planner PDF."""
    # Create a unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{name.lower().replace(' ', '_')}_{time_range}_{timestamp}.pdf"
    output_path = os.path.join(Config.GENERATED_FOLDER, filename)
    
    # Get style settings
    style_settings = Config.STYLES.get(style, Config.STYLES['minimalist'])
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Add custom styles with unique names to avoid conflicts
    styles.add(ParagraphStyle(
        name='PlannerTitle',  # Changed from 'Title' to 'PlannerTitle'
        fontName=style_settings['font'],
        fontSize=24,
        textColor=style_settings['primary_color'],
        alignment=1,  # Center
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='PlannerSubtitle',  # Changed from 'Subtitle' to 'PlannerSubtitle'
        fontName=style_settings['font'],
        fontSize=16,
        textColor=style_settings['secondary_color'],
        alignment=1,  # Center
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='PlannerHeading',  # Changed from 'Heading' to 'PlannerHeading'
        fontName=style_settings['font'],
        fontSize=14,
        textColor=style_settings['primary_color'],
        spaceBefore=12,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='PlannerNormal',  # Changed from 'Normal' to 'PlannerNormal'
        fontName=style_settings['font'],
        fontSize=10,
        textColor=style_settings['primary_color']
    ))
    
    # Create content
    content = []
    
    # Cover page
    content.append(Paragraph(f"{name}'s Planner", styles['PlannerTitle']))
    content.append(Spacer(1, 12))
    
    # Theme
    content.append(Paragraph(theme, styles['PlannerSubtitle']))
    content.append(Spacer(1, 12))
    
    # Date range
    today = datetime.date.today()
    if time_range == 'day':
        date_str = today.strftime("%A, %B %d, %Y")
    elif time_range == 'week':
        end_date = today + datetime.timedelta(days=6)
        date_str = f"{today.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    else:  # month
        date_str = today.strftime("%B %Y")
    
    content.append(Paragraph(date_str, styles['PlannerSubtitle']))
    content.append(Spacer(1, 24))
    
    # Quote
    if not quote:
        quote = get_quote()
    content.append(Paragraph(quote, styles['PlannerNormal']))
    content.append(PageBreak())
    
    # Generate pages based on time range
    if time_range == 'day':
        content.extend(generate_day_page(today, styles, components, habits))
    elif time_range == 'week':
        for i in range(7):
            day = today + datetime.timedelta(days=i)
            content.extend(generate_day_page(day, styles, components, habits))
            if i < 6:  # Don't add page break after the last day
                content.append(PageBreak())
    else:  # month
        num_days = (today.replace(month=today.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day
        for i in range(num_days):
            day = today.replace(day=i+1)
            content.extend(generate_day_page(day, styles, components, habits))
            if i < num_days - 1:  # Don't add page break after the last day
                content.append(PageBreak())
    
    # Build the PDF
    doc.build(content)
    
    return output_path

def generate_day_page(date, styles, components, habits=None):
    """Generate a page for a single day."""
    content = []
    
    # Day header
    day_header = date.strftime("%A, %B %d, %Y")
    content.append(Paragraph(day_header, styles['PlannerTitle']))
    content.append(Spacer(1, 12))
    
    # Schedule section
    if components.get('schedule', False):
        content.append(Paragraph("Daily Schedule", styles['PlannerHeading']))
        
        # Create schedule table
        schedule_data = []
        schedule_data.append(['Time', 'Activity'])
        
        for hour in range(6, 23):  # 6 AM to 10 PM
            am_pm = 'AM' if hour < 12 else 'PM'
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            
            time_str = f"{display_hour} {am_pm}"
            schedule_data.append([time_str, ''])
        
        schedule_table = Table(schedule_data, colWidths=[2*cm, 12*cm])
        schedule_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), styles['PlannerHeading'].fontName),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
        ]))
        
        content.append(schedule_table)
        content.append(Spacer(1, 12))
    
    # To-do list section
    if components.get('todo', False):
        content.append(Paragraph("To-Do List", styles['PlannerHeading']))
        
        # Create to-do table
        todo_data = []
        for i in range(10):
            todo_data.append(['□', ''])
        
        todo_table = Table(todo_data, colWidths=[1*cm, 13*cm])
        todo_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), styles['PlannerNormal'].fontName),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        
        content.append(todo_table)
        content.append(Spacer(1, 12))
    
    # Habit tracker section
    if components.get('habit_tracker', False) and habits:
        content.append(Paragraph("Habit Tracker", styles['PlannerHeading']))
        
        # Create habit tracker table
        habit_data = [['Habit', 'Done']]
        for habit in habits:
            habit_data.append([habit, '□'])
        
        habit_table = Table(habit_data, colWidths=[12*cm, 2*cm])
        habit_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), styles['PlannerHeading'].fontName),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
        ]))
        
        content.append(habit_table)
        content.append(Spacer(1, 12))
    
    # Notes section
    if components.get('notes', False):
        content.append(Paragraph("Notes", styles['PlannerHeading']))
        
        # Create notes table (just a big empty box)
        notes_data = [['']]
        notes_table = Table(notes_data, colWidths=[14*cm], rowHeights=[8*cm])
        notes_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        content.append(notes_table)
    
    return content 