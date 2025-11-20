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
        """Извлекает информацию о стадиях из реестра агентов.
        
        Args:
            router_content: Содержимое message_router.py (не используется, оставлено для совместимости)
            
        Returns:
            Список словарей со стадиями
        """
        try:
            from app.agents.registry import get_registry
            
            registry = get_registry()
            agents = registry.get_all_agents()
            
            stages = []
            for agent in agents:
                stage_info = {
                    "key": agent["key"],
                    "name": agent["name"],
                    "prompt": self._extract_stage_prompt_from_file(agent["key"], agent["file"])
                }
                stages.append(stage_info)
            
            return stages
        except Exception as e:
            # Если реестр недоступен, возвращаем пустой список
            print(f"[WARNING] Не удалось загрузить агентов из реестра: {e}")
            return []
    
    def _extract_stage_prompt_from_file(self, stage_key: str, file_name: str) -> str:
        """Извлекает промпт для конкретной стадии из файла агента.
        
        Args:
            stage_key: Ключ стадии
            file_name: Имя файла агента
        """
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
