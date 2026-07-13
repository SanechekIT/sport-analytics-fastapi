import re
from typing import List, Dict

def parse_meal_text(text: str) -> List[Dict[str, float]]:
    """
    Парсит текст и извлекает продукты с весом.
    
    Поддерживает форматы:
        - "200г курицы, 150г риса"
        - "курица 200г рис 150г"
        - "курица 200 рис 150"
        - "курица 200 грамм, рис 150 грамм"
    """
    if not text or not text.strip():
        return []
    
    # Убираем лишние пробелы и запятые
    text = text.replace(",", " ").strip()
    
    # Паттерн 1: число + единица + название
    pattern1 = r'(\d+)\s*([гмлкг]+)\s*([а-яёa-z\s]+)'
    matches1 = re.findall(pattern1, text.lower())
    
    result = []
    
    for weight, unit, name in matches1:
        weight = int(weight)
        if unit == 'кг':
            weight = weight * 1000
        result.append({
            "name": name.strip().strip(','),
            "weight": weight
        })
    
    # Паттерн 2: название + число (без единицы)
    if not result:
        pattern2 = r'([а-яёa-z\s]+)\s+(\d+)'
        matches2 = re.findall(pattern2, text.lower())
        for name, weight in matches2:
            result.append({
                "name": name.strip().strip(','),
                "weight": int(weight)
            })
    
    # Паттерн 3: название + число + "грамм"
    if not result:
        pattern3 = r'([а-яёa-z\s]+)\s+(\d+)\s*[гg]'
        matches3 = re.findall(pattern3, text.lower())
        for name, weight in matches3:
            result.append({
                "name": name.strip().strip(','),
                "weight": int(weight)
            })
    
    return result
