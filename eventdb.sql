--
-- Файл сгенерирован с помощью SQLiteStudio v3.3.3 в пн нояб. 14 19:37:12 2022
--
-- Использованная кодировка текста: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: Event
CREATE TABLE Event (date, time, text);
INSERT INTO Event (date, time, text) VALUES ('14.11.22', '20:00', 'go zxc');

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
