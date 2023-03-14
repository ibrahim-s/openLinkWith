# Відкрити посилання за допомогою #

Автори: Ibrahim Hamadeh, Cary Rowen, Belala Toufik  
Сумісність з NVDA: 2018.3 і вище   
Завантажити [Версію 2.8][1]  

Цей додаток використовується для отримання посилань із виділеного тексту, буфера обміну чи останнього промовленого тексту  
він відображає їх в діалозі у вигляді списку  
і дає вам можливість відкрити їх за допомогою декількох браузерів, якщо вони є на вашому комп'ютері.

## Використання

*	Спочатку необхідно призначити комбінації клавіш для додатка через діалог жести вводу.  
*	Ви можете зробити це в меню NVDA/Налаштування/Жести вводу/Відкрити посилання за допомогою.  
*	Є три непризначених комбінації.  
	1.	Комбінація для відображення посилань з виділеного тексту.  
	2.	Комбінація для відображення посилання з тексту буфера обміну.  
	3.	Комбінація для відображення посилання з останнього промовленого тексту.  
*	Призначивши комбінацію, ви можете отримувати посилання або з виділеного, або з буфера обміну, або з останнього промовленого тексту.  
*	потім натисніть комбінацію додатка, яку ви призначели  
*	якщо є посилання, вони відображатимуться в списку в діалозі додатка  
*	Виберіть посилання та натисніть enter, якщо ви хочете відкрити його в основному браузері.  
*	в іншому випадку перейдіть до браузера, за допомогою якого ви хочете його відкрити, та натисніть Enter.  
*	Якщо є лише одне посилання, ви можете відкрити його безпосередньо в основному браузері. Цю опцію можна налаштувати в панелі налаштувань. Цю опцію можна налаштувати в панелі налаштувань.
*	Також пам'ятайте, що в панелі налаштувань ви можете закрити діалог після активації посилання.  

## Зміни у версії 2.8 ##
*	Оновлено шаблон додатка.
*	Оновлено останню перевірену версію до 2023.1 для сумісності з останнім api додатків.

## Зміни у версії 2.7 ##

*	Тепер ви можете видобувати посилання з останнього вимовленого тексту.
*	Ви можете скористатися параметрами на панелі налаштувань, щоб вирішити, чи відкривати його безпосередньо основним браузером, коли в тексті є лише одне посилання.
*	Видалено дублікати після видобування посилання

## Changes for 2.6 ##

*	Add Turkish translation for the addon.

## Changes for 2.5 ##

*	Disable the addon in secure mode
*	Update last tested version to 2022.1, to comply with latest addon api.

## Changes for 2.4 ##

*	Now you have two unassigned gestures for the addon.  
*	One to display links under selected text, and the other to display links in clipboard text.   
*	Use latest addon template files  
*	Update manifest.ini for minimum and last version tested.  

## Changes for 2.2 ##
*	Ensures compatibility with python3.  

## Changes for 2.0 ##

*	Now we access the standard browsers from the registry, and not from C drive.
*	Added a configuration settings dialog for the addon in preferences menu  
So that we have the obtion to close the dialog after activating a link.
*	Added Edge browser to browsers available if in windows10.
*	Added settings panel to  fit  with NVDA2018.2 or later.

## Changes for 1.0 ##

*	Initial version.

[1]: https://github.com/ibrahim-s/openLinkWith/releases/download/v2.8/openLinkWith-2.8.nvda-addon
