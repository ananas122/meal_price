import { v4 as uuidv4 } from 'uuid';
import { check_password_hash } from 'werkzeug.security';
import express from 'express';
import { render_template, redirect, request, jsonify, make_response, session, send_from_directory } from 'express';
import { Api, Resource } from 'express-restful';
import { DateTime } from 'luxon';
import { parse } from 'date-fns';
import { json } from 'express';
import { createLogger, format, transports } from 'winston';

const app = express();
const api = new Api();

function configure_routes(app) {
    app.get('/set_cookie', (req, res) => {
        const session_id = uuidv4();
        res.cookie(app.config["SESSION_COOKIE_NAME"], session_id.toString());
        res.send("Setting a cookie");
    });

    app.get('/clearcookie', (req, res) => {
        res.clearCookie("my_session_cookie");
        res.send("Cookie Cleared");
    });

    app.post('/add_ingredient', (req, res) => {
        const name = req.body.name;
        const category = req.body.category;
        const supplier = req.body.supplier;
        const unit_cost = req.body.unit_cost;
        const stock_quantity = req.body.stock_quantity;

        // Insert into ingredients table
        res.send('Ingrédient ajouté avec succès');
    });

    app.all('/main_page', (req, res) => {
        if (req.method === 'POST') {
            const form_name = req.body.form_name;
            if (form_name === 'signup') {
                try {
                    res.send('Utilisateur enregistré avec succès');
                } catch (e) {
                    console.log(`Erreur lors de l'enregistrement de l'utilisateur : ${e}`);
                    res.status(500).send('Erreur lors de l\'enregistrement');
                }
            } else if (form_name === 'login') {
                try {
                    res.send('Utilisateur connecté avec succès');
                } catch (e) {
                    console.log(`Erreur lors de la connexion de l'utilisateur : ${e}`);
                    res.status(500).send('Erreur lors de la connexion');
                }
            }
        } else {
            res.render('main_page.html');
        }
    });

    function get_recipe_from_db(recipe_id) {
        // Fetch recipe from database
        return recipe;
    }

    app.get('/dashboard', (req, res) => {
        res.render('dashboard.html');
    });

    app.get('/index1', (req, res) => {
        res.render('index1.html');
    });

    app.get('/', (req, res) => {
        res.sendFile('index.html', { root: '.' });
    });

    app.get('/recettes', (req, res) => {
        res.render('recettes.html');
    });

    app.get('/calendar', (req, res) => {
        res.render('calendar.html');
    });

    app.get('/stocks', (req, res) => {
        res.render('stocks.html');
    });

    app.get('/ingredients', (req, res) => {
        res.render('ingredients.html');
    });

    app.post('/edit_ingredient', (req, res) => {
        const ingredient_id = req.body.ingredient_id;
        res.redirect('/ingredients');
    });

    app.post('/set_selected_recipe', (req, res) => {
        const selected_recipe = req.body;
        if (!selected_recipe) {
            res.status(400).json({ message: 'Invalid JSON' });
        } else {
            session.selected_recipe = JSON.stringify(selected_recipe);
            res.json({ message: 'Recipe details stored in session' });
        }
    });

    app.all('/calculator', (req, res) => {
        const recipe = {
            name: "",
            ingredients: [],
            instructions: "",
            quantity_used: ""
        };

        if (session.selected_recipe) {
            const recipe_json_string = session.selected_recipe;
            const recipe_data = JSON.parse(recipe_json_string);
            recipe.name = recipe_data.name;
            recipe.ingredients = recipe_data.ingredients || [];
            recipe.instructions = recipe_data.instructions || "";
            recipe.quantity_used = recipe_data.quantity_used || "";
        }

        res.render("calculator.html", { recipe });
    });

    app.get('/get_recipe/:recipe_id', (req, res) => {
        const recipe_id = req.params.recipe_id;
        const recipe_data = {
            recipe_id: recipe_id,
            recipe_name: 'Nom de la recette',
            ingredients: ['Ingrédient 1', 'Ingrédient 2', 'Ingrédient 3']
        };
        res.json(recipe_data);
    });

    app.get('/api/recipe_details/:recipe_id', (req, res) => {
        const recipe_id = req.params.recipe_id;
        // Fetch recipe details from database
        res.json(recipe);
    });

    app.post('/select_recipe', (req, res) => {
        const data = req.body;
        session.selectedRecipe = {
            name: data.name,
            ingredients: data.ingredients,
            instructions: data.instructions
        };
        res.json({ success: true });
    });

    const events = [];

    class Event extends Resource {
        get(event_id) {
            const event = events.find(event => event.id === event_id);
            if (event) {
                return event;
            } else {
                return "Événement non trouvé";
            }
        }

        post() {
            const new_event = req.body;
            events.push(new_event);
            return new_event;
        }
    }

    api.addResource(Event, "/event", "/event/:event_id");

    app.get('/get_events', (req, res) => {
        // Fetch events from database
        res.json(db_events);
    });

    app.post('/save_event', (req, res) => {
        const event_data = req.body;
        const title = event_data.title;
        const start_datetime = event_data.start_datetime;

        try {
            const datetime_obj = parse(start_datetime);
        } catch (e) {
            console.log(`Erreur lors de la conversion de la date: ${e}`);
            res.status(400).send('Format de date invalide');
        }

        const mysql_format = datetime_obj.toFormat('yyyy-MM-dd HH:mm:ss');

        try {
            // Insert event into database
            res.send('Événement sauvegardé');
        } catch (e) {
            console.log(`Erreur lors de l'insertion dans la base de données: ${e}`);
            res.status(500).send("Erreur lors de la sauvegarde de l'événement");
        }
    });

    api.init(app);
}

configure_routes(app);


