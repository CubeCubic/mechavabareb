import pandas as pd
import numpy as np
import re

class UniversityRecommendationSystem:
    def __init__(self, database_path: str):
        self.df = pd.read_csv(database_path)
        self.max_scores = {
            'ქართული ენა და ლიტერატურა': 60,
            'მათემატიკა': 51,
            'უცხოური ენა': 70,
            'ისტორია': 60,
            'ბიოლოგია': 70,
            'გეოგრაფია': 59,
            'ფიზიკა': 63,
            'ქიმია': 63,
            'ზოგადი უნარები': 80,
            'ლიტერატურა': 70,
            'სამოქალაქო განათლება': 60,
            'სახვითი და გამოყენებითი ხელოვნება': 70
        }

    def parse_exams(self, exams_str):
        if pd.isna(exams_str):
            return []
        exams = []
        lines = re.split(r';| \d ', exams_str)  # Разделяем по ; или цифрам
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Ищем предмет:coef:min:pri:places
            match = re.search(r'(\w+.+?) (\d) (\d+%-ზე მეტი) (\d) (\d*)', line)
            if match:
                subject = match.group(1).strip()
                coef = int(match.group(2))
                min_str = match.group(3).replace('%-ზე მეტი', '')
                min_perc = float(min_str)
                pri = int(match.group(4))
                places = int(match.group(5)) if match.group(5) else 0
                exams.append({
                    'subject': subject,
                    'coef': coef,
                    'min_perc': min_perc,
                    'pri': pri,
                    'places': places
                })
        return exams

    def calculate_score(self, row, user_scores):
        mandatory = self.parse_exams(row['mandatory_exams'])
        elective = self.parse_exams(row['elective_exams'])
        
        total = 0
        failed = []
        used = []
        max_possible = 0
        
        # Обязательные
        for m in mandatory:
            subj = m['subject']
            user = user_scores.get(subj, 0)
            max_s = self.max_scores.get(subj, 100)
            min_s = (m['min_perc'] / 100) * max_s
            max_possible += max_s * m['coef']
            if user < min_s:
                failed.append(subj)
            else:
                contrib = user * m['coef']
                total += contrib
                used.append(f"{subj}: {user} × {m['coef']} = {contrib}")
        
        # Выборочные — лучший
        best_elec = 0
        for e in elective:
            subj = e['subject']
            user = user_scores.get(subj, 0)
            max_s = self.max_scores.get(subj, 100)
            min_s = (e['min_perc'] / 100) * max_s
            if user >= min_s:
                contrib = user * e['coef']
                if contrib > best_elec:
                    best_elec = contrib
        
        total += best_elec
        max_possible += max([e['coef'] * self.max_scores.get(e['subject'], 100) for e in elective]) if elective else 0
        
        compatibility = (total / max_possible * 100) if max_possible > 0 else 0
        
        chance = "არ აკმაყოფილებს მინიმუმს" if failed else \
                 "ძალიან მაღალი" if compatibility >= 90 else \
                 "მაღალი" if compatibility >= 70 else \
                 "საშუალო" if compatibility >= 50 else "დაბალი"
        
        return {
            'compatibility': round(compatibility, 1),
            'chance': chance,
            'total': round(total, 2),
            'failed': failed,
            'used': used
        }

    def recommend_programs(self, exam_scores, top_n=20):
        results = []
        for _, row in self.df.iterrows():
            score_data = self.calculate_score(row, exam_scores)
            if score_data['chance'] != 'არ აკმაყოფილებს მინიმუმს':
                results.append({
                    'program_name': row['program_name'],
                    'university_code': row['university_code'],
                    'compatibility': score_data['compatibility'],
                    'admission_chance': score_data['chance']
                })
        
        results.sort(key=lambda x: x['compatibility'], reverse=True)
        
        return results[:top_n]