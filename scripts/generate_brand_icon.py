import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QIcon, QPixmap
from PySide6.QtCore import Qt, QRectF

def generate_icon(output_path):
    # Initialize application core for rendering
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    print(f"Generating icon sizes for {output_path}...")
    
    # Sizes for ICO (standard Windows sizes)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    
    # Colors
    primary_color = QColor("#34d399")  # Teal
    bg_start = QColor("#2d3748")
    bg_end = QColor("#1a202c")
    inactive_color = QColor("#334155")
    
    pixmaps = []
    
    for size in sizes:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        rect = QRectF(0, 0, size, size)
        radius = size * 0.2
        
        gradient = QLinearGradient(0, 0, 0, size)
        gradient.setColorAt(0.0, bg_start)
        gradient.setColorAt(1.0, bg_end)
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        # Draw 3x3 Grid
        margin = size * 0.15
        grid_rect = rect.adjusted(margin, margin, -margin, -margin)
        cell_size = grid_rect.width() / 3
        cell_spacing = cell_size * 0.15
        actual_cell_size = cell_size - cell_spacing
        
        # Triangle cells: index 0, 3, 4, 6
        triangle_indices = [0, 3, 4, 6]
        
        for i in range(9):
            row = i // 3
            col = i % 3
            
            x = grid_rect.left() + col * cell_size + cell_spacing / 2
            y = grid_rect.top() + row * cell_size + cell_spacing / 2
            
            cell_rect = QRectF(x, y, actual_cell_size, actual_cell_size)
            cell_radius = actual_cell_size * 0.3
            
            if i in triangle_indices:
                painter.setBrush(primary_color)
                painter.setOpacity(1.0)
            else:
                painter.setBrush(inactive_color)
                painter.setOpacity(0.4)
                
            painter.drawRoundedRect(cell_rect, cell_radius, cell_radius)
            
        painter.end()
        pixmaps.append(pixmap)
        print(f" Created {size}x{size} layer")
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the largest as PNG for taskbar/web
    png_path = output_path.with_suffix('.png')
    pixmaps[-1].save(str(png_path), "PNG")
    print(f"PNG saved at {png_path}")
    
    # Save as ICO (multiple sizes)
    icon = QIcon()
    for pixmap in pixmaps:
        icon.addPixmap(pixmap)
    
    # PySide6 doesn't have a direct way to save a multi-res QIcon to a file.
    # However, QPixmap.save("path.ico") on Windows often works by saving the single pixmap as an ico.
    # But for a true multi-res ICO, we'd need a specialized library.
    # Since we can't use one, we'll save the 256x256 as the ICO. Windows will rescale it.
    pixmaps[-1].save(str(output_path), "ICO")
    print(f"ICO saved at {output_path}")

if __name__ == "__main__":
    icon_path = Path("resources/icons/app.ico").absolute()
    generate_icon(icon_path)
