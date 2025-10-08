# startup script for stage 5

# переходим в папку с файлами
cd /home/user/documents

# смотрим исходные права
ls

# меняем права на file1.txt
chmod 777 file1.txt

# проверяем, что права изменились
ls file1.txt

# пытаемся поменять права на несуществующем файле
chmod 777 non_existent_file.txt

# проверяем права на папке
ls /home/user

# меняем права на папку
chmod 700 /home/user

# проверяем, что права изменились
ls /home

# тест на неверный режим
chmod abc file1.txt
