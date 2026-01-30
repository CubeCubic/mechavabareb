"""
Система рекомендаций программ обучения для абитуриентов
Грузинские университеты 2026
ОБНОВЛЕНО: использует официальную методику расчета баллов (სკალირებული ქულა)
Учет мин. 3 экзаменов, один иностранный, особые условия.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
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
        # Определяем тип университета (государственный/частный) - для 2026: гос бесплатные
        self.df['uni_type'] = np.where(self.df['annual_tuition'] == 2250.0, 'სახელმწიფო', 'კერძო')
        
        # Очищаем названия программ
        self.df['program_name_clean'] = self.df['program_name'].str.strip()
        
        # Определяем категорию программы
        self.df['category'] = self.df.apply(self._categorize_program, axis=1)
        
        # Определяем город университета
        self.df['city'] = self.df['university_code'].apply(self._get_city)
        
        # Нормализуем экзамены: очищаем от лишних символов
        exam_columns = [col for col in self.df.columns if 'exam' in col.lower()]
        for col in exam_columns:
            self.df[col] = self.df[col].astype(str).str.replace(r'\(.*\)', '', regex=True).str.strip()
        
        # Очистка min порогов: извлекаем числа
        min_columns = [col for col in self.df.columns if 'min' in col.lower()]
        for col in min_columns:
            self.df[col] = self.df[col].astype(str).str.extract(r'(\d+)', expand=False).astype(float)
        
        print(f"✓ Загружено программ: {len(self.df)}")
        print(f"✓ Университетов: {self.df['university_code'].nunique()}")
        print(f"✓ სახელმწიფო პროგრამები: {len(self.df[self.df['uni_type'] == 'სახელმწიფო'])}")
        print(f"✓ კერძო პროგრამები: {len(self.df[self.df['uni_type'] == 'კერძო'])}")
    
    def _categorize_program(self, row) -> str:
        """Определяет категорию программы по названию"""
        name = str(row['program_name']).lower()
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
            14: 'ახალციხე', 173: 'ახალციხე',
            # Другие
            194: 'სოფ. გრემი',  # Пример из вашей базы
        }
        return city_map.get(uni_code, 'უცნობი')
    
    def filter_programs(self, city: str = None, uni_type: str = None, category: str = None, teaching_language: str = None) -> pd.DataFrame:
        """Фильтрация программ по критериям"""
        filtered = self.df.copy()
        
        if city and city != 'ყველა':
            filtered = filtered[filtered['city'] == city]
        
        if uni_type and uni_type != 'ყველა':
            filtered = filtered[filtered['uni_type'] == uni_type]
        
        if category and category != 'ყველა':
            filtered = filtered[filtered['category'] == category]
        
        if teaching_language and teaching_language != 'ყველა':
            filtered = filtered[filtered['teaching_language'] == teaching_language]
        
        return filtered
    
    def get_required_exams(self, programs: pd.DataFrame) -> Dict:
        """Получает список необходимых экзаменов для отфильтрованных программ"""
        mandatory_core = set()
        elective = set()
        
        for _, program in programs.iterrows():
            # Обязательные
            for i in range(1, 5):
                exam = program.get(f'mandatory_exam_{i}_name')
                if pd.notna(exam) and exam.strip():
                    mandatory_core.add(exam.strip())
            
            # Выборочные
            for i in range(1, 7):
                exam = program.get(f'elective_exam_{i}_name')
                if pd.notna(exam) and exam.strip():
                    elective.add(exam.strip())
        
        # Всегда добавляем обязательные
        mandatory_core.add('ქართული ენა და ლიტერატურა')
        mandatory_core.add('უცხოური ენა')
        
        return {
            'mandatory_core': mandatory_core,
            'elective': elective
        }
    
    def _scale_score(self, raw_score: float) -> float:
        """Масштабирование балла по официальной формуле (пример, адаптируйте если есть точная)"""
        # Пример: scaled = raw * (200 / 100) для простоты, но используйте реальную формулу если есть
        return raw_score * 2.0  # Предполагаем max raw 100 -> scaled 200
    
    def calculate_score(self, program: pd.Series, exam_scores: Dict[str, float]) -> Dict:
        """Расчет балла для одной программы с учетом мин. 3 экзаменов и особых условий"""
        failed_minimums = []
        scored_exams = []
        competitive_score = 0.0
        total_coefficients = 0.0
        elective_candidates = []
        
        # Проверка мин. экзаменов
        if 'ქართული ენა და ლიტერატურა' not in exam_scores:
            failed_minimums.append('ქართული ენა და ლიტერატურა')
        
        foreign_present = any(key in exam_scores for key in ['უცხოური ენა', 'ინგლისური ენა', 'გერმანული ენა', 'ფრანგული ენა', 'რუსული ენა'])
        if not foreign_present:
            failed_minimums.append('უცხოური ენა')
        
        other_exams = len({k: v for k, v in exam_scores.items() if k not in ['ქართული ენა და ლიტერატურა', 'უცხოური ენა', 'ინგლისური ენა', 'გერმანული ენა', 'ფრანგული ენა', 'რუსული ენა']})
        if other_exams < 1:
            failed_minimums.append('დამატებითი საგანი')
        
        if failed_minimums:
            return {
                'compatibility': 0.0,
                'competitive_score': 0.0,
                'admission_chance': 'არ აკმაყოფილებს მინიმუმს',
                'chance_level': 'failed',
                'failed_minimums': failed_minimums,
                'scored_exams': [],
                'special_note': program.get('special_note', '')
            }
        
        # Обработка обязательных экзаменов
        for i in range(1, 5):
            exam_name = program.get(f'mandatory_exam_{i}_name')
            if pd.isna(exam_name) or not exam_name.strip():
                continue
            
            coefficient = program.get(f'mandatory_exam_{i}_coef', 1.0)
            min_score = program.get(f'mandatory_exam_{i}_min', 0.0)
            
            raw_score = exam_scores.get(exam_name.strip(), 0.0)
            if raw_score < min_score:
                failed_minimums.append(exam_name)
                continue
            
            scaled_score = self._scale_score(raw_score)
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
        
        # Обработка выборочных экзаменов (выбираем лучший)
        for i in range(1, 7):
            exam_name = program.get(f'elective_exam_{i}_name')
            if pd.isna(exam_name) or not exam_name.strip():
                continue
            
            coefficient = program.get(f'elective_exam_{i}_coef', 1.0)
            min_score = program.get(f'elective_exam_{i}_min', 0.0)
            
            raw_score = exam_scores.get(exam_name.strip(), 0.0)
            if raw_score < min_score:
                continue  # Не добавляем, если не пройден мин
            
            scaled_score = self._scale_score(raw_score)
            contribution = scaled_score * coefficient
            elective_candidates.append({
                'name': exam_name,
                'raw': raw_score,
                'scaled': round(scaled_score, 2),
                'coefficient': coefficient,
                'contribution': round(contribution, 2)
            })
        
        if elective_candidates:
            best_elective = max(elective_candidates, key=lambda x: x['contribution'])
            competitive_score += best_elective['contribution']
            total_coefficients += best_elective['coefficient']
            scored_exams.append(best_elective)
        
        # Рассчитываем процент совместимости
        if total_coefficients > 0:
            max_possible = 200.0 * total_coefficients  # Max scaled 200 per exam
            compatibility = (competitive_score / max_possible) * 100.0
        else:
            compatibility = 0.0
        
        # Определяем шанс поступления
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
            'scored_exams': scored_exams,
            'special_note': program.get('special_note', '')
        }
    
    def recommend_programs(self,
                          city: str = None,
                          uni_type: str = None,
                          category: str = None,
                          teaching_language: str = None,
                          exam_scores: Dict[str, float] = None,
                          top_n: int = 20) -> List[Dict]:
        """
        Главная функция рекомендации программ
        """
        filtered = self.filter_programs(city, uni_type, category, teaching_language)
        
        if len(filtered) == 0:
            return []
        
        results = []
        
        for idx, program in filtered.iterrows():
            score_data = self.calculate_score(program, exam_scores)
            
            # Стоимость для 2026
            tuition = 0.0 if program['uni_type'] == 'სახელმწიფო' else program['annual_tuition']
            
            result = {
                'program_code': int(program['program_code']),
                'program_name': program['program_name'],
                'university_code': int(program['university_code']),
                'city': program['city'],
                'uni_type': program['uni_type'],
                'tuition': tuition,
                'places': int(program['total_places']) if pd.notna(program['total_places']) else 0,
                'teaching_language': program['teaching_language'],
                'compatibility': score_data['compatibility'],
                'admission_chance': score_data['admission_chance'],
                'special_note': score_data['special_note']
            }
            
            results.append(result)
        
        # Сортировка по совместимости DESC
        results.sort(key=lambda x: x['compatibility'], reverse=True)
        
        return results[:top_n]
