from flask import Flask, render_template, redirect, url_for, session, flash, jsonify, request, send_from_directory
from auth import auth_bp
from sat_routes import sat_bp
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')

# Add CSRF token function to template context
@app.context_processor
def inject_csrf_token():
    from secrets import token_urlsafe
    return dict(csrf_token=lambda: token_urlsafe(32))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(sat_bp)

@app.route('/')
def index():
    """Redirect to login if not authenticated, otherwise to dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page for authenticated users"""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('auth.login'))
    
    username = session.get('username', 'User')
    return render_template('dashboard.html', username=username)

@app.route('/dashboard/sat')
def sat_dashboard():
    """Dashboard page for authenticated users"""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('auth.login'))
    
    username = session.get('username', 'User')
    return render_template('SAT/dashboard.html', username=username)

@app.route('/static/images/<filename>')
def serve_image(filename):
    """Serve images from the images folder"""
    return send_from_directory('images', filename)

@app.route('/AP Courses/Physics 1: Algebra Based/dashboard.html')
def physics1_dashboard():
    """Physics 1 Algebra Based course dashboard"""
    if 'user_id' not in session:
        flash('Please log in to access the course.', 'error')
        return redirect(url_for('auth.login'))
    
    username = session.get('username', 'User')
    return render_template('AP Courses/Physics 1: Algebra Based/dashboard.html', username=username)

# SAT Routes
@app.route('/sat/test/<test_date>/<region>/<form>')
def take_test(test_date, region, form):
    """Route to take a specific SAT test"""
    print(f"DEBUG: take_test called with {test_date}, {region}, {form}")
    
    if 'user_id' not in session:
        print(f"DEBUG: No user_id in session - adding debug user")
        session['user_id'] = 'debug_user'  # Temporary bypass for debugging
        session.modified = True
    
    print(f"DEBUG: User authenticated, user_id: {session.get('user_id')}")
    
    # Validate test parameters
    valid_tests = [
        'March 2025 International Form A',
        'March 2025 International Form B', 
        'March 2025 International Form C',
        'March 2025 US Form A',
        'March 2025 US Form B',
        'December 2024 International Form A',
        'December 2024 International Form B',
        'December 2024 International Form C',
        'December 2024 US Form A',
        'December 2024 US Form B',
        'December 2024 US Form C'
    ]
    
    test_name = f"{test_date} {region} {form}"    
    print(f"DEBUG: test_name='{test_name}', valid={test_name in valid_tests}")
    
    if test_name not in valid_tests:
        flash('Invalid test selection.', 'error')
        return redirect('/dashboard/sat')
    
    # Initialize test session
    session['current_test'] = test_name
    session['current_module'] = 1
    session['current_question'] = 1
    session['test_answers'] = {}
    session['test_start_time'] = datetime.utcnow().isoformat()
    session.modified = True
    
    print(f"DEBUG: Session initialized with current_test='{test_name}'")
    
    # Load first question directly
    module = 1
    question = 1
    
    try:
        test_folder = f"sat/{test_name}"
        module_file = f"{test_folder}/module{module}.json"
        
        with open(module_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        if question < 1 or question > len(questions):
            flash('Invalid question number.', 'error')
            return redirect('/dashboard/sat')
        
        current_question_data = questions[question - 1]
        
        # Determine template based on question type and module
        if module <= 2:  # English modules
            template = 'Bluebook/Mock SAT/english_template.html'
            choices = {}
            if 'options' in current_question_data:
                for i, option in enumerate(current_question_data['options']):
                    choices[option['name']] = option['content']
        elif current_question_data.get('type') == 'grid':  # Math FRQ
            template = 'Bluebook/Mock SAT/math_frq_template.html'
            choices = {}
        else:  # Math multiple choice
            template = 'Bluebook/Mock SAT/math_template.html'
            choices = {}
            if 'options' in current_question_data:
                for i, option in enumerate(current_question_data['options']):
                    choices[option['name']] = option['content']
        
        # Parse test name for template variables
        test_parts = test_name.split(' ')
        if len(test_parts) >= 4:
            month = test_parts[0]
            year = test_parts[1]
            region = test_parts[2]
            form = ' '.join(test_parts[3:])
            version = f"{region} {form}"
        else:
            month = "March"
            year = "2025"
            version = "Form A"
        
        # Get all answers and bookmarks
        test_answers = session.get('test_answers', {})
        if 'test_bookmarks' not in session:
            session['test_bookmarks'] = {}
        bookmarks = session.get('test_bookmarks', {})
        
        # Prepare data for JavaScript
        answers_json = json.dumps(test_answers)
        bookmarks_json = json.dumps(bookmarks)
        
        # Get stored answer if any
        answer_key = f"{module}_{question}"
        stored_answer = session.get('test_answers', {}).get(answer_key)
        
        return render_template(template,
                             question=current_question_data.get('question', ''),
                             choices=choices,
                             context=current_question_data.get('article', ''),
                             q_number=question,
                             module=module,
                             total_questions=len(questions),
                             stored_answer=stored_answer,
                             question_doc=[current_question_data],
                             answers=test_answers,
                             bookmarks=bookmarks,
                             answers_json=answers_json,
                             bookmarks_json=bookmarks_json,
                             month=month,
                             year=year,
                             version=version)
        
    except FileNotFoundError as e:
        print(f"DEBUG: FileNotFoundError: {e}")
        flash('Test data not found.', 'error')
        return redirect('/dashboard/sat')
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSONDecodeError: {e}")
        flash('Invalid test data format.', 'error')
        return redirect('/dashboard/sat')
    except Exception as e:
        print(f"DEBUG: Other exception: {type(e).__name__}: {e}")
        flash(f'Error loading test data: {str(e)}', 'error')
        return redirect('/dashboard/sat')

@app.route('/sat/test/question/<int:module>/<int:question>', methods=['GET', 'POST'])
def test_question(module, question):
    """Display a specific question from the current test"""
    if 'user_id' not in session:
        session['user_id'] = 'debug_user'
        session.modified = True
        
    if 'current_test' not in session:
        flash('No test in progress. Please start a test first.', 'error')
        return redirect('/dashboard/sat')
    
    # Handle POST request (answer submission)
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            answer = data.get('answer')
            
            if 'test_answers' not in session:
                session['test_answers'] = {}
            
            answer_key = f"{module}_{question}"
            session['test_answers'][answer_key] = answer
            session.modified = True
            
            return jsonify({'success': True})
        else:
            flash('Invalid request format.', 'error')
            return redirect(url_for('test_question', module=module, question=question))
    
    test_name = session['current_test']
    
    try:
        test_folder = f"sat/{test_name}"
        module_file = f"{test_folder}/module{module}.json"
        
        with open(module_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        if question < 1 or question > len(questions):
            flash('Invalid question number.', 'error')
            return redirect('/dashboard/sat')
        
        current_question_data = questions[question - 1]
        
        # Update session
        session['current_module'] = module
        session['current_question'] = question
        
        # Get stored answer if any
        answer_key = f"{module}_{question}"
        stored_answer = session.get('test_answers', {}).get(answer_key)
        
        # Determine template based on question type and module
        if module <= 2:  # English modules
            template = 'Bluebook/Mock SAT/english_template.html'
            choices = {}
            if 'options' in current_question_data:
                for i, option in enumerate(current_question_data['options']):
                    choices[option['name']] = option['content']
        elif current_question_data.get('type') == 'grid':  # Math FRQ
            template = 'Bluebook/Mock SAT/math_frq_template.html'
            choices = {}
        else:  # Math multiple choice
            template = 'Bluebook/Mock SAT/math_template.html'
            choices = {}
            if 'options' in current_question_data:
                for i, option in enumerate(current_question_data['options']):
                    choices[option['name']] = option['content']
        
        # Parse test name for template variables
        test_parts = test_name.split(' ')
        if len(test_parts) >= 4:
            month = test_parts[0]
            year = test_parts[1]
            region = test_parts[2]
            form = ' '.join(test_parts[3:])
            version = f"{region} {form}"
        else:
            month = "March"
            year = "2025"
            version = "Form A"
        
        # Get all answers and bookmarks
        test_answers = session.get('test_answers', {})
        if 'test_bookmarks' not in session:
            session['test_bookmarks'] = {}
        bookmarks = session.get('test_bookmarks', {})
        
        # Prepare data for JavaScript
        answers_json = json.dumps(test_answers)
        bookmarks_json = json.dumps(bookmarks)
        
        return render_template(template,
                             question=current_question_data.get('question', ''),
                             choices=choices,
                             context=current_question_data.get('article', ''),
                             q_number=question,
                             module=module,
                             total_questions=len(questions),
                             stored_answer=stored_answer,
                             question_doc=[current_question_data],
                             answers=test_answers,
                             bookmarks=bookmarks,
                             answers_json=answers_json,
                             bookmarks_json=bookmarks_json,
                             month=month,
                             year=year,
                             version=version)
        
    except FileNotFoundError:
        flash('Test data not found.', 'error')
        return redirect('/dashboard/sat')
    except Exception as e:
        flash(f'Error loading question: {str(e)}', 'error')
        return redirect('/dashboard/sat')

@app.route('/sat/test/submit_answer', methods=['POST'])
def submit_answer():
    """Submit an answer for the current question"""
    if 'user_id' not in session or 'current_test' not in session:
        return jsonify({'error': 'No test in progress'}), 400
    
    data = request.get_json()
    answer = data.get('answer')
    module = session.get('current_module')
    question = session.get('current_question')
    
    # Store answer in session
    if 'test_answers' not in session:
        session['test_answers'] = {}
    
    answer_key = f"{module}_{question}"
    session['test_answers'][answer_key] = answer
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/sat/test/navigate', methods=['POST'])
def navigate_test():
    """Navigate to next/previous question and return question data"""
    if 'user_id' not in session or 'current_test' not in session:
        return jsonify({'error': 'No test in progress'}), 400
    
    data = request.get_json()
    direction = data.get('direction')  # 'next' or 'prev'
    current_module = session.get('current_module', 1)
    current_question = session.get('current_question', 1)
    
    test_name = session['current_test']
    
    try:
        # Load current module to get question count
        test_folder = f"sat/{test_name}"
        module_file = f"{test_folder}/module{current_module}.json"
        
        with open(module_file, 'r') as f:
            questions = json.load(f)
        
        total_questions = len(questions)
        
        if direction == 'next':
            if current_question < total_questions:
                new_question = current_question + 1
                new_module = current_module
            elif current_module < 4:  # Move to next module
                new_question = 1
                new_module = current_module + 1
            else:
                return jsonify({'error': 'Already at last question'}), 400
        elif direction == 'prev':
            if current_question > 1:
                new_question = current_question - 1
                new_module = current_module
            elif current_module > 1:  # Move to previous module
                # Load previous module to get its question count
                prev_module_file = f"{test_folder}/module{current_module - 1}.json"
                with open(prev_module_file, 'r') as f:
                    prev_questions = json.load(f)
                new_question = len(prev_questions)
                new_module = current_module - 1
            else:
                return jsonify({'error': 'Already at first question'}), 400
        else:
            return jsonify({'error': 'Invalid direction'}), 400
        
        # Load the new question data
        new_module_file = f"{test_folder}/module{new_module}.json"
        with open(new_module_file, 'r') as f:
            new_questions = json.load(f)
        
        if new_question < 1 or new_question > len(new_questions):
            return jsonify({'error': 'Invalid question number'}), 400
        
        current_question_data = new_questions[new_question - 1]
        
        # Update session
        session['current_module'] = new_module
        session['current_question'] = new_question
        session.modified = True
        
        # Get stored answer if any
        answer_key = f"{new_module}_{new_question}"
        stored_answer = session.get('test_answers', {}).get(answer_key)
        
        # Convert options to the format expected by templates
        choices = {}
        if 'options' in current_question_data:
            for option in current_question_data['options']:
                choices[option['name']] = option['content']
        
        # Determine question type
        question_type = 'english' if new_module <= 2 else ('frq' if current_question_data.get('type') == 'grid' else 'math')
        
        return jsonify({
            'success': True,
            'question': current_question_data.get('question', ''),
            'choices': choices,
            'context': current_question_data.get('article', ''),
            'q_number': new_question,
            'module': new_module,
            'total_questions': len(new_questions),
            'stored_answer': stored_answer,
            'question_type': question_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sat/test/question_data/<int:module>/<int:question>')
def get_question_data(module, question):
    """Get question data as JSON for AJAX requests"""
    if 'user_id' not in session or 'current_test' not in session:
        return jsonify({'error': 'No test in progress'}), 400
    
    test_name = session['current_test']
    
    try:
        test_folder = f"sat/{test_name}"
        module_file = f"{test_folder}/module{module}.json"
        
        with open(module_file, 'r') as f:
            questions = json.load(f)
        
        if question < 1 or question > len(questions):
            return jsonify({'error': 'Invalid question number'}), 400
        
        current_question_data = questions[question - 1]
        
        # Get stored answer if any
        answer_key = f"{module}_{question}"
        stored_answer = session.get('test_answers', {}).get(answer_key)
        
        # Get bookmark status
        bookmark_key = f"{module}_{question}"
        is_bookmarked = session.get('test_bookmarks', {}).get(bookmark_key, False)
        
        # Convert options to the format expected by templates
        choices = {}
        if 'options' in current_question_data:
            for option in current_question_data['options']:
                choices[option['name']] = option['content']
        
        # Determine question type
        question_type = 'english' if module <= 2 else ('frq' if current_question_data.get('type') == 'grid' else 'math')
        
        return jsonify({
            'success': True,
            'question': current_question_data.get('question', ''),
            'choices': choices,
            'context': current_question_data.get('article', ''),
            'q_number': question,
            'module': module,
            'total_questions': len(questions),
            'stored_answer': stored_answer,
            'is_bookmarked': is_bookmarked,
            'question_type': question_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/toggle_bookmark', methods=['POST'])
def toggle_bookmark():
    """Toggle bookmark status for a question"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    q_number = data.get('q_number')
    module = data.get('module')
    
    if not q_number or not module:
        return jsonify({'error': 'Missing question number or module'}), 400
    
    # Initialize bookmarks if not exists
    if 'test_bookmarks' not in session:
        session['test_bookmarks'] = {}
    
    bookmark_key = f"{module}_{q_number}"
    current_bookmarks = session['test_bookmarks']
    
    # Toggle bookmark
    if bookmark_key in current_bookmarks and current_bookmarks[bookmark_key]:
        current_bookmarks[bookmark_key] = False
        bookmarked = False
    else:
        current_bookmarks[bookmark_key] = True
        bookmarked = True
    
    session['test_bookmarks'] = current_bookmarks
    session.modified = True
    
    return jsonify({'bookmarked': bookmarked})

if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'), 
        debug=os.getenv('DEBUG', 'False').lower() == 'true', 
        port=int(os.getenv('PORT', 8100))
    )