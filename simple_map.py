import dash 
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto

from copy import deepcopy
from SecretColors import Palette
from graph_generator import graph

color_palette = Palette("material")

overview_stylesheet = [
    {
        # Group selectors
        'selector': 'node',
        'style': {
            'width': '30px',
            'height': '30px',
            'background-color': '#f5a44e',
            # 'background-color': '#FF7216',
            'background-opacity': 1,
            'label': 'data(label)',
            # 'color': '#001345',
            'color': '#ffffff',
            'text-halign': 'center',
            'text-valign': 'center',
            'text-wrap': 'wrap',
            'font-size': '10px',
            'font-family': ['Roboto', 'Courier', 'monospace'],
            'font-weight':'light',
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': color_palette.pink(shade=60),
            'width': 1,
            'curve-style': 'bezier',
            'target-arrow-color': color_palette.pink(shade=60),
            'target-arrow-shape': 'triangle',
        }
    },
]

def get_color_coded_style_sheet(max_depth=1, color_dict=dict()):
    output = deepcopy(overview_stylesheet)
    output[1]['style']['line-color'] = '#' + color_dict.get('arrow_color', 'fbc02d')
    output[1]['style']['target-arrow-color'] = '#' + color_dict.get('arrow_head_color', 'fbc02d')

    class_selector_template = {
        'selector': '.depth_0',  # Depth of nodes that shall apply this color selector.
        'style': {
            'background-color': '#000000',  # Color in Hex
            'line-color': '#000000'
        }
    }

    first_color_hex = '#' + color_dict.get('first_color_hex', color_palette.blue(shade=60))
    second_color_hex = '#' + color_dict.get('second_color_hex', color_palette.pink(shade=60))

    # Generate a random list of gradient colors in Hex
    colors = color_palette.color_between(first_color_hex, second_color_hex, max_depth + 1)

    # colors = color_palette.random(max_depth + 2)

    for depth in range(max_depth + 1):
        class_selector = deepcopy(class_selector_template)
        class_selector['selector'] = '.depth_' + str(depth)
        class_selector['style']['background-color'] = colors[depth]
        class_selector['style']['line-color'] = colors[depth]
        output.append(class_selector)

    return output

app = dash.Dash(__name__)
app.layout = html.Div([dcc.Location(id='url', refresh=False), html.Div(id='page-content')])

# Sketchy way to retrieve GET parameters while using Dash.
# See https://community.plotly.com/t/how-to-use-url-query-strings-inside-dash/6535/10.
# Also see https://github.com/GibbsConsulting/django-plotly-dash/issues/57
@app.callback(
    dash.dependencies.Output('page-content', 'children'), 
    [dash.dependencies.Input('url', 'href')]
)
def display_page(href):
    href = str(href).replace('%20', ' ')
    attributes = href.split('?')[1]
    attribute_pairs = attributes.split('&')
    attribute_dictionary = dict(map(lambda pair: pair.split('='), attribute_pairs))
    # print(attribute_dictionary)

    for required_attribute in ['courses', 'courses_excluded']:
        if required_attribute not in attribute_dictionary.keys():
            return f"API Error: the GET parameter {required_attribute} is required but isn't found."

    courses = attribute_dictionary['courses'].split(',')
    courses_excluded = attribute_dictionary['courses_excluded'].split(',')

    nodes = graph.get_elements(graph.learning_path(courses=courses, courses_excluded=courses_excluded))
    max_depth = 0
    for element in nodes:
        if 'classes' in element.keys():
            try:
                depth = element['classes'][6]
                max_depth = max(int(depth), max_depth)
            except IndexError:
                continue

    course_path_graph=cyto.Cytoscape(
            id='course_path_graph',
            layout={'name':'cose'},
            style={
                'width': '100%',
                'height': '100vh',
            },
            zoom= 1.2,
            minZoom= 0.3,
            maxZoom= 1.5,
            stylesheet=get_color_coded_style_sheet(max_depth=max_depth, color_dict=attribute_dictionary),
            elements=nodes
        )

    return course_path_graph

if __name__ == '__main__':
    app.run_server(port=8000, host="0.0.0.0")