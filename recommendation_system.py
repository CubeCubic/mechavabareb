"""
Система рекомендаций программ обучения для абитуриентов
Грузинские университеты 2026
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import re


class UniversityRecommendationSystem:
    """
    Система рекомендаций программ обучения
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
        
        categories = {
            'მედიცინა და ფარმაცია': ['მედიცინა', 'სტომატოლოგ', 'ფარმაცია'],
            'IT და კომპიუტერული მეცნიერებები': ['კომპიუტერ', 'ინფორმაცი'],
            'ბიზნესი და ეკონომიკა': ['ბიზნეს', 'ეკონომიკ', 'მენეჯმენტ', 'ფინანს', 'ტურიზმ'],
            'სამართალი': ['სამართალ'],
            'ხელოვნება და დიზაინი': ['ხელოვნება', 'დიზაინ', 'არქიტექტურ', 'ხატვა'],
            'მუსიკა და თეატრი': ['მუსიკ', 'თეატრ', 'კინო', 'მსახიობ'],
            'ინჟინერია': ['ინჟინერ', 'მშენებლობ'],
            'ენები და ფილოლოგია': ['ფილოლოგ'],
            'საბუნებისმეტყველო მეცნიერებები': ['მათემატიკ', 'ფიზიკ', 'ქიმი', 'ბიოლოგ'],
            'სოციალური მეცნიერებები': ['ფსიქოლოგ', 'პოლიტიკ', 'სოციოლოგ', 'ისტორი'],
            'სასოფლო-სამეურნეო': ['აგრონომ', 'ვეტერინარ'],
            'განათლება': ['მასწავლებელ', 'განათლება']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in name:
                    return category
        
        return 'სხვა'
    
    def _get_city(self, uni_code: int) -> str:
        """Определяет город университета по коду"""
        # Маппинг университетов на города
        city_map = {
            1: 'თბილისი', 2: 'თბილისი', 3: 'თბილისი', 4: 'თბილისი',
            5: 'თბილისი', 6: 'თბილისი', 10: 'თბილისი', 12: 'თბილისი',
            64: 'თბილისი', 85: 'თბილისი', 88: 'თბილისი', 98: 'თბილისი',
            115: 'თბილისი', 120: 'თბილისი', 121: 'თბილისი', 122: 'თბილისი',
            9: 'ქუთაისი',
            71: 'თელავი',
            97: 'ზუგდიდი',
            114: 'ბათუმი', 129: 'ბათუმი'
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
            city: Город (თბილისი, ბათუმი и т.д.)
            uni_type: Тип вуза (სახელმწიფო/კერძო)
            category: Категория программы
            teaching_language: Язык обучения
            
        Returns:
            Отфильтрованный датафрейм программ
        """
        filtered = self.df.copy()
        
        if city and city != 'ყველა':
            filtered = filtered[filtered['city'] == city]
        
        if uni_type and uni_type != 'ყველა':
            filtered = filtered[filtered['uni_type'] == uni_type]
        
        if category and category != 'ყველა':
            filtered = filtered[filtered['category'] == category]
        
        if teaching_language and teaching_language != 'ყველა':
            # Проверяем язык обучения (может быть записан по-разному)
            filtered = filtered[filtered['teaching_language'].str.contains(
                teaching_language, case=False, na=False
            )]
        
        return filtered
    
    def get_required_exams(self, filtered_programs: pd.DataFrame) -> Dict:
        """
        Получает список всех необходимых экзаменов для отфильтрованных программ
        
        Returns:
            Словарь с обязательными и выборочными предметами
        """
        mandatory_exams = set()
        elective_exams = set()
        
        # Собираем обязательные экзамены
        for i in range(1, 5):
            col = f'mandatory_exam_{i}'
            exams = filtered_programs[col].dropna().unique()
            for exam in exams:
                if pd.notna(exam) and str(exam).strip():
                    # Очищаем название экзамена
                    exam_clean = str(exam).strip()
                    if exam_clean and exam_clean not in ['1', '2', '3', '4']:
                        mandatory_exams.add(exam_clean)
        
        # Собираем выборочные экзамены
        for i in range(1, 7):
            col = f'elective_exam_{i}_name'
            exams = filtered_programs[col].dropna().unique()
            for exam in exams:
                if pd.notna(exam) and str(exam).strip():
                    exam_clean = str(exam).strip()
                    # Исключаем числа (это места, а не названия)
                    if exam_clean and not exam_clean.isdigit():
                        elective_exams.add(exam_clean)
        
        # Грузинский язык и иностранный язык - всегда обязательны
        mandatory_core = {
            'ქართული ენა და ლიტერატურა',
            'უცხოური ენა'
        }
        
        return {
            'mandatory_core': mandatory_core,
            'mandatory_all': mandatory_exams,
            'elective': elective_exams
        }
    
    def calculate_score(self, 
                       program: pd.Series,
                       exam_scores: Dict[str, float],
                       foreign_language: str) -> Tuple[float, bool, str]:
        """
        Рассчитывает общий балл абитуриента для программы
        
        Args:
            program: Программа (строка датафрейма)
            exam_scores: Словарь {предмет: балл_в_процентах}
            foreign_language: Выбранный иностранный язык
            
        Returns:
            (weighted_score, meets_requirements, message)
        """
        total_score = 0
        total_coef = 0
        meets_requirements = True
        messages = []
        
        # Проверяем обязательные экзамены
        for i in range(1, 5):
            exam_name = program.get(f'mandatory_exam_{i}')
            if pd.notna(exam_name) and str(exam_name).strip():
                try:
                    coef = float(program.get(f'mandatory_exam_{i}_coef', 0))
                except (ValueError, TypeError):
                    coef = 0
                    
                min_score_str = program.get(f'mandatory_exam_{i}_min', '')
                
                # Парсим минимальный балл
                min_score = self._parse_min_score(min_score_str)
                
                # Находим балл абитуриента
                user_score = None
                
                # Обработка иностранного языка
                if 'უცხოური ენა' in str(exam_name):
                    user_score = exam_scores.get(foreign_language, 0)
                elif str(exam_name) in exam_scores:
                    user_score = exam_scores[str(exam_name)]
                
                if user_score is not None and coef > 0:
                    # Проверяем минимальный порог
                    if user_score <= min_score:
                        meets_requirements = False
                        messages.append(f"არ აკმაყოფილებს მინიმუმს: {exam_name} ({user_score}% < {min_score}%)")
                    
                    # Добавляем взвешенный балл
                    total_score += float(user_score) * float(coef)
                    total_coef += float(coef)
        
        # Проверяем выборочные экзамены (нужен хотя бы один)
        elective_found = False
        best_elective_score = 0
        
        for i in range(1, 7):
            exam_name = program.get(f'elective_exam_{i}_name')
            if pd.notna(exam_name) and str(exam_name).strip() and not str(exam_name).isdigit():
                try:
                    coef = float(program.get(f'elective_exam_{i}_coef', 0))
                except (ValueError, TypeError):
                    coef = 0
                
                min_score_str = program.get(f'elective_exam_{i}_min', '')
                min_score = self._parse_min_score(min_score_str)
                
                exam_name = str(exam_name).strip()
                if exam_name in exam_scores:
                    user_score = exam_scores[exam_name]
                    
                    if user_score > min_score:
                        elective_found = True
                        weighted = float(user_score) * float(coef)
                        if weighted > best_elective_score:
                            best_elective_score = weighted
                            mandatory_coefs_sum = sum([
                                float(program.get(f'mandatory_exam_{j}_coef', 0)) 
                                for j in range(1, 5) 
                                if pd.notna(program.get(f'mandatory_exam_{j}_coef'))
                            ])
                            total_coef = mandatory_coefs_sum + coef
        
        if not elective_found and program.get('elective_exams'):
            meets_requirements = False
            messages.append("არცერთი საარჩევი საგანი არ არის შეყვანილი")
        
        total_score += best_elective_score
        
        # Финальный взвешенный балл
        if total_coef > 0:
            weighted_score = total_score / total_coef
        else:
            weighted_score = 0
        
        return weighted_score, meets_requirements, "; ".join(messages)
    
    def _parse_min_score(self, min_score_str) -> float:
        """Парсит минимальный балл из строки"""
        if pd.isna(min_score_str):
            return 0
        
        min_str = str(min_score_str)
        # Извлекаем число из строки типа "40%-ზე მეტი"
        numbers = re.findall(r'\d+', min_str)
        if numbers:
            return float(numbers[0])
        return 0
    
    def recommend_programs(self,
                          city: str,
                          uni_type: str,
                          category: str,
                          teaching_language: str,
                          exam_scores: Dict[str, float],
                          foreign_language: str,
                          top_n: int = 10) -> List[Dict]:
        """
        Главная функция рекомендации программ
        
        Args:
            city: Город
            uni_type: Тип вуза
            category: Категория программы
            teaching_language: Язык обучения
            exam_scores: Баллы по экзаменам
            foreign_language: Выбранный иностранный язык
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
            score, meets_req, message = self.calculate_score(
                program, exam_scores, foreign_language
            )
            
            # Рассчитываем процент совместимости (0-100%)
            compatibility = min(100, (score / 100) * 100)
            
            # Определяем шанс поступления
            if not meets_req:
                admission_chance = "არ აკმაყოფილებს მოთხოვნებს"
                compatibility = 0
            elif compatibility >= 90:
                admission_chance = "ძალიან მაღალი"
            elif compatibility >= 75:
                admission_chance = "მაღალი"
            elif compatibility >= 60:
                admission_chance = "საშუალო"
            elif compatibility >= 45:
                admission_chance = "დაბალი"
            else:
                admission_chance = "ძალიან დაბალი"
            
            result = {
                'program_code': program['program_code'],
                'program_name': program['program_name'],
                'university_code': program['university_code'],
                'city': program['city'],
                'uni_type': program['uni_type'],
                'tuition': program['annual_tuition'],
                'places': program['total_places'],
                'teaching_language': program['teaching_language'],
                'credits': program['credits'],
                'compatibility': round(compatibility, 1),
                'admission_chance': admission_chance,
                'weighted_score': round(score, 2),
                'meets_requirements': meets_req,
                'message': message,
                'special_note': program.get('special_note', '')
            }
            
            results.append(result)
        
        # Сортируем по совместимости
        results.sort(key=lambda x: x['compatibility'], reverse=True)
        
        return results[:top_n]
    
    def get_available_filters(self) -> Dict:
        """
        Возвращает доступные значения для фильтров
        """
        return {
            'cities': ['ყველა'] + sorted(self.df['city'].unique().tolist()),
            'uni_types': ['ყველა', 'სახელმწიფო', 'კერძო'],
            'categories': ['ყველა'] + sorted(self.df['category'].unique().tolist()),
            'languages': ['ყველა', 'ქართული ენა', 'ინგლისური ენა', 'რუსული ენა']
        }


def main():
    """
    Тестовый запуск системы
    """
    print("=" * 80)
    print("სისტემა იტვირთება...")
    print("=" * 80)
    
    # Инициализация системы
    system = UniversityRecommendationSystem('/mnt/project/programs_database.csv')
    
    # Пример использования
    print("\n" + "=" * 80)
    print("მაგალითი: IT პროგრამების ძიება თბილისში")
    print("=" * 80)
    
    # Фильтруем программы
    filtered = system.filter_programs(
        city='თბილისი',
        category='IT და კომპიუტერული მეცნიერებები'
    )
    
    print(f"\nნაპოვნია {len(filtered)} პროგრამა")
    
    # Получаем необходимые экзамены
    exams = system.get_required_exams(filtered)
    print("\nსავალდებულო საგნები:")
    for exam in exams['mandatory_core']:
        print(f"  - {exam}")
    
    print("\nსაარჩევი საგნები:")
    for exam in list(exams['elective'])[:5]:
        print(f"  - {exam}")
    
    # Пример баллов абитуриента
    example_scores = {
        'ქართული ენა და ლიტერატურა': 75,
        'ინგლისური ენა': 80,
        'მათემატიკა': 85,
        'ფიზიკა': 70
    }
    
    print("\n" + "=" * 80)
    print("რეკომენდაციები (მაგალითი):")
    print("=" * 80)
    
    recommendations = system.recommend_programs(
        city='თბილისი',
        uni_type='ყველა',
        category='IT და კომპიუტერული მეცნიერებები',
        teaching_language='ქართული',
        exam_scores=example_scores,
        foreign_language='ინგლისური ენა',
        top_n=5
    )
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['program_name']}")
        print(f"   თავსებადობა: {rec['compatibility']}%")
        print(f"   ჩაბარების შანსი: {rec['admission_chance']}")
        print(f"   ადგილების რაოდენობა: {rec['places']}")
        if rec['uni_type'] == 'კერძო':
            print(f"   საფასური: {rec['tuition']} GEL")
        else:
            print(f"   უფასო (სახელმწიფო)")


if __name__ == "__main__":
    main()
