import pandas as pd
import numpy as np
from typing import Dict, List
import re

class UniversityRecommendationSystem:
    def __init__(self, database_path: str):
        self.df = pd.read_csv(database_path)
        self.prepare_data()
    
    def prepare_data(self):
        # Тип вуза (государственный = 2250 GEL, но это условно)
        self.df['uni_type'] = np.where(self.df['annual_tuition'] == 2250.0, 'სახელმწიფო', 'კერძო')
        self.df['program_name_clean'] = self.df['program_name'].str.strip()
        self.df['category'] = self.df.apply(self._categorize_program, axis=1)
        self.df['city'] = self.df['university_code'].apply(self._get_city)
        
        # Очистка колонок экзаменов
        exam_columns = [col for col in self.df.columns if 'exam' in col.lower()]
        for col in exam_columns:
            self.df[col] = self.df[col].astype(str).str.replace(r'\(.*\)', '', regex=True).str.strip()
        
        min_columns = [col for col in self.df.columns if 'min' in col.lower()]
        for col in min_columns:
            self.df[col] = self.df[col].astype(str).str.extract(r'(\d+)', expand=False).astype(float)
    
    def _categorize_program(self, row) -> str:
        name = str(row['program_name']).lower()
        uni_code = row['university_code']
        
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
        city_map = {
            1: 'თბილისი', 2: 'თბილისი', 3: 'თბილისი', 4: 'თბილისი',
            5: 'თბილისი', 6: 'თბილისი', 9: 'ქუთაისი', 10: 'თბილისი',
            12: 'თბილისი', 14: 'ახალციხე', 19: 'ქუთაისი', 33: 'თბილისი',
            36: 'თბილისი', 40: 'თბილისი', 52: 'თბილისი', 53: 'ბათუმი',
            64: 'თბილისი', 71: 'თელავი', 85: 'თბილისი', 88: 'თბილისი',
            97: 'ზუგდიდი', 98: 'თბილისი', 114: 'ბათუმი', 115: 'თბილისი',
            # Добавь остальные по своему файлу umaglesebi.xlsx
        }
        return city_map.get(uni_code, 'უცნობი')
    
    def filter_programs(self, city: str = None, uni_type: str = None, category: str = None, teaching_language: str = None) -> pd.DataFrame:
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
        mandatory_core = set()
        elective = set()
        
        for _, program in programs.iterrows():
            for i in range(1, 5):
                exam = program.get(f'mandatory_exam_{i}_name')
                if pd.notna(exam) and exam.strip():
                    mandatory_core.add(exam.strip())
            
            for i in range(1, 7):
                exam = program.get(f'elective_exam_{i}_name')
                if pd.notna(exam) and exam.strip():
                    elective.add(exam.strip())
        
        mandatory_core.add('ქართული ენა და ლიტერატურა')
        mandatory_core.add('უცხოური ენა')
        
        return {
            'mandatory_core': list(mandatory_core),
            'elective': list(elective)
        }
    
    def calculate_score(self, program: pd.Series, exam_scores: Dict[str, float]) -> Dict:
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
        
        # Обязательные экзамены
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
            
            scaled_score = raw_score * 2.0  # Max raw 100 → scaled 200
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
        
        # Выборочные — лучший
        for i in range(1, 7):
            exam_name = program.get(f'elective_exam_{i}_name')
            if pd.isna(exam_name) or not exam_name.strip():
                continue
            
            coefficient = program.get(f'elective_exam_{i}_coef', 1.0)
            min_score = program.get(f'elective_exam_{i}_min', 0.0)
            
            raw_score = exam_scores.get(exam_name.strip(), 0.0)
            if raw_score < min_score:
                continue
            
            scaled_score = raw_score * 2.0
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
        
        # Процент совместимости
        if total_coefficients > 0:
            max_possible = 200.0 * total_coefficients
            compatibility = (competitive_score / max_possible) * 100.0
        else:
            compatibility = 0.0
        
        # Шанс поступления
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
        filtered = self.filter_programs(city, uni_type, category, teaching_language)
        
        if len(filtered) == 0:
            return []
        
        results = []
        
        for idx, program in filtered.iterrows():
            score_data = self.calculate_score(program, exam_scores)
            
            tuition = 0.0 if program['uni_type'] == 'სახელმწიფო' else program.get('annual_tuition', 0)
            
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
        
        results.sort(key=lambda x: x['compatibility'], reverse=True)
        
        return results[:top_n]
        
