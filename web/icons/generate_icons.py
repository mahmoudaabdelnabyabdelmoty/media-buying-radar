from PIL import Image, ImageDraw
import math

def create_radar_icon(size, filename):
    # Create image with transparent or deep background
    img = Image.new("RGBA", (size, size), (10, 14, 23, 255)) # Dark navy #0a0e17
    draw = ImageDraw.Draw(img)
    
    center = size / 2
    radius = size * 0.42
    
    # Outer circle gradient-like rim
    draw.ellipse([center - radius, center - radius, center + radius, center + radius], outline=(0, 229, 255, 180), width=max(2, int(size * 0.015)))
    
    # Middle circle
    r2 = radius * 0.68
    draw.ellipse([center - r2, center - r2, center + r2, center + r2], outline=(0, 200, 240, 100), width=max(1, int(size * 0.01)))
    
    # Inner circle
    r3 = radius * 0.35
    draw.ellipse([center - r3, center - r3, center + r3, center + r3], outline=(0, 240, 255, 120), width=max(1, int(size * 0.01)))
    
    # Crosshairs
    draw.line([center - radius, center, center + radius, center], fill=(0, 229, 255, 70), width=max(1, int(size * 0.008)))
    draw.line([center, center - radius, center, center + radius], fill=(0, 229, 255, 70), width=max(1, int(size * 0.008)))
    
    # Radar sweep sector (wedge)
    wedge_overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    wedge_draw = ImageDraw.Draw(wedge_overlay)
    
    # Draw sweep rays
    steps = 45
    for i in range(steps):
        angle = -45 + i * (60 / steps)
        rad = math.radians(angle)
        alpha = int(220 * (i / steps))
        x = center + radius * math.cos(rad)
        y = center + radius * math.sin(rad)
        wedge_draw.line([center, center, x, y], fill=(0, 240, 255, alpha), width=max(2, int(size * 0.02)))
        
    img = Image.alpha_composite(img, wedge_overlay)
    draw = ImageDraw.Draw(img)
    
    # Target blips (detected points)
    # Target 1 (green/cyan)
    t1_x = center + radius * 0.45 * math.cos(math.radians(-15))
    t1_y = center + radius * 0.45 * math.sin(math.radians(-15))
    draw.ellipse([t1_x - size*0.035, t1_y - size*0.035, t1_x + size*0.035, t1_y + size*0.035], fill=(0, 255, 180, 255))
    
    # Target 2 (orange/alert)
    t2_x = center + radius * 0.65 * math.cos(math.radians(135))
    t2_y = center + radius * 0.65 * math.sin(math.radians(135))
    draw.ellipse([t2_x - size*0.028, t2_y - size*0.028, t2_x + size*0.028, t2_y + size*0.028], fill=(255, 90, 95, 230))
    
    # Target 3 (purple/meta)
    t3_x = center + radius * 0.55 * math.cos(math.radians(220))
    t3_y = center + radius * 0.55 * math.sin(math.radians(220))
    draw.ellipse([t3_x - size*0.025, t3_y - size*0.025, t3_x + size*0.025, t3_y + size*0.025], fill=(168, 85, 247, 230))
    
    # Center pulse dot
    draw.ellipse([center - size*0.04, center - size*0.04, center + size*0.04, center + size*0.04], fill=(0, 240, 255, 255))
    draw.ellipse([center - size*0.018, center - size*0.018, center + size*0.018, center + size*0.018], fill=(255, 255, 255, 255))
    
    img.save(filename, "PNG")
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_radar_icon(192, r"C:\Users\EXCELLENT COMPUTER\.gemini\antigravity\scratch\media-buying-radar\web\icons\icon-192.png")
    create_radar_icon(512, r"C:\Users\EXCELLENT COMPUTER\.gemini\antigravity\scratch\media-buying-radar\web\icons\icon-512.png")
    create_radar_icon(64, r"C:\Users\EXCELLENT COMPUTER\.gemini\antigravity\scratch\media-buying-radar\web\icons\favicon.png")
