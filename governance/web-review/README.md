# Web-review заметок

Канонический процесс: [`00-workflow.md`](<./00-workflow.md>).

Для существующей заметки ChatGPT Web последовательно применяет:

1. [`01-file-structure.md`](<./01-file-structure.md>);
2. [`02-block-structure.md`](<./02-block-structure.md>);
3. [`03-content-distribution.md`](<./03-content-distribution.md>);
4. [`04-content-quality.md`](<./04-content-quality.md>);
5. при подтверждённых проблемах — [`05-change-design.md`](<./05-change-design.md>).

Создание новой заметки начинается с [`new-note-workflow.md`](<./new-note-workflow.md>), а затем проходит полный процесс `00-workflow.md`.

Каждая новая, мигрируемая или явно взятая в полное ревью заметка требует отдельного fresh Web review exact фактического кандидата, даже если primary review не изменил текст. Pure mechanical task может быть освобождена только когда она не является полным ревью и protected content доказанно неизменно.

Эти файлы являются методологией ChatGPT Web. Codex читает их только как структурный справочник, когда конкретная Web-инструкция прямо разрешает `BOUNDED_STRUCTURE` или другой ограниченный режим. Архивные правила не участвуют в текущем процессе.
