"""
Вспомогательный модуль для работы с инструментами в редакторе.
"""

import inspect
from typing import Dict, List, Any
from langchain_core.tools import BaseTool


def get_all_tools() -> List[BaseTool]:
    """
    Получить все инструменты напрямую из модулей.
    
    Returns:
        Список всех инструментов
    """
    try:
        # Импортируем все инструменты напрямую
        from app.tools.get_categories import get_categories_tool
        from app.tools.get_services import get_services_tool
        from app.tools.view_service import view_service_tool
        from app.tools.about_salon import about_salon_tool
        from app.tools.masters import masters_tool
        from app.tools.book_times import book_times_tool
        from app.tools.find_slots import find_slots_tool
        from app.tools.create_booking import create_booking_tool
        from app.tools.get_client_records import get_client_records_tool
        from app.tools.reschedule_booking import reschedule_booking_tool
        from app.tools.cancel_booking import cancel_booking_tool
        from app.tools.find_master_by_service import find_master_by_service_tool
        from app.tools.call_manager import call_manager_tool
        
        tools = [
            get_categories_tool,
            get_services_tool,
            view_service_tool,
            about_salon_tool,
            masters_tool,
            book_times_tool,
            find_slots_tool,
            create_booking_tool,
            get_client_records_tool,
            reschedule_booking_tool,
            cancel_booking_tool,
            find_master_by_service_tool,
            call_manager_tool,
        ]
        
        # Логируем для отладки
        print(f"[DEBUG] Загружено инструментов: {len(tools)}")
        if tools:
            print(f"[DEBUG] Имена инструментов: {[t.name for t in tools]}")
        
        return tools
    except Exception as e:
        # Логируем ошибку для диагностики
        import traceback
        error_msg = f"Ошибка загрузки инструментов: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_msg}")
        # Если не удалось загрузить инструменты, возвращаем пустой список
        return []


def get_tool_info(tool: BaseTool) -> Dict[str, Any]:
    """
    Получить информацию об инструменте для отображения в редакторе.
    
    Args:
        tool: Инструмент LangChain
        
    Returns:
        Словарь с информацией об инструменте
    """
    info = {
        "name": tool.name,
        "description": tool.description or "",
        "parameters": []
    }
    
    # Получаем схему инструмента
    try:
        # Получаем JSON схему инструмента через метод schema()
        schema = tool.schema()
        
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'string')
            
            # Обрабатываем разные типы
            if param_type == 'integer':
                param_type = 'number'
            elif 'enum' in param_info:
                param_type = 'enum'
            
            param_data = {
                "name": param_name,
                "type": param_type,
                "description": param_info.get('description', ''),
                "required": param_name in required,
                "default": param_info.get('default')
            }
            
            # Добавляем enum значения если есть
            if 'enum' in param_info:
                param_data['enum'] = param_info['enum']
            
            info["parameters"].append(param_data)
    except Exception as e:
        # Если не удалось получить схему через schema(), пробуем через inspect
        try:
            # Пробуем получить функцию инструмента
            func = tool.func if hasattr(tool, 'func') else (tool._run if hasattr(tool, '_run') else None)
            
            if func:
                sig = inspect.signature(func)
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue
                    
                    # Определяем тип из аннотации
                    param_type = 'string'
                    if param.annotation != inspect.Parameter.empty:
                        if param.annotation == int:
                            param_type = 'number'
                        elif param.annotation == bool:
                            param_type = 'boolean'
                    
                    param_data = {
                        "name": param_name,
                        "type": param_type,
                        "description": '',
                        "required": param.default == inspect.Parameter.empty,
                        "default": param.default if param.default != inspect.Parameter.empty else None
                    }
                    info["parameters"].append(param_data)
        except Exception as inner_e:
            # Если ничего не получилось, просто возвращаем базовую информацию
            pass
    
    return info


def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Выполнить инструмент с заданными аргументами.
    
    Args:
        tool_name: Имя инструмента
        args: Аргументы для инструмента
        
    Returns:
        Результат выполнения инструмента
    """
    try:
        tools = get_all_tools()
        
        if not tools:
            return {
                "success": False,
                "error": "Не удалось загрузить инструменты. Убедитесь, что модули app доступны."
            }
        
        # Находим инструмент по имени
        tool = None
        for t in tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return {
                "success": False,
                "error": f"Инструмент '{tool_name}' не найден"
            }
        
        # Выполняем инструмент
        result = tool.invoke(args)
        
        return {
            "success": True,
            "result": str(result) if result else "Инструмент выполнен успешно, но не вернул результат"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"{str(e)}\n\n{traceback.format_exc()}"
        }

