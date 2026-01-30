"""
Flask веб-приложение для системы рекомендаций университетов
Интерфейс на грузинском языке
"""

from flask import Flask, render_template, request, jsonify
from recommendation_system import UniversityRecommendationSystem
import os

app = Flask(__name__)

# Инициализируем систему рекомендаций
DB_PATH = os.environ.get('DATABASE_PATH', 'programs_database.csv')
if not os.path.exists(DB_PATH):
    raise FileNotFoundError("ბაზა მონაცემები programs_database.csv არ მოიძებნა!")

system = UniversityRecommendationSystem(DB_PATH)

# Константы для интерфейса
CITIES = {
    'ყველა': 'ყველა ქალაქი',
    'თბილისი': 'თბილისი',
    'ბათუმი': 'ბათუმი',
    'ქუთაისი': 'ქუთაისი',
    'გორი': 'გორი',
    'ახალციხე': 'ახალციხე',
    'თელავი': 'თელავი',
    'ზუგდიდი': 'ზუგდიდი',
    'სოფ. ხიჭაური': 'სოფ. ხიჭაური',
    'სოფ. გრემი': 'სოფ. გრემი'
}

UNI_TYPES = {
    'ყველა': 'ყველა ტიპი',
    'სახელმწიფო': 'სახელმწიფო (უფასო)',
    'კერძო': 'კერძო (ფასიანი)'
}

CATEGORIES = {
    'ყველა': 'ყველა მიმართულება',
    'საღვთისმეტყველო': 'საღვთისმეტყველო',
    'მედიცინა და ფარმაცია': 'მედიცინა და ფარმაცია',
    'IT და კომპიუტერული მეცნიერებები': 'IT და კომპიუტერული მეცნიერებები',
    'ბიზნესი და ეკონომიკა': 'ბიზნესი და ეკონომიკა',
    'სამართალი': 'სამართალი',
    'ხელოვნება და დიზაინი': 'ხელოვნება და დიზაინი',
    'მუსიკა და თეატრი': 'მუსიკა და თეატრი',
    'ინჟინერია': 'ინჟინერია',
    'ენები და ფილოლოგია': 'ენები და ფილოლოგია',
    'საბუნებისმეტყველო მეცნიერებები': 'საბუნებისმეტყველო მეცნიერებები',
    'სოციალური მეცნიერებები': 'სოციალური მეცნიერებები',
    'სასოფლო-სამეურნეო': 'სასოფლო-სამეურნეო',
    'განათლება': 'განათლება',
    'სხვა': 'სხვა'
}

LANGUAGES = {
    'ყველა': 'ყველა ენა',
    'ქართული': 'ქართული ენა',
    'ინგლისური': 'ინგლისური ენა',
    'რუსული': 'რუსული ენა'
}

FOREIGN_LANGUAGES = {
    'ინგლისური ენა': 'ინგლისური (English)',
    'გერმანული ენა': 'გერმანული (Deutsch)',
    'ფრანგული ენა': 'ფრანგული (Français)',
    'რუსული ენა': 'რუსული (Русский)'
}

# Список всех возможных экзаменов
ALL_EXAMS = [
    'ქართული ენა და ლიტერატურა',
    'მათემატიკა',
    'ფიზიკა',
    'ქიმია',
    'ბიოლოგია',
    'ისტორია',
    'გეოგრაფია',
    'ლიტერატურა',
    'სამოქალაქო განათლება',
    'ხელოვნება'
]


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html',
                           cities=CITIES,
                           uni_types=UNI_TYPES,
                           categories=CATEGORIES,
                           languages=LANGUAGES,
                           foreign_languages=FOREIGN_LANGUAGES,
                           all_exams=ALL_EXAMS)


@app.route('/get_required_exams', methods=['POST'])
def get_required_exams():
    """
    API endpoint для получения списка необходимых экзаменов
    на основе выбранных фильтров
    """
    data = request.json
    
    city = data.get('city', 'ყველა')
    uni_type = data.get('uni_type', 'ყველა')
    category = data.get('category', 'ყველა')
    teaching_language = data.get('teaching_language', 'ყველა')
    
    # Фильтруем программы
    filtered = system.filter_programs(
        city=city if city != 'ყველა' else None,
        uni_type=uni_type if uni_type != 'ყველა' else None,
        category=category if category != 'ყველა' else None,
        teaching_language=teaching_language if teaching_language != 'ყველა' else None
    )
    
    if len(filtered) == 0:
        return jsonify({
            'success': False,
            'message': 'არცერთი პროგრამა არ მოიძებნა შერჩეული ფილტრებით'
        })
    
    # Получаем необходимые экзамены
    exams = system.get_required_exams(filtered)
    
    # Фильтруем выборочные экзамены (исключаем мусорные данные)
    elective_clean = [exam for exam in exams['elective'] if exam and not exam.replace('%', '').replace('-', '').replace('ზე', '').replace('მეტი', '').strip().isdigit() and exam not in ['25%', '30%', '40%', '50%']]
    
    return jsonify({
        'success': True,
        'programs_found': len(filtered),
        'mandatory_exams': list(exams['mandatory_core']),
        'elective_exams': elective_clean[:15]  # Ограничиваем количество
    })


@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """
    API endpoint для получения рекомендаций программ
    """
    data = request.json
    
    # Получаем параметры фильтров
    city = data.get('city', 'ყველა')
    uni_type = data.get('uni_type', 'ყველა')
    category = data.get('category', 'ყველა')
    teaching_language = data.get('teaching_language', 'ყველა')
    foreign_language = data.get('foreign_language')
    
    # Получаем баллы по экзаменам
    exam_scores_raw = data.get('exam_scores', {})
    
    # Проверка обязательных экзаменов
    if 'ქართული ენა და ლიტერატურა' not in exam_scores_raw:
        return jsonify({
            'success': False,
            'message': 'გთხოვთ შეიყვანოთ ქულა ქართულ ენაში'
        })
    
    if not foreign_language or foreign_language not in exam_scores_raw:
        return jsonify({
            'success': False,
            'message': 'გთხოვთ აირჩიოთ უცხოური ენა და შეიყვანოთ ქულა'
        })
    
    # Проверка на минимум один дополнительный предмет
    other_exams = {k: v for k, v in exam_scores_raw.items() 
                   if k not in ['ქართული ენა და ლიტერატურა', foreign_language]}
    
    if len(other_exams) == 0:
        return jsonify({
            'success': False,
            'message': 'გთხოვთ აირჩიოთ მინიმუმ ერთი დამატებითი საგანი'
        })
    
    # Подготавливаем баллы: заменяем конкретный иностранный на "უცხოური ენა"
    exam_scores = exam_scores_raw.copy()
    if foreign_language:
        foreign_score = exam_scores.pop(foreign_language, 0)
        exam_scores['უცხოური ენა'] = foreign_score
        exam_scores['უცხოური ენა (ინგ.)'] = foreign_score
        exam_scores['უცხოური ენა (გერ.; ინგ.; რუს.; ფრან.)'] = foreign_score
        exam_scores['უცხოური ენა (ინგ.; რუს.; გერ.; ფრან.)'] = foreign_score
        exam_scores['უცხოური ენა (გერ.)'] = foreign_score
        exam_scores['უცხოური ენა (რუს.)'] = foreign_score
        exam_scores['უცხოური ენა (ფრან.)'] = foreign_score
    
    # Получаем рекомендации
    recommendations = system.recommend_programs(
        city=city if city != 'ყველა' else None,
        uni_type=uni_type if uni_type != 'ყველა' else None,
        category=category if category != 'ყველა' else None,
        teaching_language=teaching_language if teaching_language != 'ყველა' else None,
        exam_scores=exam_scores,
        top_n=20
    )
    
    if len(recommendations) == 0:
        return jsonify({
            'success': False,
            'message': 'არცერთი შესაბამისი პროგრამა არ მოიძებნა'
        })
    
    return jsonify({
        'success': True,
        'recommendations': recommendations,
        'total_found': len(recommendations)
    })


if __name__ == '__main__':
    # Запуск в режиме разработки
    app.run(debug=True, host='0.0.0.0', port=5000)
