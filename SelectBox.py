from qtpy import QtWidgets, QtCore

class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15,0,0,0)
        layout.setSpacing(10)
        for text in 'One Two Three Four Five'.split():
            layout.addWidget(QtWidgets.QPushButton(text, self))
        self.rubberband = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(
            QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtWidgets.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, event.pos()).normalized())
        QtWidgets.QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            selected = []
            rect = self.rubberband.geometry()
            for child in self.findChildren(QtWidgets.QPushButton):
                if rect.intersects(child.geometry()):
                    selected.append(child)
            print('Selection Contains:\n ')
            if selected:
                print('  '.join(
                    'Button: %s\n' % child.text() for child in selected)) 
            else:
                print(' Nothing\n')
        QtWidgets.QWidget.mouseReleaseEvent(self, event)

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())