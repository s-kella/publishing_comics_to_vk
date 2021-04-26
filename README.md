# publishing comics to vk


### Как установить

Создайте .env файл с содержимым
```
ACCESS_TOKEN_VK=''
GROUP_ID=''
```
Создайте группу Вконтакте и вставьте её ID во вторую строчку .env файла.
Создайте приложение Вконтакте на [странице для разработчиков](https://vk.com/apps?act=manage). Укажите тип ```standalone```
Cкопируйте цифры в адресной строке после id=
Вставьте их вместо "CLIENT_ID"
```
https://oauth.vk.com/authorize?client_id=CLIENT_ID&scope=photos,groups,offline,wall&response_type=token
```
Вставьте ссылку в адресную строку и нажмите "Разрешить"
Скопируйте из адресной строки токен (выглядит как строка наподобие 533bacf01e1165b57531ad114461ae8736d6506a3) и вставьте его в первую строку  .env файла.

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Пример запуска
```
python main.py
```

### Пример результата
![image](https://user-images.githubusercontent.com/52741545/116143089-5e036580-a6e3-11eb-904e-629603a6ae07.png)


### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
