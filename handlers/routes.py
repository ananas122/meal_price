import uuid
from werkzeug.security import check_password_hash
from flask import Flask, render_template, redirect, request, jsonify, make_response, session, send_from_directory
from flask_restful import Api, Resource
from datetime import datetime
from dateutil.parser import parse
import json
import logging

api = Api()

def configure_routes(app):
    @app.route('/set_cookie')
    def set_cookie():
        session_id = str(uuid.uuid4())
        response = make_response("Setting a cookie")
        response.set_cookie(app.config["SESSION_COOKIE_NAME"], session_id)
        return response



    @app.route('/clearcookie')
    def clear_cookie():
        resp = make_response("Cookie Cleared")
        resp.set_cookie("my_session_cookie", expires=0)
        return resp


    @app.route('/add_ingredient', methods=['POST'])
    def add_ingredient():
        cur = mysql.connection.cursor()
        name = request.json.get('name')
        category = request.json.get('category')
        supplier = request.json.get('supplier')
        unit_cost = request.json.get('unit_cost')
        stock_quantity = request.json.get('stock_quantity')

        cur.execute("INSERT INTO ingredients (name, category, supplier, unit_cost, stock_quantity) VALUES (%s, %s, %s, %s, %s)",
                    (name, category, supplier, unit_cost, stock_quantity))
        mysql.connection.commit()
        cur.close()

        return 'Ingrédient ajouté avec succès', 201


    @app.route('/main_page', methods=['GET', 'POST'])
    def main_page():
        if request.method == 'POST':
            form_name = request.form.get('form_name')

            if form_name == 'signup':
                try:
                    # ... code to handle signup requests ...
                    return 'Utilisateur enregistré avec succès', 201
                except Exception as e:
                    print(f"Erreur lors de l'enregistrement de l'utilisateur : {e}")
                    return 'Erreur lors de l\'enregistrement', 500

            elif form_name == 'login':
                try:
                    # ... code to handle login requests ...
                    return 'Utilisateur connecté avec succès', 200
                except Exception as e:
                    print(f"Erreur lors de la connexion de l'utilisateur : {e}")
                    return 'Erreur lors de la connexion', 500

        return render_template('main_page.html')


    def get_recipe_from_db(recipe_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM recettes WHERE id=%s", [recipe_id])
        recipe = cur.fetchone()
        cur.close()
        return recipe


    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')


    @app.route('/index1')
    def index1():
        return render_template('index1.html')


    @app.route('/')
    def index():
        return send_from_directory('.', 'index.html')

    @app.route('/recettes')
    def recettes():
        return render_template('recettes.html')


    @app.route('/calendar')
    def calendar():
        return render_template('calendar.html')


    @app.route('/stocks')
    def stocks():
        return render_template('stocks.html')


    @app.route('/ingredients')
    def ingredients():
        return render_template('ingredients.html')


    @app.route('/edit_ingredient', methods=['POST'])
    def edit_ingredient():
        ingredient_id = request.form.get('ingredient_id')
        return redirect('/ingredients')


    @app.route('/set_selected_recipe', methods=['POST'])
    def set_selected_recipe():
        selected_recipe = request.get_json()

        if selected_recipe is None:
            return jsonify({'message': 'Invalid JSON'}), 400

        session['selected_recipe'] = json.dumps(selected_recipe, ensure_ascii=False)
        return jsonify({'message': 'Recipe details stored in session'})


    @app.route("/calculator", methods=["GET", "POST"])
    def calculator():
        recipe = {
            "name": "",
            "ingredients": [],
            "instructions": "",
            "quantity_used": ""
        }

        if 'selected_recipe' in session:
            recipe_json_string = session.get('selected_recipe')
            recipe_data = json.loads(recipe_json_string)
            recipe['name'] = recipe_data.get('name')
            recipe['ingredients'] = recipe_data.get('ingredients', [])
            recipe['instructions'] = recipe_data.get('instructions', "")
            recipe['quantity_used'] = recipe_data.get('quantity_used', "")

        return render_template("calculator.html", recipe=recipe)


    @app.route('/get_recipe/<int:recipe_id>', methods=['GET'])
    def get_recipe(recipe_id):
        recipe_data = {
            'recipe_id': recipe_id,
            'recipe_name': 'Nom de la recette',
            'ingredients': ['Ingrédient 1', 'Ingrédient 2', 'Ingrédient 3'],
        }
        return jsonify(recipe_data)


    @app.route('/api/recipe_details/<int:recipe_id>', methods=['GET'])
    def get_recipe_details(recipe_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM recettes WHERE id=%s", [recipe_id])
        recipe = cur.fetchone()
        cur.close()

        return jsonify(recipe)


    @app.route('/select_recipe', methods=['POST'])
    def select_recipe():
        data = request.json

        session['selectedRecipe'] = {
            'name': data['name'],
            'ingredients': data['ingredients'],
            'instructions': data['instructions']
        }

        return jsonify(success=True)


    events = []


    class Event(Resource):
        def get(self, event_id):
            event = next((event for event in events if event['id'] == event_id), None)
            return (event, 200) if event else ("Événement non trouvé", 404)

        def post(self):
            new_event = request.get_json()
            events.append(new_event)
            return new_event, 201


    api.add_resource(Event, "/event", "/event/<string:event_id>")


    @app.route('/get_events', methods=['GET'])
    def get_events():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM events")
        db_events = cur.fetchall()
        cur.close()

        return jsonify(db_events), 200


    @app.route('/save_event', methods=['POST'])
    def save_event():
        cur = mysql.connection.cursor()
        event_data = request.json
        title = event_data.get('title')
        start_datetime = event_data.get('start_datetime')
        print(f"Title: {title}, Start Time: {start_datetime}")

        try:
            datetime_obj = parse(start_datetime)
        except Exception as e:
            print(f"Erreur lors de la conversion de la date: {e}")
            return 'Format de date invalide', 400

        mysql_format = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

        try:
            cur.execute("INSERT INTO events (title, start_datetime) VALUES (%s, %s)",
                        (title, mysql_format))
            mysql.connection.commit()
        except Exception as e:
            print(f"Erreur lors de l'insertion dans la base de données: {e}")
            return "Erreur lors de la sauvegarde de l'événement", 500

        cur.close()

        return 'Événement sauvegardé', 201