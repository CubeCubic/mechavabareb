import pandas as pd

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

    def parse_exams(self, exams_str):
        if pd.isna(exams_str):
            return []
        items = []
        for part in exams_str.split(';'):
            part = part.strip()
            if not part: continue
            subparts = part.split(':')
            if len(subparts) >= 3:
                subject = subparts[0].strip()
                coef = int(subparts[1])
                min_perc = float(subparts[2].replace('%','').replace('-','').strip())
                items.append({'subject': subject, 'coef': coef, 'min_perc': min_perc})
        return items

    def calculate_score(self, row, user_scores):
        total = 0
        failed = []
        used = []

        # Обязательные
        mandatory = self.parse_exams(row['mandatory_exams'])
        for m in mandatory:
            subj = m['subject']
            user = user_scores.get(subj, 0)
            max_s = self.max_scores.get(subj, 100)
            min_s = (m['min_perc'] / 100) * max_s
            if user < min_s:
                failed.append(subj)
            else:
                total += user * m['coef']
                used.append(f"{subj}: {user} × {m['coef']} = {user * m['coef']}")

        # Выборочные — берём лучший
        elective = self.parse_exams(row['elective_exams'])
        best_elec = 0
        best_subj = ''
        for e in elective:
            subj = e['subject']
            user = user_scores.get(subj, 0)
            max_s = self.max_scores.get(subj, 100)
            min_s = (e['min_perc'] / 100) * max_s
            if user >= min_s:
                score = user * e['coef']
                if score > best_elec:
                    best_elec = score
                    best_subj = subj

        if best_elec > 0:
            total += best_elec
            used.append(f"{best_subj} (არჩევითი): {user_scores.get(best_subj,0)} × {e['coef']} = {best_elec}")

        max_possible = 0
        for m in mandatory:
            max_possible += self.max_scores.get(m['subject'], 100) * m['coef']
        if elective:
            max_possible += max([self.max_scores.get(e['subject'], 100) * e['coef'] for e in elective])

        compatibility = (total / max_possible * 100) if max_possible > 0 else 0

        chance = "არ აკმაყოფილებს მინიმუმს" if failed else \
                 f"ძალიან მაღალი ({compatibility:.1f}%)" if compatibility >= 85 else \
                 f"მაღალი ({compatibility:.1f}%)" if compatibility >= 70 else \
                 f"საშუალო ({compatibility:.1f}%)" if compatibility >= 50 else \
                 f"დაბალი ({compatibility:.1f}%)"

        return {
            'total': round(total),
            'compatibility': round(compatibility, 1),
            'chance': chance,
            'failed': failed,
            'used': used,
            'places': row['total_places']
        }

    def recommend(self, user_scores):
        results = []
        for _, row in self.df.iterrows():
            score_data = self.calculate_score(row, user_scores)
            results.append({
                'program': row['program_name'],
                'qualification': row['qualification'],
                'uni_code': row['university_code'],
                'places': score_data['places'],
                'total': score_data['total'],
                'compatibility': score_data['compatibility'],
                'chance': score_data['chance']
            })
        results.sort(key=lambda x: x['compatibility'], reverse=True)
        return results[:10]