from dash import html

# Define the GitHub URL
github_url = "https://github.com/MatthieuRu"  # Replace with your actual GitHub URL

# Define CSS styles for the footer
footer_style = {
    "border": "1px solid #ccc",  # Add a border at the top
    "text-align": "center",  # Center-align the text
    "padding": "10px",  # Add some padding for spacing
    "background-color": "#f2f2f2",  # Set a background color
}


def get_footer():
    footer = html.Footer(
        html.A(html.I(className="fab fa-github"), href=github_url, target="_blank"),
        style=footer_style,
    )
    return footer
