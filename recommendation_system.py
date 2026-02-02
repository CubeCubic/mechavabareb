import pandas as pd
import numpy as np

class UniversityRecommendationSystem:
    def __init__(self, database_path='programs_database.csv'):
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

    def calculate_score(self, program_row, user_scores):
        total = 0
        failed = False
        details = []

        # Обязательные экзамены
        mandatory = program_row['mandatory_exams'].split(';') if pd.notna(program_row['mandatory_exams']) else []
        for m in mandatory:
            if not m.strip(): continue
            parts = m.split(':')
            if len(parts) < 3: continue
            subject, coef, min_perc = parts[0], int(parts[1]), float(parts[2].replace('%',''))
            min_score = (min_perc / 100) * self.max_scores.get(subject, 100)
            user = user_scores.get(subject, 0)
            if user < min_score:
                failed = True
            else:
                total += user * coef
                details.append(f"{subject}: {user} × {coef} = {user*coef}")

        # Выборочные (берём лучший)
        elective = program_row['elective_exams'].split(';') if pd.notna(program_row['elective_exams']) else []
        best_elective = 0
        for e in elective:
            if not e.strip(): continue
            parts = e.split(':')
            if len(parts) < 3: continue
            subject, coef, min_perc = parts[0], int(parts[1]), float(parts[2].replace('%',''))
            min_score = (min_perc / 100) * self.max_scores.get(subject, 100)
            user = user_scores.get(subject, 0)
            if user >= min_score:
                score = user * coef
                if score > best_elective:
                    best_elective = score

        total += best_elective

        chance = "არ აკმაყოფილებს მინიმუმს" if failed else \
                 "ძალიან მაღალი" if total > 800 else \
                 "მაღალი" if total > 600 else \
                 "საშუალო" if total > 400 else "დაბალი"

        return {
            'total_score': total,
            'chance': chance,
            'details': details,
            'places': program_row['total_places']
        }

    def recommend(self, user_scores):
        results = []
        for _, row in self.df.iterrows():
            score_data = self.calculate_score(row, user_scores)
            results.append({
                'program': row['program_name'],
                'uni_code': row['university_code'],
                'places': score_data['places'],
                'score': score_data['total_score'],
                'chance': score_data['chance']
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:10]
