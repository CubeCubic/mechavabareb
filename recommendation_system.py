"""
Система рекомендаций программ обучения для абитуриентов
Грузинские университеты 2026
ОБНОВЛЕНО: использует официальную методику расчета баллов (სკალირებული ქულა)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import re


class UniversityRecommendationSystem:
    """
    Система рекомендаций программ обучения с официальной методикой расчета
    """
    
    def __init__(self, database_path: str):
        """
        Инициализация системы
        
        Args:
            database_path: Путь к CSV файлу с программами
        """
        self.df = pd.read_csv(database_path)
        self.prepare_data()
    
    def prepare_data(self):
        """
        Подготовка данных - очистка и нормализация
        """
        # Определяем тип университета (государственный/частный)
        self.df['uni_type'] = self.df['annual_tuition'].apply(
            lambda x: 'სახელმწიფო' if x == 2250.0 else 'კერძო'
        )
        
        # Очищаем названия программ
        self.df['program_name_clean'] = self.df['program_name'].str.strip()
        
        # Определяем категорию программы
        self.df['category'] = self.df.apply(self._categorize_program, axis=1)
        
        # Определяем город университета
        self.df['city'] = self.df['university_code'].apply(self._get_city)
        
        print(f"✓ Загружено программ: {len(self.df)}")
        print(f"✓ Университетов: {self.df['university_code'].nunique()}")
        print(f"✓ Государственные программы: {len(self.df[self.df['uni_type'] == 'სახელმწიფო'])}")
        print(f"✓ Частные программы: {len(self.df[self.df['uni_type'] == 'კერძო'])}")
    
    def _categorize_program(self, row) -> str:
        """Определяет категорию программы по названию"""
        name = row['program_name'].lower()
        uni_code = row['university_code']
        
        # Специальная обработка для теологических университетов
        theological_universities = [4, 88, 173, 174, 175, 177, 184, 194]
        if uni_code in theological_universities:
            return 'საღვთისმეტყველო'
        
        categories = {
            'საღვთისმეტყველო': ['თეოლოგ', 'ღვთისმეტყველ', 'საღმრთო', 'საეკლესიო', 'სასულიერო', 'ქრისტიანული ხელოვნებ'],
            'მედიცინა და ფარმაცია': ['მედიცინა', 'სტომატოლოგ', 'ფარმაცია', 'ექთანი', 'სამეანო', 'რეაბილიტაცი'],
            'IT და კომპიუტერული მეცნიერებები': ['კომპიუტერ', 'ინფორმაცი'],
            'ბიზნესი და ეკონომიკა': ['ბიზნეს', 'ეკონომიკ', 'მენეჯმენტ', 'ფინანს', 'ტურიზმ', 'მარკეტინგ'],
            'სამართალი': ['სამართალ', 'იურისპრუდენცი'],
            'ხელოვნება და დიზაინი': ['ხელოვნება', 'დიზაინ', 'არქიტექტურ', 'ხატვა', 'გრაფიკ', 'რესტავრაცი'],
            'მუსიკა და თეატრი': ['მუსიკ', 'თეატრ', 'კინო', 'მსახიობ', 'ბალეტ', 'ქორეოგრაფი'],
            'ინჟინერია': ['ინჟინერ', 'მშენებლობ', 'ენერგეტიკ', 'ტრანსპორტ'],
            'ენები და ფილოლოგია': ['ფილოლოგ', 'ქართული ენა', 'ინგლისური', 'გერმანული'],
            'საბუნებისმეტყველო მეცნიერებები': ['მათემატიკ', 'ფიზიკ', 'ქიმი', 'ბიოლოგ', 'გეოგრაფ', 'ეკოლოგ'],
            'სოციალური მეცნიერებები': ['ფსიქოლოგ', 'პოლიტიკ', 'სოციოლოგ', 'ისტორი', 'ფილოსოფი', 'ანთროპოლოგ'],
            'სასოფლო-სამეურნეო': ['აგრონომ', 'ვეტერინარ', 'სატყეო', 'ლანდშაფტ'],
            'განათლება': ['მასწავლებელ', 'განათლება', 'პედაგოგ']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in name:
                    return category
        
        return 'სხვა'
    
    def _get_city(self, uni_code: int) -> str:
        """Определяет город университета по коду"""
        city_map = {
            # Тбилиси
            1: 'თბილისი', 2: 'თბილისი', 3: 'თბილისი', 4: 'თბილისი',
            5: 'თბილისი', 6: 'თბილისი', 10: 'თბილისი', 12: 'თბილისი',
            33: 'თბილისი', 36: 'თბილისი', 40: 'თბილისი', 52: 'თბილისი',
            64: 'თბილისი', 85: 'თბილისი', 88: 'თბილისი', 98: 'თბილისი',
            115: 'თბილისი', 120: 'თბილისი', 121: 'თბილისი', 122: 'თბილისი',
            129: 'თბილისი', 131: 'თბილისი', 143: 'თბილისი', 145: 'თბილისი',
            152: 'თბილისი', 153: 'თბილისი', 154: 'თბილისი', 171: 'თბილისი',
            172: 'თბილისი', 175: 'თბილისი', 177: 'თბილისი',
            181: 'თბილისი', 183: 'თბილისი', 186: 'თბილისი', 195: 'თბილისი',
            198: 'თბილისი', 199: 'თბილისი', 201: 'თბილისი', 202: 'თბილისი',
            203: 'თბილისი', 204: 'თბილისი', 206: 'თბილისი',
            # Кутаиси
            9: 'ქუთაისი', 19: 'ქუთაისი', 174: 'ქუთაისი', 197: 'ქუთაისი',
            # Телави
            71: 'თელავი',
            # Зугдиди
            97: 'ზუგდიდი',
            # Батуми
            53: 'ბათუმი', 114: 'ბათუმი', 130: 'ბათუმი', 140: 'ბათუმი',
            184: 'ბათუმი', 192: 'ბათუმი', 205: 'ბათუმი',
            # Гори
            133: 'გორი', 155: 'გორი',
            # Ахалцихе
            14: 'ახალციხე', 194: 'ახალციხე',
            # სოფ. ხიჭაური
            142: 'სოფ. ხიჭაური',
            # სოფ. გრემი (Греми)
            173: 'სოფ. გრემი'
        }
        return city_map.get(uni_code, 'თბილისი')
    
    def filter_programs(self, 
                       city: str = None,
                       uni_type: str = None,
                       category: str = None,
                       teaching_language: str = None) -> pd.DataFrame:
        """
        Фильтрация программ по критериям
        
        Args:
            city: Город
            uni_type: Тип вуза (სახელმწიფო/კერძო)
            category: Категория программы
            teaching_language: Язык обучения
            
        Returns:
            Отфильтрованный DataFrame
        """
        filtered = self.df.copy()
        
        if city:
            filtered = filtered[filtered['city'] == city]
        
        if uni_type:
            filtered = filtered[filtered['uni_type'] == uni_type]
        
        if category:
            filtered = filtered[filtered['category'] == category]
        
        if teaching_language:
            filtered = filtered[filtered['teaching_language'] == teaching_language]
        
        return filtered
    
    def get_required_exams(self, 
                          city: str = None,
                          uni_type: str = None,
                          category: str = None,
                          teaching_language: str = None) -> Dict:
        """
        Получает список обязательных и выборочных экзаменов для отфильтрованных программ
        
        Returns:
            Dictionary с mandatory и elective экзаменами
        """
        filtered = self.filter_programs(city, uni_type, category, teaching_language)
        
        if len(filtered) == 0:
            return {'mandatory': [], 'elective': []}
        
        mandatory_exams = set()
        elective_exams = set()
        
        # Собираем обязательные экзамены
        for i in range(1, 5):
            col = f'mandatory_exam_{i}'
            exams = filtered[col].dropna().unique()
            for exam in exams:
                if str(exam).strip() and not str(exam).isdigit():
                    mandatory_exams.add(str(exam).strip())
        
        # Собираем выборочные экзамены
        for i in range(1, 7):
            col = f'elective_exam_{i}_name'
            exams = filtered[col].dropna().unique()
            for exam in exams:
                if str(exam).strip() and not str(exam).isdigit():
                    elective_exams.add(str(exam).strip())
        
        return {
            'mandatory': sorted(list(mandatory_exams)),
            'elective': sorted(list(elective_exams))
        }
    
    def _convert_to_scaled_score(self, raw_percentage: float) -> float:
        """
        Конвертирует сырой процент (0-100) в скалированный балл (100-200)
        
        Официальный процесс:
        1. Выравнивание (გათანაბრება) - корректировка сложности варианта
        2. Скалирование (სკალირება) - Z = (X - E) / SD, потом Scaled = 15*Z + 150
        
        Для нашей симуляции (без реальных данных распределения):
        - 0% → 100 (scaled)
        - 50% → 150 (scaled, среднее)
        - 100% → 200 (scaled)
        
        Args:
            raw_percentage: Балл от 0 до 100
            
        Returns:
            Скалированный балл от 100 до 200
        """
        if raw_percentage <= 0:
            return 100.0
        elif raw_percentage >= 100:
            return 200.0
        else:
            # Линейный маппинг: scaled = 100 + raw_percentage
            # Симулирует официальную шкалу где среднее=150, диапазон=100-200
            return 100.0 + raw_percentage
    
    def _parse_percentage(self, value) -> float:
        """Извлекает процент из строки"""
        if pd.isna(value):
            return 0.0
        
        value_str = str(value)
        numbers = re.findall(r'\d+', value_str)
        if numbers:
            return float(numbers[0])
        return 0.0
    
    def calculate_score(self, program, exam_scores: Dict[str, float]) -> Dict:
        """
        Рассчитывает конкурсный балл по ОФИЦИАЛЬНОЙ грузинской методике
        
        Формула из официального справочника (стр. 32):
        საკონკურსო ქულა = Σ(სკალირებული ქულა × კოეფიციენტი)
        Competitive Score = Σ(Scaled Score × Coefficient)
        
        Процесс:
        1. Конвертируем сырые баллы (0-100%) в скалированные (100-200)
        2. Умножаем каждый скалированный балл на его коэффициент
        3. Суммируем все взвешенные баллы = конкурсный балл
        4. Проверяем минимальные пороги
        
        Args:
            program: DataFrame row с информацией о программе
            exam_scores: dict вида {exam_name: score_percentage}
            
        Returns:
            dict с compatibility, competitive_score и admission_chance
        """
        competitive_score = 0.0
        total_coefficients = 0.0
        failed_minimums = []
        scored_exams = []
        
        # Обрабатываем обязательные экзамены
        for i in range(1, 5):
            exam_col = f'mandatory_exam_{i}'
            coef_col = f'mandatory_exam_{i}_coef'
            min_col = f'mandatory_exam_{i}_min'
            
            if pd.notna(program[exam_col]):
                exam_name = str(program[exam_col]).strip()
                coefficient = float(program[coef_col]) if pd.notna(program[coef_col]) else 1.0
                minimum = self._parse_percentage(program[min_col]) if pd.notna(program[min_col]) else 0.0
                
                # Получаем сырой балл (0-100%)
                raw_score = exam_scores.get(exam_name, 0.0)
                
                # Проверяем минимальный порог (на сыром балле)
                if raw_score < minimum:
                    failed_minimums.append(f"{exam_name} ({raw_score}% < {minimum}%)")
                
                # Конвертируем в скалированный балл (100-200)
                scaled_score = self._convert_to_scaled_score(raw_score)
                
                # Добавляем к конкурсному баллу: scaled × coefficient
                contribution = scaled_score * coefficient
                competitive_score += contribution
                total_coefficients += coefficient
                
                scored_exams.append({
                    'name': exam_name,
                    'raw': raw_score,
                    'scaled': round(scaled_score, 2),
                    'coefficient': coefficient,
                    'contribution': round(contribution, 2)
                })
        
        # Обрабатываем выборочные экзамены - выбираем лучший
        elective_candidates = []
        for i in range(1, 7):
            exam_col = f'elective_exam_{i}_name'
            coef_col = f'elective_exam_{i}_coef'
            min_col = f'elective_exam_{i}_min'
            
            if pd.notna(program[exam_col]):
                exam_name = str(program[exam_col]).strip()
                coefficient = float(program[coef_col]) if pd.notna(program[coef_col]) else 1.0
                minimum = self._parse_percentage(program[min_col]) if pd.notna(program[min_col]) else 0.0
                
                raw_score = exam_scores.get(exam_name, 0.0)
                
                # Учитываем только если проходит минимум
                if raw_score >= minimum:
                    scaled_score = self._convert_to_scaled_score(raw_score)
                    contribution = scaled_score * coefficient
                    
                    elective_candidates.append({
                        'name': exam_name,
                        'raw': raw_score,
                        'scaled': round(scaled_score, 2),
                        'coefficient': coefficient,
                        'contribution': round(contribution, 2)
                    })
        
        # Выбираем лучший выборочный (наибольший вклад в конкурсный балл)
        if elective_candidates:
            best_elective = max(elective_candidates, key=lambda x: x['contribution'])
            competitive_score += best_elective['contribution']
            total_coefficients += best_elective['coefficient']
            scored_exams.append(best_elective)
        
        # Рассчитываем процент совместимости
        # Максимально возможный балл = 200 (scaled) × total_coefficients
        # Фактический балл = competitive_score
        if total_coefficients > 0:
            max_possible = 200.0 * total_coefficients
            compatibility = (competitive_score / max_possible) * 100.0
        else:
            compatibility = 0.0
        
        # Определяем шанс поступления на основе совместимости
        if failed_minimums:
            admission_chance = "არ აკმაყოფილებს მინიმუმს"
            chance_level = "failed"
        elif compatibility >= 90:
            admission_chance = "ძალიან მაღალი"
            chance_level = "very_high"
        elif compatibility >= 75:
            admission_chance = "მაღალი"
            chance_level = "high"
        elif compatibility >= 60:
            admission_chance = "საშუალო"
            chance_level = "medium"
        elif compatibility >= 45:
            admission_chance = "დაბალი"
            chance_level = "low"
        else:
            admission_chance = "ძალიან დაბალი"
            chance_level = "very_low"
        
        return {
            'compatibility': round(compatibility, 1),
            'competitive_score': round(competitive_score, 2),
            'admission_chance': admission_chance,
            'chance_level': chance_level,
            'failed_minimums': failed_minimums,
            'scored_exams': scored_exams
        }
    
    def recommend_programs(self,
                          city: str,
                          uni_type: str,
                          category: str,
                          teaching_language: str,
                          exam_scores: Dict[str, float],
                          top_n: int = 20) -> List[Dict]:
        """
        Главная функция рекомендации программ
        
        Args:
            city: Город
            uni_type: Тип вуза
            category: Категория программы
            teaching_language: Язык обучения
            exam_scores: Баллы по экзаменам {exam_name: score_0_to_100}
            top_n: Количество рекомендаций
            
        Returns:
            Список рекомендованных программ с оценками
        """
        # Фильтруем программы
        filtered = self.filter_programs(city, uni_type, category, teaching_language)
        
        if len(filtered) == 0:
            return []
        
        # Рассчитываем баллы для каждой программы
        results = []
        
        for idx, program in filtered.iterrows():
            score_data = self.calculate_score(program, exam_scores)
            
            # Получаем стоимость (бесплатно для государственных в 2026)
            if program['uni_type'] == 'სახელმწიფო':
                cost_display = "უფასო"
            else:
                cost_display = f"{int(program['annual_tuition'])} ლარი"
            
            result = {
                'program_code': int(program['program_code']),
                'program_name': program['program_name'],
                'university_code': int(program['university_code']),
                'city': program['city'],
                'uni_type': program['uni_type'],
                'tuition': float(program['annual_tuition']),
                'cost_display': cost_display,
                'places': int(program['total_places']) if pd.notna(program['total_places']) else 0,
                'teaching_language': program['teaching_language'],
                'credits': int(program['credits']) if pd.notna(program['credits']) else 240,
                'compatibility': score_data['compatibility'],
                'competitive_score': score_data['competitive_score'],
                'admission_chance': score_data['admission_chance'],
                'chance_level': score_data['chance_level'],
                'failed_minimums': score_data['failed_minimums'],
                'accreditation': program.get('accreditation_status', ''),
                'special_note': program.get('special_note', '')
            }
            
            results.append(result)
        
        # Сортируем по конкурсному баллу (DESC)
        results.sort(key=lambda x: x['competitive_score'], reverse=True)
        
        return results[:top_n]
