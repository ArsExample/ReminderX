# TODO: make exe

import sys
from MODULES import eventX, mycalendar
import threading
import sqlite3

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QColorDialog, QMessageBox
from PyQt5.QtCore import QRect, QDate, QTime
from PyQt5.QtGui import QColor

event = None
event_done = False
event_canceled = False

colorToday = QColor(255, 0, 0, 50)
colorEvent = QColor(255, 0, 0, 255)


class FormError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return "Form has been raised"


class WelcomeForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi(r'UI_Files/welcome.ui', self)  # Загружаем дизайн
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
        try:
            self.mode = None
            self.os = self.checkPlatform()
            self.saved = True
            self.fname = None
            self.saveFname = None
            self._back = False

            self.monthes = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
                            "ноября", "декабря"]

            super().__init__()
            uic.loadUi(r'UI_Files/table.ui', self)  # Загружаем дизайн
            self.initUI()
            self.setCalendarColors()
            if args[1] == "create":
                print(1)
                self.saveFname = QFileDialog.getSaveFileName(self, "Сохранить", "", "База данных (*.sqlite)")[0]
                # if self.saveFname[-7:] != ".sqlite" and self.saveFname != "":
                #     self.saveFname = self.saveFname + ".sqlite"
                # else:
                #     raise FormError("empty path")
                if self.saveFname == "":
                    raise FormError("empty path")
                print(3)

                con = sqlite3.connect(self.saveFname)
                cur = con.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS Event (date, time, text)""")
                cur.execute("""DELETE FROM Event""")
                con.commit()

                res = cur.execute("SELECT * FROM Event").fetchall()
                for i in res:
                    print(i)

                self.mode = "create"

                self.calendarW.clicked.connect(self.updateInfo)
                self.btnAdd.clicked.connect(self.createEvent)
                self.tableWidget.setColumnCount(2)
                self.tableWidget.cellClicked.connect(self.chageEvent)
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
                    'База данных (*.sqlite)')[0]

                self.calendarW.clicked.connect(self.updateInfo)
                self.btnAdd.clicked.connect(self.createEvent)
                self.tableWidget.cellClicked.connect(self.chageEvent)
                self.tableWidget.setColumnCount(2)
                self.tableWidget.setRowCount(0)
                self.tableWidget.setHorizontalHeaderLabels(["Время", "Событие"])
                self.cellFirst = True
                self.day = None
                self.month = None
                self.year = None
                #  self.tableWidget.setEnabled(False) !!! а че делать оно серое

                _dates = []

                con = sqlite3.connect(self.fname)
                cur = con.cursor()
                result = cur.execute("""SELECT * FROM Event""").fetchall()
                con.close()

                for i in result:
                    self.calendarW.addEventDate(
                        QDate(int(i[0].split(".")[2]), int(i[0].split(".")[1]), int(i[0].split(".")[0])))


                self.updateInfo()
            else:
                raise FormError("unknown table creating mode")
        except sqlite3.OperationalError as e:
            self._back = True
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Path error")
            msg.setInformativeText('Invalid path')
            msg.setWindowTitle("Path error")
            msg.exec_()
            sys.exit(0)
        except FormError as e:
            if e == "empty path":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("path error")
                msg.setInformativeText("Path can't be empty")
                msg.setWindowTitle("Path error")
                msg.exec_()
                sys.exit(0)
            elif e == "unknown table creating mode":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Mode error")
                msg.setWindowTitle("Unknown error")
                msg.exec_()
                sys.exit(0)
        except Exception as e:
            print(e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Unknown error")
            msg.setWindowTitle("Unknown error")
            msg.exec_()
            sys.exit(0)

    def initUI(self):
        self.calendarW = mycalendar.MyCalendar(self.centralwidget)
        self.calendarW.setGeometry(QRect(0, 0, 1121, 751))
        self.calendarW.setObjectName("calendarW")

    def setCalendarColors(self):
        global colorEvent
        global colorToday

        if colorToday:
            self.calendarW.setColors(current=colorToday)
        if colorEvent:
            self.calendarW.setColors(event=colorEvent)

    def updateInfo(self):
        if self._back:
            print(123)
            self.welcomeForm = WelcomeForm(self)
            self.welcomeForm.show()
            self.close()
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

            con = sqlite3.connect(self.saveFname)
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM Event WHERE date = ?""", (_date,)).fetchall()
            con.close()

            for i in result:
                events.append([i[1], i[2]])

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

            con = sqlite3.connect(self.fname)
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM Event WHERE date = ?""", (_date,)).fetchall()
            con.close()

            for i in result:
                events.append([i[1], i[2]])

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
                        con = sqlite3.connect(self.saveFname)
                        cur = con.cursor()
                        cur.execute("""INSERT INTO Event(date,time,text) VALUES(?,?,?)""",
                                    (event.getDate(), event.getTime(), event.getText()))
                        con.commit()
                        con.close()

                        self.saved = False
                        event_done = False
                    elif self.mode == "open":
                        con = sqlite3.connect(self.fname)
                        cur = con.cursor()
                        cur.execute("""INSERT INTO Event(date,time,text) VALUES(?,?,?)""",
                                    (event.getDate(), event.getTime(), event.getText()))
                        con.commit()
                        con.close()

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
        self.welcomeForm.show()
        self.close()

    def chageEvent(self, r, c):
        def waiting():
            global event_done
            global event_canceled
            global event
            while not event_done:
                pass
            else:
                if event_done and not event_canceled:
                    self.updateInfo()
                    if event.getTime() and event.getText():
                        self.addEvent(event.getTime(), event.getText())

                        # сохранение файла в csv таблицу
                        if self.mode == "create":
                            con = sqlite3.connect(self.saveFname)
                            cur = con.cursor()
                            cur.execute("""UPDATE Event SET date=?, time=?, text=? WHERE date=? AND time=? AND text=?""",
                                        (event.getDate(), event.getTime(), event.getText(),
                                         f"{self.day}.{self.month}.{self.year}", self.tableWidget.item(r, 0).text(),
                                         self.tableWidget.item(r, 1).text()))
                            con.commit()
                            con.close()

                            self.saved = False
                            event_done = False
                            self.updateInfo()
                        elif self.mode == "open":
                            con = sqlite3.connect(self.fname)
                            cur = con.cursor()
                            cur.execute("""UPDATE Event SET date=?, time=?, text=? WHERE date=? AND time=? AND text=?""",
                                        (event.getDate(), event.getTime(), event.getText(),
                                         f"{self.day}.{self.month}.{self.year}", self.tableWidget.item(r, 0).text(),
                                         self.tableWidget.item(r, 1).text()))
                            con.commit()
                            con.close()

                            self.saved = False
                            event_done = False
                            self.updateInfo()
                    else:
                        self.updateInfo()
                elif event_canceled:
                    pass

        self.changeForm = ChangeEventForm(self, [self.day, self.month, self.year],
                                          [self.tableWidget.item(r, 0).text(), self.tableWidget.item(r, 1).text()], [self.mode, self.saveFname, self.fname])
        self.changeForm.show()
        t = threading.Thread(target=waiting)
        t.start()

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
        uic.loadUi(r'UI_Files/createForm.ui', self)  # Загружаем дизайн
        self.btnCreate.clicked.connect(self.create)
        self.btnCancel.clicked.connect(self.cancel)
        self.date = ".".join(list(map(str, args[1])))

    def create(self):
        global event
        global event_done
        time = str(self.timeE.time())[19:-1].split(", ")
        time = self.formatTime(time)
        event = eventX.Event(self.date, str(time[0] + ":" + time[1]), self.tE.toPlainText())
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
        uic.loadUi(r'UI_Files/settings.ui', self)  # Загружаем дизайн
        self.btnCancel.clicked.connect(self.back)
        self.btnSave.clicked.connect(self.save)
        self.btnDateChange.clicked.connect(self.todayColor)
        self.btnColorChange.clicked.connect(self.eventColor)
        self.colorT = None
        self.colorE = None

    def closeEvent(self, event):
        self.welcomeForm = WelcomeForm(self)
        self.welcomeForm.show()
        self.close()

    def back(self):
        self.welcomeForm = WelcomeForm(self)
        self.welcomeForm.show()
        self.close()

    def todayColor(self):
        self.colorT = QColorDialog.getColor()

    def eventColor(self):
        self.colorE = QColorDialog.getColor()

    def save(self):
        global colorEvent
        global colorToday
        if self.colorT:
            colorEvent = self.colorE

        if self.colorE:
            colorEvent = self.colorE

        self.back()


class ChangeEventForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi(r'UI_Files/changeForm.ui', self)  # Загружаем дизайн
        self.btnCreate.clicked.connect(self.create)
        self.btnDelete.clicked.connect(self.delete)
        self.btnCancel.clicked.connect(self.cancel)
        self.date = ".".join(list(map(str, args[1])))
        self.time = args[2][0]
        self.text = args[2][1]
        self.mode = args[3][0]
        self.saveFname = args[3][1]
        self.fname = args[3][2]

        self.loadUI()

    def loadUI(self):
        self.timeE.setTime(QTime(int(self.time.split(":")[0]), int(self.time.split(":")[1])))
        self.tE.setPlainText(self.text)

    def create(self):
        global event
        global event_done
        time = str(self.timeE.time())[19:-1].split(", ")
        time = self.formatTime(time)
        event = eventX.Event(self.date, str(time[0] + ":" + time[1]), self.tE.toPlainText())
        self.close()

        event_done = True

    def cancel(self):
        global event_done
        global event_canceled
        event_done = True
        event_canceled = True
        self.close()

    def delete(self):
        global event_canceled
        global event_done
        if self.mode == "create":
            con = sqlite3.connect(self.saveFname)
            cur = con.cursor()
            cur.execute("""DELETE WHERE time=? AND date=? AND text=?""", (self.time, self.date, self.text))
            con.commit()
            con.close()
        elif self.mode == "open":
            con = sqlite3.connect(self.fname)
            cur = con.cursor()
            cur.execute("""DELETE FROM Event WHERE time=? AND date=? AND text=?""", (self.time, self.date, self.text))
            con.commit()
            con.close()

        event_canceled = True
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WelcomeForm()
    ex.show()
    sys.exit(app.exec_())
