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