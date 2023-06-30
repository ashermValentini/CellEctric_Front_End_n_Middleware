from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPen


class QRoundProgressBar(QtWidgets.QWidget):

    StyleDonut = 1
    StylePie = 2
    StyleLine = 3

    PositionLeft = 180
    PositionTop = 90
    PositionRight = 0
    PositionBottom = -90

    UF_VALUE = 1
    UF_PERCENT = 2
    UF_MAX = 4

    def __init__(self):
        super().__init__()
        
        self.gradientData = [(0.0, QtGui.QColor('#0796FF')), (1.0, QtGui.QColor('#0796FF'))]
        

        self.min = 0
        self.max = 50  # Update the maximum value to 50ml
        self.value = 0

        self.nullPosition = self.PositionTop
        self.barStyle = self.StyleDonut
        self.outlinePenWidth = 2
        self.dataPenWidth = 2
        self.rebuildBrush = False
        self.format = "%v ml/mn"  # Update the format to display values in ml
        self.decimals = 0  # Update the number of decimals to 0
        self.updateFlags = self.UF_VALUE
        self.gradientData = []
        self.donutThicknessRatio = 0.9

    def setRange(self, min, max):
        self.min = min
        self.max = max

        if self.max < self.min:
            self.max, self.min = self.min, self.max

        if self.value < self.min:
            self.value = self.min
        elif self.value > self.max:
            self.value = self.max

        if not self.gradientData:
            self.rebuildBrush = True
        self.update()

    def setMinimum(self, min):  # Correct typo in method name
        self.setRange(min, self.max)

    def setMaximum(self, max):  # Correct typo in method name
        self.setRange(self.min, max)

    def setValue(self, val):
        if self.value != val:
            if val < self.min:
                self.value = self.min
            elif val > self.max:
                self.value = self.max
            else:
                self.value = val
            self.update()

    def setNullPosition(self, position):
        if position != self.nullPosition:
            self.nullPosition = position
            if not self.gradientData:
                self.rebuildBrush = True
            self.update()

    def setBarStyle(self, style):
        if style != self.barStyle:
            self.barStyle = style
            self.update()

    def setOutlinePenWidth(self, penWidth):
        if penWidth != self.outlinePenWidth:
            self.outlinePenWidth = penWidth
            self.update()

    def setDataPenWidth(self, penWidth):
        if penWidth != self.dataPenWidth:
            self.dataPenWidth = penWidth
            self.update()

    def setDataColors(self, stopPoints):
        if stopPoints != self.gradientData:
            self.gradientData = stopPoints
            self.rebuildBrush = True
            self.update()

    def setFormat(self, format):
        if format != self.format:
            self.format = format
            self.valueFormatChanged()

    def resetFormat(self):
        self.format = ''
        self.valueFormatChanged()

    def setDecimals(self, count):
        if count >= 0 and count != self.decimals:
            self.decimals = count
            self.valueFormatChanged()

    def setDonutThicknessRatio(self, val):
        self.donutThicknessRatio = max(0., min(val, 1.))
        self.update()

    def paintEvent(self, event):
        outerRadius = min(self.width(), self.height())
        baseRect = QtCore.QRectF(1, 1, outerRadius - 2, outerRadius - 2)

        buffer = QtGui.QImage(outerRadius, outerRadius, QtGui.QImage.Format_ARGB32)
        buffer.fill(Qt.black)  # Set background color to black

        p = QtGui.QPainter(buffer)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # data brush
        self.rebuildDataBrushIfNeeded()

        # background
        self.drawBackground(p, buffer.rect())

        # base circle
        self.drawBase(p, baseRect)

        # data circle
        arcStep = 360.0 / (self.max - self.min) * self.value
        self.drawValue(p, baseRect, self.value, arcStep)

        # center circle
        innerRect, innerRadius = self.calculateInnerRect(baseRect, outerRadius)
        self.drawInnerBackground(p, innerRect)

        # text
        self.drawText(p, innerRect, innerRadius, self.value)

        # finally draw the bar
        p.end()

        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, buffer)

    def drawBackground(self, p, baseRect):
        p.fillRect(baseRect, QtGui.QBrush(QtGui.QColor("#222222")))

    def drawBase(self, p, baseRect):
        bs = self.barStyle
        if bs == self.StyleDonut:
            p.setPen(QtGui.QPen(Qt.NoPen))  # Set pen to NoPen
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StylePie:
            p.setPen(QtGui.QPen(Qt.NoPen))  # Set pen to NoPen
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StyleLine:
            p.setPen(QtGui.QPen(QtGui.QColor("white"), self.outlinePenWidth))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(
                baseRect.adjusted(
                    self.outlinePenWidth / 2,
                    self.outlinePenWidth / 2,
                    -self.outlinePenWidth / 2,
                    -self.outlinePenWidth / 2,
                )
            )

    def drawValue(self, p, baseRect, value, arcLength):
        # nothing to draw
        if value == self.min:
            return

        # for Line style
        if self.barStyle == self.StyleLine:
            p.setPen(Qt.NoPen)  # Set pen to NoPen
            p.setBrush(Qt.NoBrush)
            p.drawArc(
                baseRect.adjusted(
                    self.outlinePenWidth / 2,
                    self.outlinePenWidth / 2,
                    -self.outlinePenWidth / 2,
                    -self.outlinePenWidth / 2,
                ),
                int(self.nullPosition * 16),
                int(-arcLength * 16),
            )
            return

        # for Pie and Donut styles
        dataPath = QtGui.QPainterPath()
        dataPath.setFillRule(Qt.WindingFill)

        # pie segment outer
        dataPath.moveTo(baseRect.center())
        dataPath.arcTo(baseRect, self.nullPosition, -arcLength)
        dataPath.lineTo(baseRect.center())

        if value == self.max:
            p.setBrush(QtGui.QBrush(QtGui.QColor("#0796FF")))  # Set brush color to your custom color
        else:
            p.setBrush(QtGui.QBrush(QtGui.QColor("#0796FF")))  # Set brush color to your custom color

        p.setPen(Qt.NoPen)  # Set pen to NoPen (removing the outline)
        p.drawPath(dataPath)


    def calculateInnerRect(self, baseRect, outerRadius):
        # for Line style
        if self.barStyle == self.StyleLine:
            innerRadius = outerRadius - self.outlinePenWidth
        else:  # for Pie and Donut styles
            innerRadius = outerRadius * self.donutThicknessRatio

        delta = (outerRadius - innerRadius) / 2.0
        innerRect = QtCore.QRectF(delta, delta, innerRadius, innerRadius)
        return innerRect, innerRadius

    def drawInnerBackground(self, p, innerRect):
        if self.barStyle == self.StyleDonut:
            p.setBrush(self.palette().base())
            p.setPen(Qt.NoPen)  # Set pen to NoPen

            cmod = p.compositionMode()
            p.setCompositionMode(QtGui.QPainter.CompositionMode_Source)

            p.drawEllipse(innerRect)

            p.setCompositionMode(cmod)

    def drawText(self, p, innerRect, innerRadius, value):
        if not self.format:
            return

        text = self.valueToText(value)

        f = QFont("Archivo")  # Set font family to Archivo
        f.setPixelSize(int(innerRadius * 0.25))  # Adjust font size to make it smaller
        p.setFont(f)

        textRect = innerRect
        p.setPen(QtGui.QPen(QtGui.QColor("white")))  # Set pen color to white
        p.drawText(textRect, Qt.AlignCenter, text)

    def valueToText(self, value):
        textToDraw = self.format

        format_string = "{" + ":.{}f".format(self.decimals) + "}"

        if self.updateFlags & self.UF_VALUE:
            if value == self.max and self.max != 0:
                textToDraw = format_string.format(self.max)  # Display the maximum value instead of "OFF"
            else:
                textToDraw = textToDraw.replace("%v", format_string.format(value))
        return textToDraw

    def valueFormatChanged(self):
        self.updateFlags = self.UF_VALUE

        self.update()

    def rebuildDataBrushIfNeeded(self):
        if self.rebuildBrush:
            self.rebuildBrush = False

            dataBrush = QtGui.QConicalGradient()
            dataBrush.setCenter(0.5, 0.5)
            dataBrush.setCoordinateMode(QtGui.QGradient.StretchToDeviceMode)

            for pos, color in self.gradientData:
                dataBrush.setColorAt(1.0 - pos, color)

            # angle
            dataBrush.setAngle(self.nullPosition)

            p = self.palette()
            p.setBrush(QtGui.QPalette.Highlight, dataBrush)
            self.setPalette(p)
            
    def sizeHint(self):
        return QtCore.QSize(100, 100) # return your preferred size here
    
    def setBarColor(self, color):
        self.gradientData = [(0.0, QtGui.QColor(color)), (1.0, QtGui.QColor(color))]
        self.rebuildBrush = True
        self.update()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the application palette to use a black color scheme
        app.setStyle("Fusion")
        darkPalette = QtGui.QPalette()
        darkPalette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        darkPalette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 0, 0))
        darkPalette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(0, 0, 0))
        darkPalette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.Button, QtGui.QColor(0, 0, 0))
        darkPalette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        darkPalette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        darkPalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        darkPalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        app.setPalette(darkPalette)

        # Create the first instance of QRoundProgressBar with maximum value of 50ml
        self.roundProgressBar1 = QRoundProgressBar()
        self.roundProgressBar1.setRange(0, 50)
        self.roundProgressBar1.setValue(0)
        self.roundProgressBar1.setBarColor('#0796FF')


        # Create the second instance of QRoundProgressBar with maximum value of 10ml
        self.roundProgressBar2 = QRoundProgressBar()
        self.roundProgressBar2.setRange(0, 10)
        self.roundProgressBar2.setValue(0)

        # Create a line edit widget
        self.lineEdit = QtWidgets.QLineEdit()

        # Create a layout for the line edit and progress bars
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.roundProgressBar1)
        self.layout.addWidget(self.roundProgressBar2)

        # Create a vertical layout for the line edit and progress bars
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.addLayout(self.layout)
        self.verticalLayout.addWidget(self.lineEdit)

        # Create a central widget and set the layout
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setLayout(self.verticalLayout)

        # Set the central widget for the main window
        self.setCentralWidget(self.centralWidget)

        # Connect the line edit's returnPressed signal to update the progress bars
        self.lineEdit.returnPressed.connect(self.updateProgressBars)

    def updateProgressBars(self):
        value = self.lineEdit.text()
        if value:
            value = int(value)
            if value <= self.roundProgressBar1.max:
                self.roundProgressBar1.setValue(value)
            if value <= self.roundProgressBar2.max:
                self.roundProgressBar2.setValue(value)
        else:
            self.roundProgressBar1.setValue(0)
            self.roundProgressBar2.setValue(0)

    def closeEvent(self, event):
        # Clean up resources and exit the application properly
        self.roundProgressBar1.deleteLater()
        self.roundProgressBar2.deleteLater()
        self.lineEdit.deleteLater()
        event.accept()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
