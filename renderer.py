"""
Wallpaper rendering functionality for TaskPaper.
"""
import os
import datetime as dt
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config import TZ, MAX_CARD_WIDTH, MAX_CARD_HEIGHT
from models import CalItem, UrgentTask, DisplayItem


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load system font with fallbacks."""
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/SFNSRounded.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_vertical_gradient(size: Tuple[int, int], top: Tuple[int, int, int], bottom: Tuple[int, int, int]) -> Image:
    """Create vertical gradient background."""
    W, H = size
    base = Image.new("RGB", (W, H), bottom)
    top_img = Image.new("RGB", (W, H), top)
    mask = Image.linear_gradient("L").resize((W, H))
    return Image.composite(top_img, base, mask)


def apply_vignette(img: Image, strength: int = 180) -> Image:
    """Apply vignette effect to image."""
    W, H = img.size
    vignette = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(vignette)
    cx, cy = W // 2, H // 2
    max_r = int((W**2 + H**2) ** 0.5 // 2)
    
    for r in range(max_r, 0, -max(1, max_r // 40)):
        alpha = int((1 - r / max_r) * strength)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=alpha)
    
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=max(10, min(W, H) // 60)))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    overlay.putalpha(vignette)
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    return out


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines: List[str] = []
    current = []
    
    for word in words:
        test = (" ".join(current + [word])).strip()
        if draw.textlength(test, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    
    if current:
        lines.append(" ".join(current))
    
    return lines


def draw_card(draw: ImageDraw.ImageDraw, xy: Tuple[int, int, int, int], radius=24, 
              fill=(0, 0, 0, 200), outline=(255, 255, 255, 80)):
    """Draw rounded rectangle card."""
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2)


def draw_text_with_shadow(draw: ImageDraw.ImageDraw, xy: Tuple[int, int], text: str, 
                         font: ImageFont.FreeTypeFont, fill: Tuple[int, int, int, int], 
                         shadow_offset: int = 2):
    """Draw text with shadow effect."""
    x, y = xy
    # Draw shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 120))
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)


def prepare_display_items(tasks: List[UrgentTask], events: List[CalItem]) -> List[DisplayItem]:
    """
    Prepare items for display, choosing between tasks and events.
    
    Args:
        tasks: Processed urgent tasks
        events: Raw calendar events
        
    Returns:
        List of items to display on wallpaper
    """
    display_items = []
    
    if tasks:
        # Show processed tasks
        for task in tasks[:6]:
            when = f"{task.time} • " if task.time else ""
            display_items.append(DisplayItem(
                text=f"{when}{task.title}",
                source='calendar',
                priority=task.priority,
                type='task'
            ))
    else:
        # Fallback: show raw events
        for event in events[:6]:
            start = event.start.strftime("%H:%M") if event.start else "--"
            end = event.end.strftime("%H:%M") if event.end else "--"
            display_items.append(DisplayItem(
                text=f"{start}–{end}  {event.summary}",
                source='calendar',
                priority=3,
                type='event'
            ))
    
    return display_items


def render_wallpaper(tasks: List[UrgentTask], events: List[CalItem], size: Tuple[int, int], out_path: str):
    """
    Render wallpaper with tasks and events.
    
    Args:
        tasks: Urgent tasks to display
        events: Calendar events for fallback
        size: Wallpaper dimensions (width, height)
        out_path: Output file path
    """
    W, H = size
    
    # Create background
    bg = draw_vertical_gradient((W, H), (34, 40, 55), (14, 18, 26))
    img = bg.convert("RGBA")
    img = apply_vignette(img, strength=160)
    
    d = ImageDraw.Draw(img)
    
    # Layout settings
    margin = 144  # 2 inches at 72 DPI
    base = max(16, min(28, int(min(W, H) / 70)))
    
    # Fonts
    title_font = load_font(base * 3)
    h1 = load_font(int(base * 2.2))
    h2 = load_font(int(base * 1.6))
    small = load_font(int(base * 1.2))
    
    # Header (date)
    now = dt.datetime.now(TZ)
    header = f"{now:%A, %b %d}"
    draw_text_with_shadow(d, (margin, margin), header, title_font, (255, 255, 255, 255), 3)
    
    # Card layout with size constraints
    available_width = W - 2 * margin
    card_width = min(MAX_CARD_WIDTH, available_width)
    left = margin + (available_width - card_width) // 2  # Center horizontally
    col_w = card_width
    top = margin + int(base * 5)
    card_pad = int(base * 1.5)
    
    # Prepare items to display
    display_items = prepare_display_items(tasks, events)
    
    # Calculate card height
    total_items = len(display_items) if display_items else 1
    line_height = int(h2.size * 1.4)
    min_card_height = 150
    content_height = int(card_pad * 3.5) + (total_items * line_height) + int(base * 2)
    card_h = max(min_card_height, min(content_height, MAX_CARD_HEIGHT))
    
    # Draw card
    draw_card(d, (left, top, left + col_w, top + card_h), radius=28)
    
    # Card header
    draw_text_with_shadow(d, (left + card_pad, top + card_pad), "Today's Agenda", h1, (255, 255, 255, 255), 2)
    
    # Content area
    y = top + int(card_pad * 3.0)  # Extra space after title
    list_left = left + int(card_pad * 1.2)
    text_w = col_w - int(card_pad * 2.4)
    
    if display_items:
        _render_items(d, display_items, list_left, y, text_w, h2, small, line_height)
    else:
        # Show appropriate empty message
        if not events:
            message = "You're all set for the day! 🌟"
            color = (185, 255, 185, 255)  # Light green
        else:
            message = "No urgent items right now ✨"
            color = (200, 220, 255, 255)  # Light blue
        
        draw_text_with_shadow(d, (list_left, y), message, h2, color, 1)
    
    # Save wallpaper
    img = img.convert("RGB")
    img.save(out_path, "PNG", optimize=True)


def _render_items(draw: ImageDraw.ImageDraw, items: List[DisplayItem], list_left: int, 
                 start_y: int, text_w: int, h2_font: ImageFont.FreeTypeFont, 
                 small_font: ImageFont.FreeTypeFont, line_height: int):
    """Render display items on the wallpaper."""
    y = start_y
    
    for item in items:
        # Calendar icon and colors
        icon = "🕐"
        icon_color = (100, 150, 255, 255)
        priority_colors = {
            1: (100, 200, 100), 2: (150, 200, 100), 3: (200, 200, 100), 
            4: (255, 180, 100), 5: (255, 120, 120)
        }
        priority_color = priority_colors.get(item.priority, (100, 150, 255))
        
        # Draw source icon
        draw_text_with_shadow(draw, (list_left - 32, y), icon, small_font, icon_color, 1)
        
        # Draw priority dot for tasks
        if item.type == 'task':
            dot_x = list_left - 12
            dot_y = y + int(h2_font.size * 0.3)
            draw.ellipse((dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4), fill=priority_color)
        
        # Format and wrap text
        lines = wrap_text(draw, item.text, h2_font, text_w)
        
        for line_idx, line in enumerate(lines):
            indent = 0 if line_idx == 0 else 24
            draw_text_with_shadow(draw, (list_left + indent, y), line, h2_font, (255, 255, 255, 255), 1)
            y += line_height
        
        y += int(h2_font.size * 0.2)  # Small gap between items
