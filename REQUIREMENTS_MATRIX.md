# Матрица покрытия задания

Проверка 28.10.2026: наличие и согласованность проектных артефактов, не выполнение production-плана. «Покрыто» означает, что требуемое решение/анализ описаны и проверены по источникам. Неизвестные значения остаются неизвестными. Фактические испытания и согласования будущего внедрения здесь не отмечаются выполненными.

| ID | Требование | Артефакт / свидетельство | Результат |
|---|---|---|---|
| T1-01 | Функциональные требования | [requirements.md](Task1/requirements.md), F-01–08 с источниками | Покрыто |
| T1-02 | Архитектурно значимые NFR | [requirements.md](Task1/requirements.md), N-01–08 и методы проверки | Покрыто; числа не придуманы |
| T1-03 | Ограничения/допущения | [requirements.md](Task1/requirements.md), C/A/H | Покрыто; статус различён |
| T1-04 | Проблемные зоны/приоритеты | [requirements.md](Task1/requirements.md), P0–P2 и [трансформация](Task3/transformation.md) | Покрыто; приоритет предложен |
| T1-05 | Пробелы и владельцы | [requirements.md](Task1/requirements.md), Q-01–12 | Покрыто |
| T1-06 | Карта стейкхолдеров | [stakeholders.md](Task1/stakeholders.md) | Покрыто |
| T1-07 | Сценарий спонсора | [interview-scenarios.md](Task1/interview-scenarios.md), раздел 1 | Цель, гипотезы, вопросы, ценность |
| T1-08 | Сценарий руководителя заказов | [interview-scenarios.md](Task1/interview-scenarios.md), раздел 2 | Цель, гипотезы, вопросы, ценность |
| T1-09 | Сценарий техлида | [interview-scenarios.md](Task1/interview-scenarios.md), раздел 3 | Цель, гипотезы, вопросы, ценность |
| T1-10 | Анализ интервью | [interview-analysis.md](Task1/interview-analysis.md), I-01–18 | Вопрос/гипотеза/исход/противоречие/вывод |
| T1-11 | Сценарии не заменены стенограммами | [interview-scenarios.md](Task1/interview-scenarios.md) и [анализ](Task1/interview-analysis.md) | Новые встречи не выдуманы |
| T2-01 | Architecture Canvas | [architecture-canvas.md](Task2/architecture-canvas.md) | Девять блоков arc42 и связь с кейсом |
| T2-02 | AS-IS контекст | [as-is.drawio](Task2/as-is.drawio), [SVG](Task2/as-is.svg) | Граница, участники, потоки/риски; крупная декомпозиция отмечена |
| T2-03 | Анализ материалов | [as-is-analysis.md](Task2/as-is-analysis.md), разделы 1–4 | P/C и все три интервью разработчиков сопоставлены |
| T2-04 | Фактические зависимости/обходы | [as-is-analysis.md](Task2/as-is-analysis.md), последовательность C и реестр потоков | Staging/batch/manual/fallback; границы знания указаны |
| T3-01 | Точки трансформации | [transformation.md](Task3/transformation.md), паспорта TP-01–03 | Проблема/эффект/ограничения/зависимости/метрики |
| T3-02 | Промежуточная цель | [transformation.md](Task3/transformation.md), карточка/ownership | Первый этап read-only, core остаётся |
| T3-03 | Опасные изменения отложены | [transformation.md](Task3/transformation.md), приоритизация | Цена/create/payment/route/Oracle не выносятся сразу |
| T3-04 | TO-BE контекст | [to-be.drawio](Task3/to-be.drawio), [SVG](Task3/to-be.svg) | Старый/new/later различены, write-path сохранён |
| T3-05 | Шаблоны урока | [transformation.md](Task3/transformation.md), три явно названных шаблона; источник T | Поля сверены на платформе |
| T4-01 | Roadmap | [migration-roadmap.md](Task4/migration-roadmap.md), E0–E6 | Состояния, зависимости, риски, выходные gates |
| T4-02 | Cutover | [cutover-plan.md](Task4/cutover-plan.md), разделы 1–4 | Scope, роли, условия и шаги |
| T4-03 | Данные/наблюдаемость/откат | [cutover-plan.md](Task4/cutover-plan.md), W0/W1/W2, M, rollback | Согласованные позиции, shadow/replay, возврат чтения |
| S-01 | Публичный RetailCore | Проверяется по GitHub перед сдачей, ссылка будет в PR | Условие публикации, не тест production |
| S-02 | Task1–Task4 и обязательные файлы | [validate.py](tools/validate.py) | Проверяется машинно и содержательно |
| S-03 | Ссылка на PR для платформы | После проверки PR отправляется по прямому указанию пользователя | Фактический ответ платформы фиксируется отдельно в журнале курса |
| S-04 | Не менять после отправки | Ветка сдачи фиксируется после принятия платформой | Изменения до комментариев не планируются |

## Содержательная самопроверка

- Нет утверждения, что C доказывает transaction boundary/отсутствие компенсаций во всей системе.
- Создание платежной сессии не приравнено к списанию денег; неизвестный исход не повторяется автоматически.
- CDC не назван готовым business event stream; snapshot не назван полной историей.
- При непройденном capability gate проекция не вводится. Недостающие SLO/lag/RTO не заменены числами.
- Rollback read-only не меняет Oracle и не пересылает команды; поздний перенос внешних writers имеет отдельный gate.
- Авторизация/сохранность новой копии данных и capacity учтены, но внедрение и проверки не выданы за выполненные.
