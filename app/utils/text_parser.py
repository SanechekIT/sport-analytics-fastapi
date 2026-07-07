import re
from typing import List, Dict

def parse_meal_text(text: str) -> List[Dict[str, float]]:
    """
    Парсит текст и извлекает продукты с весом.
    
    Пример:
        "200г курицы, 150г риса" 
        → [{"name": "курица", "weight": 200}, {"name": "рис", "weight": 150}]
    """
    pattern = r'(\d+)\s*([гмлкг]+)?\s*([а-яё\s]+)'
    matches = re.findall(pattern, text.lower())
    
    result = []
    for weight, unit, name in matches:
        weight = int(weight)
        # Конвертация единиц (мл → г для воды, и т.д.)
        if unit == 'мл':
            weight = weight  # для воды 1мл = 1г
        result.append({
            "name": name.strip(),
            "weight": weight
        })
    
    return result
