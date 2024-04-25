import dash
from dash import html, dcc
import plotly.express as px

def generate_top_section_report(top_section, top_section_count):
    app = dash.Dash(__name__)

    # Create a bar chart using Plotly Express
    fig = px.bar(x=[top_section], y=[top_section_count], labels={'x': 'Section', 'y': 'Number of Articles'})

    # Create the HTML layout for the report
    app.layout = html.Div([
        html.H1('Top Section Report'),
        html.P(f'The section with the most articles about Justin Trudeau is: {top_section}'),
        html.P(f'Number of articles in the {top_section} section: {top_section_count}'),
        html.Div([
            dcc.Graph(figure=fig)
        ])
    ])

    # Save the report as an HTML file
    app.write_html('reports/top_section_report.html')