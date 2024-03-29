# TAXIBOT

TaxiBot - небольшой бот в Telegram, который позволяет узнать и сравнить стоимости поездок на такси по определенному маршруту в разных такси-сервисах. Вместо того, чтобы копаться в каждом приложении по очереди, чтобы найти самое выгодное предложение - отметьте начало и конец маршрута, и бот выведет всю информацию по одному нажатию!

## Достоинства
- Доступность   - никаких регистраций, просто запустить бота
- Эффективность - вместо долгих поисков - пара нажатий в боте
- Минимализм    - нет лишних функций или кнопок, интуитивно понятный интерфейс, использование для одной понятной цели

## Функции
- Сравнение цен такси на определенном маршруте
- Переход в приложение такси с уже построенным маршрутом 

## Ресурсы
- API такси-сервисов (Яндекс, Uber, Ситимобил, vk, Bolt и т.д.)
- Telegram Bots 
- ЯП: Python
- optional: 2GIS API

## Детали реализации
Схема работы: пользователь вводит две геопозиции -> бот формирует и отправляет запросы, обрабатывает ответы, формирует кликабельные ссылки, форматирует и отправляет сообщение по типу:
<details><summary>Success response</summary>

> Кронверский пр-кт 49 - ст. м. Беговая:  
>   
> [Яндекс.Такси](https://youtu.be/8aPpF15_gTA) - 200 р.  
> [Uber](https://youtu.be/dQw4w9WgXcQ)        - 180 р.  
> [Ситимобил](https://youtu.be/PGNiXGX2nLU)    - 185 р.  
> [vk](https://youtu.be/YQyue_X4Pk4)           - 666 р.  
> [Bolt](https://youtu.be/CIepe6KMSYs)         - 10 р.  
> 
> Нажмите на название такси, чтобы открыть приложение сервиса!


</details>

Переход в такси с уже построенным маршрутом - небольшие кликабельные ссылки, по нажатию на которые на устройстве открывается приложение %taxi-name% с уже выставленными стартом и финишем, и пользователю остается только нажать на кнопку заказа. Подобные ссылки использует, например, Uber в своих виджетах.

Установку геопозиции возможно реализовать двумя разными путями: 
1) Через встроенную геопозицию Telegram; 
2) Через подключение сторонних API карт: пользователь вводит название улицы в чат с ботом, бот находит это местоположение (с поправкой на город, откуда идёт запрос) в картах и берет координаты. 

Для доступа ко многим API такси-сервисов необходимо сделать запрос в компанию, по которому будут предоставлены данные для пользования API. Или не будут. Некоторые компании хранят свои methods в тайне.


# Design Document
## Функциональные детали
- Бот создан для поиска наиболее выгодного приложения такси
- Минимальное количество функций, доступных пользователю, для облегчения работы
- Реализован API Яндекс.Такси, т.к. остальные сервисы либо не предоставили свой интерфейс ввиду отсутствия ИП/ООО, либо не имеют такого вовсе.

## Структура проекта
### Общая логика
- Пользователь последовательно отправляет боту статичные геопозоиции. 
- Бот запоминает мировые координаты позиций, после чего формирует GET запрос и отправляет его на сервер такси. 
- Ответ от сервера приходит в формате JSON, из которого по ключевым данным получается цена поездки
- По ранее полученным мировым координатам формируется гиперссылка с быстрым доступом к назначенному маршруту в приложении.

### Логика хранения данных
В базе данных Taxigram существует одна таблица, хранящая в себе отправленные пользователями геопозиции для работы с ними:
| Название | Функционал |
| -------------- | -------------- |
| chat_id | Уникальный ID чата каждого пользователя бота |
| latitude_1 | Географическая ширина точки старта маршрута |
| longitude_1 | Географическая долгота точки старта маршрута |
| latitude_2 | Географическая ширина точки финиша маршрута|
| longitude_2 | Географическая долгота точки финиша маршрута |
| pointer | Указатель на то, какую точку в данный момент устанавливает пользователь - старт или финиш |

### Функции
| Название | Функционал |
| -------------- | -------------- |
| send_welcome | Обработка команды /start - приветствие |
| send_help | Обработка команды /help - помощь |
| check | Дебаггинг в консоли сервера (deprecated) |
| location | Обработка отправленной пользователем геопозиции, установка точки начала либо конца поездки (в зависимости от pointer) |
| buttons | Функционал кнопок в меню |
| switchto1 | Меняет величину pointer в БД для конкретного пользователя для последующей установки точки начала поездки |
| switchto2 | Аналогично switchto1, но для установки точки конца поездки |
| check_if_entry_exists | Проверяет, существует ли в БД строка с данными, соответствующая ID чата данного пользователя, и создает пустую строку при ее отсутствии |
| getcost | Формирование строки GET-запроса и обработка JSON, возвращает стоимость поездки |
| poserror | Обработка ситуаций с запросом стоимости при отсутствии геоданных |
| createlink | Создание гиперссылки для приложения такси |
| formatresult | Форматирование текста стоимости всех такси |
| keyborad | Keyboard markup |

### Интерфейс
Реализован с помощью кнопочного меню Telegram. Функионал:
- Выбор типа точки - задать начальную или конечную точку маршрута.
- Получить данные о стоимости.

![Interface picture](./interface2.png)

## План выполненния
- Основная работа с Telegram - создание обработки геопозиций, создание интерфейса, системы хранения данных
- Работа с API Яндекса - GET-запросы, работа с JSON
- Финальные штрихи - настройка вывода, ответов, внешний вид и т.д.
