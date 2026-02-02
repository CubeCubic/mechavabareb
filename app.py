from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Загружаем базу
df = pd.read_csv('programs_database.csv')

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    if request.method == 'POST':
        georgian = int(request.form.get('georgian', 0))
        foreign_lang = request.form.get('foreign_lang')
        foreign_score = int(request.form.get('foreign_score', 0)) if foreign_lang else 0
        math = int(request.form.get('math', 0))
        
        for _, row in df.iterrows():
            # Простой пример расчёта (замени на реальный позже)
            total = georgian * 5 + foreign_score * 4 + math * 3
            chance = "ძალიან მაღალი" if total > 500 else "მაღალი" if total > 400 else "საშუალო"
            
            results.append({
                'program': row['program_name'],
                'qualification': row['qualification'],
                'uni_code': row['university_code'],
                'total': total,
                'chance': chance
            })
        
        results = sorted(results, key=lambda x: x['total'], reverse=True)[:10]

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
