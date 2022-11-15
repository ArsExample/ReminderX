from PyQt5.QtWidgets import QCalendarWidget
from PyQt5.QtGui import QColor

class MyCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        QCalendarWidget.__init__(self, parent)
        self.dates = []
        self.currentColor = QColor(255, 0, 0, 50)
        self.eventColor = QColor(255, 0, 0, 255)

    def paintCell(self, painter, rect, date):
        QCalendarWidget.paintCell(self, painter, rect, date)
        if date == date.currentDate():
            painter.setBrush(self.currentColor)
            painter.setPen(QColor(0, 0, 0, 0))
            painter.drawRect(rect)
        if date in self.dates:
            painter.setBrush(self.eventColor)
            painter.setPen(QColor(0, 0, 0, 0))
            painter.drawRect(rect.x() + 20, rect.y() + 47, 5, 5)

    def addEventDate(self, date):
        if date not in self.dates:
            self.dates.append(date)

    def getEventDates(self):
        return self.dates

    def setColors(self, current=None, event=None):
        if current:
            current.setAlpha(50)
            self.currentColor = current
        if event:
            self.eventColor = event

    def undoColors(self):
        self.currentColor = QColor(255, 0, 0, 50)
        self.eventColor = QColor(255, 0, 0, 255)