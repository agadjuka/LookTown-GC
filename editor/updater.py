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

"""Обновление промптов и стадий в структуре проекта."""

import re
from pathlib import Path
from typing import Optional


class PromptUpdater:
    """Класс для обновления промптов в структуре проекта."""
    
    def __init__(self, project_root: Path):
        """Инициализация обновлятора.
        
        Args:
            project_root: Корневая директория проекта
        """
        self.project_root = Path(project_root)
        self.router_file = self.project_root / "app" / "agents" / "message_router.py"
        self.router_stage_file = self.project_root / "app" / "agents" / "router_stage.py"
        self.agents_dir = self.project_root / "app" / "agents"
        self.agents_init_file = self.agents_dir / "__init__.py"
    
    def _read_content(self, file_path: Path) -> str:
        """Читает содержимое файла."""
        return file_path.read_text(encoding="utf-8")
    
    def _write_content(self, file_path: Path, content: str) -> None:
        """Записывает содержимое в файл."""
        file_path.write_text(content, encoding="utf-8")
    
    def update_system_prompt(self, new_prompt: str) -> None:
        """Обновляет основной системный промпт (в текущей структуре не используется)."""
        # В текущей структуре нет отдельного системного промпта
        # Каждый агент имеет свой собственный промпт
        pass
    
    def update_router_prompt(self, new_prompt: str) -> None:
        """Обновляет промпт роутера в router_stage.py."""
        content = self._read_content(self.router_stage_file)
        pattern = r'(ROUTER_STAGE_INSTRUCTION\s*=\s*""").*?(""")'
        replacement = rf'\1{new_prompt}\2'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        self._write_content(self.router_stage_file, content)
    
    def update_stage_prompt(self, stage_key: str, new_prompt: str) -> None:
        """Обновляет промпт стадии в файле агента."""
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
            raise ValueError(f"Неизвестная стадия: {stage_key}")
        
        stage_file = self.agents_dir / file_name
        if not stage_file.exists():
            raise FileNotFoundError(f"Файл агента не найден: {stage_file}")
        
        content = self._read_content(stage_file)
        
        # Ищем и обновляем промпт стадии в формате: STAGE_INSTRUCTION = """..."""
        pattern = rf'([A-Z_]+_STAGE_INSTRUCTION\s*=\s*""").*?(""")'
        replacement = rf'\1{new_prompt}\2'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        self._write_content(stage_file, content)
    
