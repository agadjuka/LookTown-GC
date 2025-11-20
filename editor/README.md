# Эдитор промптов и инструментов

## Что такое эдитор?

Эдитор — это веб-интерфейс для редактирования промптов агентов и управления инструментами без необходимости редактировать код напрямую. Он предоставляет удобный графический интерфейс для:

- Редактирования системных промптов агентов
- Редактирования промптов роутера
- Редактирования промптов отдельных стадий (агентов)
- Управления инструментами для каждой стадии
- Просмотра и тестирования инструментов

## Для чего он нужен?

Эдитор решает следующие задачи:

1. **Упрощение работы с промптами** — не нужно искать и редактировать промпты в коде, все доступно через веб-интерфейс
2. **Быстрое тестирование** — можно быстро изменять промпты и сразу видеть результат
3. **Управление инструментами** — легко добавлять и удалять инструменты для каждой стадии агента
4. **Централизованное управление** — все промпты и инструменты в одном месте

## Как он работает?

### Архитектура эдитора

Эдитор состоит из нескольких модулей:

#### 1. **Flask приложение** (`app.py`)
- Веб-сервер на Flask
- API endpoints для работы с промптами и инструментами
- Отдает HTML интерфейс и обрабатывает запросы

#### 2. **Парсер промптов** (`parser.py`)
- Читает промпты из файлов проекта
- Извлекает системные промпты из `app/config/agent_config.py`
- Извлекает промпты стадий из файлов в `app/stages/`
- Извлекает промпт роутера из `app/routing/message_router.py`

#### 3. **Обновлятор промптов** (`updater.py`)
- Записывает изменения промптов обратно в файлы
- Обновляет промпты стадий в соответствующих файлах
- Может создавать и удалять стадии
- Обновляет граф агентов при добавлении/удалении стадий

#### 4. **Помощник инструментов** (`tools_helper.py`)
- Получает все доступные инструменты из реестра
- Получает информацию об инструментах (параметры, описание)
- Выполняет инструменты для тестирования

#### 5. **Помощник конфигурации инструментов** (`tools_config_helper.py`)
- Читает конфигурацию инструментов из `app/tools/config.py`
- Обновляет привязку инструментов к стадиям
- Парсит файл конфигурации для получения списка инструментов каждой стадии

### Процесс работы

1. **Запуск эдитора**: Запускается через `run_editor.py`, который стартует Flask сервер на `localhost:5000`

2. **Загрузка данных**:
   - Парсер читает все промпты из файлов
   - Загружаются все инструменты из реестра
   - Загружается конфигурация инструментов для стадий

3. **Редактирование**:
   - Пользователь редактирует промпты через веб-интерфейс
   - Выбирает инструменты для стадий через чекбоксы
   - Сохраняет изменения

4. **Сохранение**:
   - Обновлятор записывает промпты в файлы
   - Конфигурация инструментов обновляется в `app/tools/config.py`
   - Изменения применяются сразу (без перезапуска сервера)

## Инструкция по подключению

### Подключение к агентам (стадиям)

Эдитор автоматически подключается к агентам через следующие механизмы:

#### 1. Импорты в `editor/parser.py`

```python
# Парсер использует следующие пути:
self.config_file = self.project_root / "app" / "config" / "agent_config.py"
self.router_file = self.project_root / "app" / "routing" / "message_router.py"
self.stages_dir = self.project_root / "app" / "stages"
```

#### 2. Импорты в `editor/updater.py`

```python
# Обновлятор использует те же пути для записи:
self.config_file = self.project_root / "app" / "config" / "agent_config.py"
self.router_file = self.project_root / "app" / "routing" / "message_router.py"
self.stages_dir = self.project_root / "app" / "stages"
self.graph_file = self.project_root / "app" / "graph" / "graph_builder.py"
```

#### 3. Структура стадий

Каждая стадия должна быть в файле `app/stages/<stage_key>_stage.py` и содержать:

```python
# Промпт стадии (извлекается парсером)
STAGE_INSTRUCTION = SYSTEM_INSTRUCTION + """
...промпт стадии...
"""

# Класс стадии
class StageName(BaseStage):
    def create_llm(self) -> ChatVertexAI:
        return ChatVertexAI(
            model="gemini-2.5-flash",
            system_instruction=STAGE_INSTRUCTION
        )

# Функция-обертка для графа
def stage_key_stage(state: AgentState) -> AgentState:
    return stage_instance.execute(state)
```

#### 4. Регистрация стадий в роутере

Стадии должны быть зарегистрированы в `app/routing/message_router.py`:

```python
valid_routes = [
    "greeting",
    "information_gathering",
    "booking",
    # ... другие стадии
]
```

#### 5. Добавление стадии в граф

При создании новой стадии через эдитор, она автоматически добавляется в:
- `app/routing/message_router.py` (в `valid_routes`)
- `app/graph/graph_builder.py` (узел графа и маршруты)
- `app/stages/__init__.py` (импорт стадии)

**Никаких дополнительных импортов не требуется** — эдитор работает напрямую с файлами проекта.

### Подключение к инструментам

Эдитор подключается к инструментам через реестр инструментов:

#### 1. Импорты в `editor/tools_helper.py`

```python
from app.tools.registry import get_registry
from app.tools.config import configure_tools
```

#### 2. Импорты в `editor/tools_config_helper.py`

```python
from app.tools.config import configure_tools
from app.tools.registry import get_registry
```

#### 3. Структура инструментов

Каждый инструмент должен быть в папке `app/tools/<tool_name>/` и содержать:

```python
# app/tools/<tool_name>/tool.py
from langchain_core.tools import tool

@tool
def tool_name(param1: str, param2: int) -> str:
    """Описание инструмента"""
    # Логика инструмента
    pass
```

#### 4. Регистрация инструментов

Инструменты регистрируются в `app/tools/config.py`:

```python
from app.tools.registry import get_registry
from app.tools.get_services import get_services_tool
# ... другие импорты инструментов

def configure_tools():
    registry = get_registry()
    
    # Регистрация всех инструментов как доступных
    registry.register_tool(get_services_tool)
    # ... другие инструменты
    
    # Привязка инструментов к стадиям
    registry.register_tools(
        "information_gathering_stage",
        [
            get_services_tool,
            # ... другие инструменты для этой стадии
        ]
    )
```

#### 5. Использование инструментов в стадиях

Стадии получают инструменты через реестр в `app/stages/base_stage.py`:

```python
from app.tools.registry import get_registry

def execute(self, state: AgentState) -> AgentState:
    # Получаем инструменты для этой стадии из реестра
    registry = get_registry()
    stage_tools = registry.get_tools(self.stage_name)
    
    # Создаем цепочку с инструментами
    chain = prompt | llm.bind_tools(stage_tools)
```

#### 6. Обновление конфигурации инструментов

Эдитор обновляет конфигурацию напрямую в `app/tools/config.py`:

- Читает файл `app/tools/config.py`
- Находит блоки `registry.register_tools()` для каждой стадии
- Обновляет список инструментов в этих блоках
- Сохраняет изменения обратно в файл

**Важно**: Эдитор парсит файл `config.py` как текст, поэтому важно сохранять форматирование:
- Комментарии перед блоками регистрации
- Правильные отступы
- Правильный синтаксис Python

### Примеры подключения

#### Добавление нового инструмента

1. Создайте инструмент в `app/tools/new_tool/tool.py`:
```python
from langchain_core.tools import tool

@tool
def new_tool(param: str) -> str:
    """Описание нового инструмента"""
    return f"Результат: {param}"
```

2. Экспортируйте в `app/tools/new_tool/__init__.py`:
```python
from app.tools.new_tool.tool import new_tool as new_tool_tool
```

3. Зарегистрируйте в `app/tools/config.py`:
```python
from app.tools.new_tool import new_tool_tool

def configure_tools():
    registry = get_registry()
    registry.register_tool(new_tool_tool)  # Для отображения в эдиторе
    registry.register_tools("stage_name", [new_tool_tool])  # Для конкретной стадии
```

4. Эдитор автоматически увидит новый инструмент после перезапуска

#### Добавление новой стадии

1. Создайте файл `app/stages/new_stage.py`:
```python
from app.stages.base_stage import BaseStage
from app.config.agent_config import SYSTEM_INSTRUCTION

NEW_STAGE_INSTRUCTION = SYSTEM_INSTRUCTION + """
Промпт для новой стадии
"""

class NewStage(BaseStage):
    def create_llm(self):
        # ... создание LLM
        pass
```

2. Зарегистрируйте в роутере (`app/routing/message_router.py`):
```python
valid_routes = [
    # ... существующие стадии
    "new_stage",
]
```

3. Добавьте в граф (`app/graph/graph_builder.py`):
```python
from app.stages.new_stage import new_stage

graph.add_node("new_stage", new_stage)
```

4. Эдитор автоматически увидит новую стадию после перезапуска

## Запуск эдитора

```bash
python run_editor.py
```

Эдитор будет доступен по адресу: `http://localhost:5000`

## Важные замечания

1. **Изменения применяются сразу** — промпты и инструменты обновляются без перезапуска сервера агента
2. **Резервное копирование** — перед массовыми изменениями рекомендуется сделать бэкап файлов
3. **Синтаксис Python** — эдитор проверяет синтаксис перед сохранением, но лучше проверять вручную
4. **Реестр инструментов** — инструменты должны быть зарегистрированы через `configure_tools()` для отображения в эдиторе
5. **Имена стадий** — имена стадий должны соответствовать формату `<key>_stage` для корректной работы

