# TODO: double click on cell in table to edit event | 0%
# TODO: double click on cell in calendar to edit event | 10%  <-- connected, tomorrow i'll make def (changeEvent())
# TODO: test different file names (ex: save (create) file 'name../"".,.csv' | 0%
# TODO: make notifications | ... xd
# TODO: settings | 30%
# TODO: redo excel saving -> SQL DB saving (and reading) | 0%

import sys
import threading
import csv
import plyer

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QCalendarWidget
from PyQt5.QtCore import QRect, QDate
from PyQt5.QtGui import QColor

event = None
event_done = False


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
            self.currentColor = current
        if event:
            self.eventColor = event


class FormError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"FormError: {self.message}"
        else:
            return "Form has been raised"


class Event():
    def __init__(self, date, time, text):
        self.date = date
        self.time = time
        self.text = text

    def __str__(self):
        return f"{self.date},{self.time};{self.text}"

    def getDate(self):
        return self.date

    def getTime(self):
        return self.time

    def getText(self):
        return self.text

    def getFullDate(self):
        return f"{self.date},{self.time}"

    def setDate(self, date):
        self.date = date

    def setTime(self, time):
        self.time = time

    def setText(self, text):
        self.text = text


class WelcomeForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('welcome.ui', self)  # Загружаем дизайн
        self.btnExit.clicked.connect(self.exit)
        self.btnCreate.clicked.connect(self.create)
        self.btnOpen.clicked.connect(self.openNew)
        self.btnSettings.clicked.connect(self.settings)

    def exit(self):
        self.close()

    def openNew(self):
        self.calendarForm = CalendarForm(self, "open")
        self.calendarForm.show()
        self.close()

    def create(self):
        self.calendarForm = CalendarForm(self, "create")
        self.calendarForm.show()
        self.close()

    def settings(self):
        self.settingsForm = SettingsForm(self)
        self.settingsForm.show()
        self.close()


class CalendarForm(QMainWindow):
    def __init__(self, *args):
        self.mode = None
        self.os = self.checkPlatform()
        self.saved = True
        self.saveFname = None

        self.monthes = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
                        "ноября", "декабря"]

        super().__init__()
        uic.loadUi('table.ui', self)  # Загружаем дизайн
        self.initUI()
        if args[1] == "create":
            self.saveFname = QFileDialog.getSaveFileName(self, "Сохранить", "", "Таблица (*.csv)")[0]
            if self.saveFname[-4:] != ".csv" and self.saveFname != "":
                self.saveFname = self.saveFname + ".csv"
            else:
                raise FormError("empty path")
            f = open(self.saveFname, "w")
            f.close()

            self.mode = "create"

            self.calendarW.clicked.connect(self.updateInfo)
            self.calendarW.activated.connect(self.chageEvent)
            self.btnAdd.clicked.connect(self.createEvent)
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setRowCount(0)
            self.tableWidget.setHorizontalHeaderLabels(["Время", "Событие"])
            self.cellFirst = True
            self.day = None
            self.month = None
            self.year = None
            #  self.tableWidget.setEnabled(False) !!! а че делать оно серое

            self.updateInfo()
        elif args[1] == "open":
            self.mode = "open"

            self.fname = QFileDialog.getOpenFileName(
                self, 'Выбрать файл', '',
                'Таблица (*.csv)')[0]

            self.calendarW.clicked.connect(self.updateInfo)
            self.btnAdd.clicked.connect(self.createEvent)
            self.calendarW.activated.connect(self.chageEvent)
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setRowCount(0)
            self.tableWidget.setHorizontalHeaderLabels(["Время", "Событие"])
            self.cellFirst = True
            self.day = None
            self.month = None
            self.year = None
            #  self.tableWidget.setEnabled(False) !!! а че делать оно серое

            _dates = []

            with open(self.fname, encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for index, row in enumerate(reader):
                    if row[0].split(",")[0] not in _dates:
                        _dates.append(row[0].split(",")[0])
                        self.calendarW.addEventDate(
                            QDate(int((row[0].split(",")[0]).split(".")[2]), int((row[0].split(",")[0]).split(".")[1]),
                                  int((row[0].split(",")[0]).split(".")[0])))

            self.updateInfo()
        else:
            raise FormError("unknown table creating mode")

    def initUI(self):
        self.calendarW = MyCalendar(self.centralwidget)
        self.calendarW.setGeometry(QRect(0, 0, 1121, 751))
        self.calendarW.setObjectName("calendarW")

    def updateInfo(self):
        def get_key(d, value):
            for k, v in d.items():
                if v == value:
                    return k

        if self.mode == "create":
            while self.tableWidget.rowCount() > 0:
                self.tableWidget.removeRow(0)
            self.cellFirst = True
            date = str(self.calendarW.selectedDate())[19:-1].split(", ")
            self.day = int(date[2])
            self.month = int(date[1])
            self.year = int(date[0])
            self.dateL.setText(f"{self.day} {self.monthToStr(self.month)} {self.year}")
            _date = f"{self.day}.{self.month}.{self.year}"

            events = []

            with open(self.saveFname, encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for index, row in enumerate(reader):
                    if row[0].split(",")[0] == _date:
                        events.append([row[0].split(",")[1], row[1]])

            events = list(map(lambda x: [self.hoursToMinutes(x[0]), x[1]], events))
            if events:
                qdate = QDate(self.year, self.month, self.day)
                self.calendarW.addEventDate(qdate)
            events_d = {}
            mins = []
            for i in events:
                events_d[i[0]] = i[1]
                mins.append(i[0])
            mins = sorted(mins)
            events = []
            for i in mins:
                events.append([(self.minutesToHours(get_key(events_d, events_d[i]))), events_d[i]])
            for i in events:
                self.addEvent(i[0], i[1])

        elif self.mode == "open":
            while self.tableWidget.rowCount() > 0:
                self.tableWidget.removeRow(0)
            self.cellFirst = True
            date = str(self.calendarW.selectedDate())[19:-1].split(", ")
            self.day = int(date[2])
            self.month = int(date[1])
            self.year = int(date[0])
            self.dateL.setText(f"{self.day} {self.monthToStr(self.month)} {self.year}")
            _date = f"{self.day}.{self.month}.{self.year}"
            events = []

            with open(self.fname, encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for index, row in enumerate(reader):
                    if row[0].split(",")[0] == _date:
                        events.append([row[0].split(",")[1], row[1]])

            events = list(map(lambda x: [self.hoursToMinutes(x[0]), x[1]], events))
            if events:
                qdate = QDate(self.year, self.month, self.day)
                self.calendarW.addEventDate(qdate)
            events_d = {}
            mins = []
            for i in events:
                events_d[i[0]] = i[1]
                mins.append(i[0])
            mins = sorted(mins)
            events = []
            for i in mins:
                events.append([(self.minutesToHours(get_key(events_d, events_d[i]))), events_d[i]])
            for i in events:
                self.addEvent(i[0], i[1])

    def addEvent(self, time, event):
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        if self.cellFirst:
            self.tableWidget.setItem(0, 0, QTableWidgetItem(time))
            self.tableWidget.setItem(0, 1, QTableWidgetItem(event))
            self.tableWidget.setCurrentCell(self.tableWidget.currentRow() + 1, 0)
            self.cellFirst = False
        else:
            self.tableWidget.setItem(self.tableWidget.currentRow() + 1, self.tableWidget.currentColumn(),
                                     QTableWidgetItem(time))
            self.tableWidget.setItem(self.tableWidget.currentRow() + 1, self.tableWidget.currentColumn() + 1,
                                     QTableWidgetItem(event))
            self.tableWidget.setCurrentCell(self.tableWidget.currentRow() + 1, 0)

    def createEvent(self):
        def waiting():
            global event_done
            global event
            while not event_done:
                pass
            else:
                if event.getTime() and event.getText():
                    self.addEvent(event.getTime(), event.getText())

                    # сохранение файла в csv таблицу
                    if self.mode == "create":
                        with open(self.saveFname, "a", newline="", encoding="utf-8") as csvfile:
                            writer = csv.writer(
                                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL
                            )
                            writer.writerow([event.getFullDate(), event.getText()])

                        self.saved = False
                        event_done = False
                    elif self.mode == "open":
                        with open(self.fname, "a", newline="", encoding="utf-8") as csvfile:
                            writer = csv.writer(
                                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL
                            )
                            writer.writerow([event.getFullDate(), event.getText()])

                        self.saved = False
                        event_done = False
                else:
                    pass
        self.createForm = CreateEventForm(self, [self.day, self.month, self.year])
        self.createForm.show()
        t = threading.Thread(target=waiting)
        t.start()

    def back(self):
        self.welcomeForm = WelcomeForm(self)
        self.selcomeForm.show()
        self.close()

    def notify(self, msg):
        if self.os == "windows":
            ICON_PATH = "calendar_icon.ico"

            plyer.notification.notify(message=msg, app_name="Reminder", title="Событие!")
        else:
            pass

    def chageEvent(self):
        pass

    def monthToStr(self, date):
        return self.monthes[date - 1]

    def hoursToMinutes(self, time):
        h, m = int(time.split(":")[0]), int(time.split(":")[1])
        return (h * 60) + m

    def minutesToHours(self, minutes):
        h = minutes // 60
        m = minutes - (h * 60)
        if h < 10:
            h = f"0{str(h)}"
        if m < 10:
            m = f"0{str(m)}"
        return f"{h}:{m}"

    def formatTime(self, t):
        if len(t[0]) == 1:
            x = "0" + t[0]
        else:
            x = t[0]
        if len(t[1]) == 1:
            y = "0" + t[1]
        else:
            y = t[1]

        return f"{x}:{y}"

    def checkPlatform(self):
        if sys.platform == "linux" or sys.platform == "linux2":
            return "linux"
        elif sys.platform == "darwin":
            return "mac"
        elif sys.platform == "win32":
            return "windows"


class CreateEventForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('createForm.ui', self)  # Загружаем дизайн
        self.btnCreate.clicked.connect(self.create)
        self.btnCancel.clicked.connect(self.cancel)
        self.date = ".".join(list(map(str, args[1])))

    def create(self):
        global event
        global event_done
        time = str(self.timeE.time())[19:-1].split(", ")
        time = self.formatTime(time)
        event = Event(self.date, str(time[0] + ":" + time[1]), self.tE.toPlainText())
        self.close()

        event_done = True

    def cancel(self):
        global event_done
        event_done = True
        self.close()

    def formatTime(self, t):
        if len(t[0]) == 1:
            x = "0" + t[0]
        else:
            x = t[0]
        if len(t[1]) == 1:
            y = "0" + t[1]
        else:
            y = t[1]

        return [x, y]


class SettingsForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('settings.ui', self)  # Загружаем дизайн

class ChangeEventForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('changeForm.ui', self)  # Загружаем дизайн
        self.btnCreate.clicked.connect(self.create)
        self.btnDelete.clicked.connect(self.delete)
        self.btnCancel.clicked.connect(self.cancel)
        self.date = ".".join(list(map(str, args[1])))

    def create(self):
        global event
        global event_done
        time = str(self.timeE.time())[19:-1].split(", ")
        time = self.formatTime(time)
        event = Event(self.date, str(time[0] + ":" + time[1]), self.tE.toPlainText())
        self.close()

        event_done = True

    def cancel(self):
        global event_done
        event_done = True
        self.close()

    def delete(self):
        pass

    def formatTime(self, t):
        if len(t[0]) == 1:
            x = "0" + t[0]
        else:
            x = t[0]
        if len(t[1]) == 1:
            y = "0" + t[1]
        else:
            y = t[1]

        return [x, y]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WelcomeForm()
    # ex = CalendarForm(None, "create")
    ex.show()
    sys.exit(app.exec_())
