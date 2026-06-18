import time
from pathlib import Path
from typing import Union, List
import pandas as pd

# Lazy import definitions for optional dependencies
# This prevents the whole file from crashing if Selenium or Plotly isn't installed in a specific environment
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

def sanitize_plotly_layout(fig) -> None:
    """
    Fixes Plotly serialization issues by converting raw Pandas Timestamps 
    hidden in layout shapes to string format.
    """
    if hasattr(fig, "layout") and fig.layout.shapes:
        for shape in fig.layout.shapes:
            if isinstance(shape.x0, pd.Timestamp):
                shape.x0 = shape.x0.strftime("%Y-%m-%d")
            if isinstance(shape.x1, pd.Timestamp):
                shape.x1 = shape.x1.strftime("%Y-%m-%d")


def save_plotly_figure_with_fallback(fig, output_path: Union[str, Path], scale: int = 2) -> bool:
    """
    Attempts to save a Plotly figure cleanly as a PNG using Kaleido.
    Falls back to saving an interactive HTML file if Kaleido fails or hangs.
    
    Returns:
        bool: True if PNG export succeeded, False if it fell back to HTML.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Clean up layout timestamps
    sanitize_plotly_layout(fig)

    try:
        fig.write_image(str(output_path), format="png", scale=scale)
        print(f"Successfully saved figure directly to {output_path}")
        return True
    except Exception as e:
        html_path = output_path.with_suffix(".html")
        fig.write_html(str(html_path))
        print(f"PNG export failed ({e}). Saved instead as interactive HTML: {html_path}")
        return False


def save_plotly_via_selenium(
    fig, 
    primary_png_path: Union[str, Path], 
    secondary_png_paths: List[Union[str, Path]] = None,
    delay: float = 2.0,
    window_size: tuple = (1600, 1000)
) -> None:
    """
    Renders a Plotly figure to a temporary HTML file and uses Selenium 
    to capture a high-resolution, perfectly-bounded PNG element screenshot.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By

    primary_png_path = Path(primary_png_path)
    primary_png_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Gather all destination paths
    secondary_paths = [Path(p) for p in (secondary_png_paths or [])]
    all_png_paths = [primary_png_path] + secondary_paths

    # Create temporary HTML path next to the primary PNG destination
    html_path = primary_png_path.with_suffix(".html")
    
    # Clean and write HTML Source locally
    sanitize_plotly_layout(fig)
    fig.write_html(str(html_path))
    print(f"Base HTML saved safely to: {html_path}")

    # Configure Local Selenium Environment
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        driver.set_window_size(window_size[0], window_size[1])
        file_url = f"file:///{html_path.resolve()}"
        driver.get(file_url)
        
        # Give Plotly JS Engine a moment to execute layout transformations
        time.sleep(delay) 
        
        try:
            # TARGETING FIX: Locate the specific Plotly graph container element
            plotly_graph_div = driver.find_element(By.CLASS_NAME, "plotly-graph-div")
            
            # Snap the screenshot from the specific element node
            for path in all_png_paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                plotly_graph_div.screenshot(str(path))
            print(f"Success! Bounded high-res PNG saved to {len(all_png_paths)} location(s).")

        except Exception as e:
            print(f"Target element capture failed ({e}). Falling back to viewport snapshot...")
            for path in all_png_paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                driver.save_screenshot(str(path))

    except Exception as e:
        print(f"Selenium execution error: {e}")
    finally:
        driver.quit()
        #Clean up the temporary HTML file if you don't want to keep it
        if html_path.exists(): html_path.unlink()