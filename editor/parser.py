# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Парсер для извлечения промптов и стадий из структуры проекта."""

import re
from pathlib import Path
from typing import Dict, List, Any


class PromptParser:
    """Класс для парсинга промптов из структуры проекта."""
    
    def __init__(self, project_root: Path):
        """Инициализация парсера.
        
        Args:
            project_root: Корневая директория проекта
        """
        self.project_root = Path(project_root)
        self.router_file = self.project_root / "app" / "agents" / "message_router.py"
        self.router_stage_file = self.project_root / "app" / "agents" / "router_stage.py"
        self.agents_dir = self.project_root / "app" / "agents"
    
    def parse(self) -> Dict[str, Any]:
        """Извлекает все промпты и стадии из проекта.
        
        Returns:
            Словарь с промптами и стадиями
        """
        router_content = self.router_file.read_text(encoding="utf-8")
        router_stage_content = self.router_stage_file.read_text(encoding="utf-8")
        
        return {
            "router_prompt": self._extract_router_prompt(router_stage_content),
            "stages": self._extract_stages(router_content)
        }
    
    def _extract_router_prompt(self, content: str) -> str:
        """Извлекает промпт роутера из router_stage.py."""
        pattern = r'ROUTER_STAGE_INSTRUCTION\s*=\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_stages(self, router_content: str) -> List[Dict[str, str]]:
        """Извлекает информацию о стадиях.
        
        Args:
            router_content: Содержимое message_router.py
            
        Returns:
            Список словарей со стадиями
        """
        stages = []
        
        # Извлекаем список валидных стадий из роутера
        valid_routes_pattern = r'valid_routes\s*=\s*\[(.*?)\]'
        match = re.search(valid_routes_pattern, router_content, re.DOTALL)
        if match:
            routes_str = match.group(1)
            route_keys = re.findall(r'"([^"]+)"', routes_str)
            
            for key in route_keys:
                stage_info = {
                    "key": key,
                    "name": self._get_stage_name(key),
                    "prompt": self._extract_stage_prompt_from_file(key)
                }
                stages.append(stage_info)
        
        return stages
    
    def _get_stage_name(self, key: str) -> str:
        """Преобразует ключ стадии в читаемое имя."""
        names = {
            "greeting": "Приветствие",
            "information_gathering": "Сбор информации",
            "booking": "Бронирование",
            "booking_to_master": "Бронирование к мастеру",
            "view_my_booking": "Просмотр моей записи",
            "reschedule": "Перенесение записи",
            "cancellation_request": "Отмена записи",
        }
        return names.get(key, key.replace("_", " ").title())
    
    def _extract_stage_prompt_from_file(self, stage_key: str) -> str:
        """Извлекает промпт для конкретной стадии из файла агента."""
        # Маппинг ключей стадий на имена файлов
        stage_file_mapping = {
            "greeting": "greeting_stage.py",
            "information_gathering": "information_gathering_stage.py",
            "booking": "booking_stage.py",
            "booking_to_master": "booking_to_master_stage.py",
            "view_my_booking": "view_my_booking_stage.py",
            "reschedule": "reschedule_stage.py",
            "cancellation_request": "cancellation_request_stage.py",
        }
        
        file_name = stage_file_mapping.get(stage_key)
        if not file_name:
            return ""
        
        stage_file = self.agents_dir / file_name
        if not stage_file.exists():
            return ""
        
        content = stage_file.read_text(encoding="utf-8")
        
        # Ищем промпт стадии в формате: STAGE_INSTRUCTION = """..."""
        pattern = rf'[A-Z_]+_STAGE_INSTRUCTION\s*=\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return ""
