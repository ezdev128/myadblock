## My AdBlock - Adblock-фильтр против исключений проплаченной рекламы

## My AdBlock - Adblock-filter against paid ads rules exceptions
[English version](https://github.com/ezdev128/myadblock/blob/master/README_EN.md)

###Цель проекта

* Централизованное хранилище
  * своих и корпоративных правил
  * подписок Adblock и Adblock plus
* Отключение или удаление
  * произвольных исключений, полученных в подписках
  * "проплаченных" исключений
  * всех исключений
* Добавление своих правил (фильтров или исключений), согласно синтаксису Adblock
* Кэширование подписок


###Как это работает?
Программа стартует из крона (предположительно, 1 раз в день), читает конфигурационный файл и загружает пользовательские подписки либо использует кэшированную версию, если не удалось загрузить список.
Затем производятся действия, логика которых описана в конфигурационном файле и после окончания работы программы генерируется пользовательский файл подписки, который обновлят Adblock, установленный в браузер.


###Системные требования
* Linux (под другими системами пока не тестировалось)
* [Python (>=2.6)](https://www.python.org/)
* [Python-lxml](https://pypi.python.org/pypi/lxml)
* Любой веб-сервер


###Установка и настройка
1. Устанавливаем Веб-сервер и все необходимые библиотеки
2. Инсталлируем проект, открываем на редактирование файл etc/myadblock.xml и переходим к пункту 3.
3. Добавление подписок
  * Заходим в параметры Adblock -> Список фильтров и выбираем фильтр, который нам нужен ![01](http://s010.radikal.ru/i313/1507/d6/2670b68ae045.jpg)
  * Нажимаем правой кнопкой мыши по фильтру -> Исследовать документ -> находим имя и ссылку на подписку: ![02](http://s04.radikal.ru/i177/1507/18/3468a72ad3d7.jpg)
  * Добавляем подписку в конфигурационный файл (нода subscriptions):
  ```xml
  		<subscription>
			<enabled>True</enabled>
			<mime-type></mime-type>
			<name>EasyList</name>
			<url>https://easylist-downloads.adblockplus.org/easylist.txt</url>
		</subscription>
  ```
  * При желании добавляем другие подписки
4. Кэширование подписок
  * Включаем кэширование и устанавливаем путь к директории, в которую будет разрешено писать файлы (нода cache):
  ```xml
	<app>
	    ...
  		<cache>
  			<enabled>True</enabled>
  			<dir>/var/cache/myadblock</dir>
  		</cache>
  		...
	</app>

  ```
 * Для отключения кэширования необходимо установить enabled в False

5. Устанавливаем путь к выходному файлу, который будет видеть Adblock:
  * Директория, в которой будет находиться выходной файл, должна быть видима по http(s). Например, если мы используем Apache и wwwroot у нас указан в /var/www/html, то мы можем создать поддиректорию myadblock указать такой путь: 
   ```xml
  ...
	<app>
	  ...
		<output-file>/var/www/html/myadblock/myadblock.txt</output-file>
		...
	</app>
	...
   ```
  Соответственно, ссылка для собственной подписки будет такая: http://ip[или имя]_сервера/myadblock/myadblock.txt

6. Добавляем эту ссылку в Adblock в поле ввода "Пользовательские списки фильтров".
7. Добавляем (по желанию) свои правила (нода add-rules), например, так:
   ```xml
	...
	<rule>
	    <name>facebook</name>
	    <enabled>True</enabled>
	    <data>
	        <![CDATA[
			||connect.facebook.net$third-party
			||facebook.com/plugins$third-party
			||pixel.facebook.com
			||api.facebook.com$domain=~facebook.com
		]]>
	    </data>
	</rule>
	...
   ```
8. Добавляем (по желанию) правила удаления исключений:
  * Удалить все исключения:
  ```xml
  ...
  <remove-excludes>
      <remove-all>True</remove-all>
  </remove-excludes>
  ...
  ```
  * Добавить список проплаченных исключений для удаления, например, с типом starts-with (начинаются с...) :
  ```xml
  ...
  <remove-excludes>
	...
	<starts-with>
		<enabled>True</enabled>
		<data>
			<![CDATA[
				@@||vk.com
				
				@@||facebook.com/plugins/like
				@@||facebook.com/plugins/likebox
				@@||facebook.com/plugins/facepile
		</data>
	</starts-with>
	...
  </remove-excludes>
  ...
  ```
  * Удалить ВСЕ исключения, в которых встречается слова "adzerk" и "doubleclick.net":
  ```xml
  ...
  <remove-excludes>
	...
  	<find-any>
		<enabled>True</enabled>
		<data>
			<![CDATA[
				adzerk
				doubleclick.net
			]]>
		</data>
	</find-any>
  ...
  </remove-excludes>
  ```
Примеры конфигурационного файла находятся в директории examples.
