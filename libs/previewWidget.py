try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

# from libs.shape import Shape
# from libs.utils import distance


class PreviewWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(PreviewWidget, self).__init__(*args, **kwargs)

        self.pixmap = QPixmap(0, 0)
        self.position = QPoint(0, 0)
        self.scale = 1
        self.drawing = False
        self.editing = True
        self.drawingColor = QColor(0, 0, 255)
        self.shapes = []

        self.shape_start = None
        self.zoom_factor = 4

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.repaint()

    def set_shapes(self, shapes):
        self.shapes = shapes
        self.repaint()

    def set_position(self, position):
        self.position = position
        self.repaint()

    def set_scale(self, scale):
        self.scale = scale
        self.repaint()

    def set_editing(self, editing):
        self.editing = editing
        if self.editing:
            self.drawing = False
            self.shape_start = None
        self.repaint()

    def set_drawing_color(self, drawingColor):
        self.drawingColor = drawingColor

    def toggle_drawing(self, drawing):
        self.drawing = drawing
        self.shape_start = self.position
        self.repaint()

    def paintEvent(self, event):
        pp = QPainter()
        pp.begin(self)

        scale = self.scale * self.zoom_factor
        w = self.width()
        h = self.height()
        cx = w/2
        cy = h/2

        # stop the preview from moving when drawing a shape, it's easier to aim
        pos = self.shape_start if self.drawing else self.position

        def translate(point):
            x = (point.x() - pos.x()) * scale + cx
            y = (point.y() - pos.y()) * scale + cy
            return QPoint(x, y)

        sw = w / scale
        sh = h / scale
        x = pos.x() - sw / 2
        y = pos.y() - sh / 2
        pp.drawPixmap(0, 0, w, h,
                      self.pixmap,
                      int(x), int(y), int(sw), int(sh))

        # existing shapes
        for shape in self.shapes:
            if not shape.points:
                continue

            color = shape.select_line_color if shape.selected else shape.line_color
            style = QPen(color)
            style.setWidth(1)
            pp.setPen(style)

            path = None
            for p in shape.points:
                s = translate(p)
                if not path:
                    path = QPainterPath()
                    path.moveTo(s)
                else:
                    path.lineTo(s)
            if shape.is_closed():
                path.lineTo(translate(shape.points[0]))

            pp.drawPath(path)
            pp.fillPath(path, shape.fill_color)

        # the currently drawing rect
        if self.drawing and self.shape_start:
            pp.setPen(self.drawingColor)
            pp.setBrush(Qt.BDiagPattern)

            tl = translate(self.shape_start)
            br = translate(self.position)
            pp.drawRect(QRect(tl, br))

            pp.setPen(QColor(0, 255, 0, 255))
            pp.setBrush(QColor(0, 255, 0, 255))
            pp.drawEllipse(tl, 5, 5)

        # cursor/crosshair
        style = QPen(QColor(200, 200, 200, 255))
        pp.setCompositionMode(pp.CompositionMode_Difference)
        if self.drawing or self.editing:
            # i.e. small crosshair/fake cursor
            style.setWidth(3)
            pp.setPen(style)
            sizeh = 10
            s = translate(self.position)
            pp.drawLine(s.x(), s.y()-sizeh, s.x(), s.y()+sizeh)
            pp.drawLine(s.x()-sizeh, s.y(), s.x()+sizeh, s.y())
        else:
            # i.e. full picture crosshair
            style.setWidth(1)
            pp.setPen(style)
            pp.drawLine(cx, 0, cx, h)
            pp.drawLine(0, cy, w, cy)

        pp.end()
