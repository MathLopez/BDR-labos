from flask import Flask, render_template, jsonify, request, make_response, redirect, flash,session,url_for
from datetime import date, timedelta

import psycopg2
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
# Configuration de la base de données
DB_CONFIG = {
    "dbname": "ecommerce",
    "user": "admin",
    "password": "admin123",
    "host": "localhost",
    "port": "5432",
}

# Connexion à la base de données
def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        raise


@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer les 5 boutiques
    cursor.execute("SELECT pkBoutique, nom FROM Boutique LIMIT 5")
    boutiques = cursor.fetchall()

    # Récupérer les 5 articles les plus achetés d'hier
    yesterday = date.today() - timedelta(days=1)
    cursor.execute("""
        SELECT p.pkProduit, p.nom, p.prix
        FROM Produit p
        JOIN Contient c ON p.pkProduit = c.fkArticleProduit
        JOIN Commande cmd ON cmd.pkCommande = c.fkCommande
        WHERE cmd.date::date = %s
        GROUP BY p.pkProduit
        ORDER BY SUM(c.quantité) DESC
        LIMIT 5
    """, (yesterday,))
    articles = cursor.fetchall()

    # Si pas d'articles populaires, récupérer des articles aléatoires
    if not articles:
        cursor.execute("SELECT pkProduit, nom, prix FROM Produit ORDER BY RANDOM() LIMIT 5")
        articles = cursor.fetchall()

    conn.close()
    return render_template('home.html', boutiques=boutiques, articles=articles)

@app.route('/boutiques')
def boutiques():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pkBoutique, nom FROM Boutique")
    boutiques = cursor.fetchall()
    conn.close()
    return render_template('boutiques.html', boutiques=boutiques)

@app.route('/articles', methods=['GET'])
def articles():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer toutes les catégories disponibles
    cursor.execute("SELECT nom FROM Categorie")
    categories = [row[0] for row in cursor.fetchall()]  # Liste des catégories disponibles

    # Récupérer les articles en fonction de la catégorie sélectionnée
    category = request.args.get('category')  # Paramètre GET "category" depuis l'URL
    if category:
        cursor.execute("""
            SELECT p.pkProduit, p.nom, p.prix
            FROM Produit p
            JOIN Categorie c ON p.fkCategorie = c.pkCategorie
            WHERE c.nom = %s
        """, (category,))
    else:
        cursor.execute("SELECT pkProduit, nom, prix FROM Produit")

    articles = cursor.fetchall()
    conn.close()
    
    # Rendre le template en passant à la fois les articles et les catégories
    return render_template('articles.html', articles=articles, categories=categories, selected_category=category)

@app.route('/article/<int:product_id>', methods=['GET'])
def product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer les détails du produit
    cursor.execute("""
        SELECT p.pkProduit, p.nom, p.description, p.prix, c.nom AS category_name
        FROM Produit p
        JOIN Categorie c ON p.fkCategorie = c.pkCategorie
        WHERE p.pkProduit = %s
    """, (product_id,))
    product = cursor.fetchone()

    # Récupérer les tailles disponibles
    cursor.execute("""
        SELECT taille, quantiteDisponible
        FROM Article
        WHERE pkProduit = %s
    """, (product_id,))
    sizes = cursor.fetchall()

    conn.close()
    return render_template('product.html', product=product, sizes=sizes, product_category=product[4])

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    size = request.form['size']
    quantity = int(request.form['quantity'])

    # Lire le panier actuel dans les cookies
    cart = request.cookies.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = []

    # Ajouter l'article au panier (vérifier si le produit et la taille existent déjà)
    for item in cart:
        if item['product_id'] == product_id and item['size'] == size:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'size': size, 'quantity': quantity})

    # Sauvegarder le panier mis à jour dans les cookies
    response = make_response(redirect('/cart'))
    response.set_cookie('cart', json.dumps(cart), max_age=30*24*60*60)  # 30 jours
    return response

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form['product_id']
    size = request.form['size']

    # Lire le panier actuel dans les cookies
    cart = request.cookies.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = []

    # Supprimer l'article correspondant
    cart = [item for item in cart if not (item['product_id'] == product_id and item['size'] == size)]

    # Sauvegarder le panier mis à jour dans les cookies
    response = make_response(redirect('/cart'))
    response.set_cookie('cart', json.dumps(cart), max_age=30*24*60*60)  # 30 jours
    return response


@app.route('/cart', methods=['GET'])
def cart():
    cart = request.cookies.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = []

    # Récupérer les détails des produits à partir de l'ID des produits
    conn = get_db_connection()
    cursor = conn.cursor()
    product_details = []

    for item in cart:
        cursor.execute("""
            SELECT pkProduit, nom, prix FROM Produit WHERE pkProduit = %s
        """, (item['product_id'],))
        product = cursor.fetchone()
        if product:
            product_details.append({
                "product_id": product[0],
                "name": product[1],
                "price": product[2],
                "size": item['size'],
                "quantity": item['quantity'],
                "total_price": product[2] * item['quantity']
            })

    conn.close()

    return render_template('cart.html', cart=product_details)

from collections import defaultdict

@app.route('/boutique/<int:boutique_id>', methods=['GET'])
def boutique(boutique_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer les informations de la boutique
    cursor.execute("""
        SELECT nom, urlOrigine
        FROM Boutique
        WHERE pkBoutique = %s
    """, (boutique_id,))
    boutique = cursor.fetchone()

    if not boutique:
        conn.close()
        return "Boutique introuvable", 404

    # Récupérer les articles vendus, triés par catégorie
    cursor.execute("""
        SELECT c.nom AS categorie, p.pkProduit, p.nom, p.prix
        FROM Produit p
        JOIN Categorie c ON p.fkCategorie = c.pkCategorie
        WHERE p.fkBoutique = %s
        ORDER BY c.nom, p.nom
    """, (boutique_id,))
    articles = cursor.fetchall()

    # Organiser les articles par catégorie
    articles_par_categorie = defaultdict(list)
    for categorie, pkProduit, nom, prix in articles:
        articles_par_categorie[categorie].append({
            "pkProduit": pkProduit,
            "nom": nom,
            "prix": prix
        })

    # Récupérer les réseaux sociaux de la boutique
    cursor.execute("""
        SELECT typeSocial, url
        FROM RéseauSocial
        WHERE fkBoutique = %s
    """, (boutique_id,))
    reseaux = cursor.fetchall()

    # Récupérer les 5 derniers avis sur la boutique
    cursor.execute("""
        SELECT a.note, a.commentaire, u.nom, u.prenom
        FROM Avis a
        JOIN Produit p ON a.fkProduit = p.pkProduit
        JOIN Utilisateur u ON a.fkUtilisateur = u.pkUtilisateur
        WHERE p.fkBoutique = %s
        ORDER BY a.note DESC
        LIMIT 5
    """, (boutique_id,))
    avis = cursor.fetchall()

    conn.close()

    return render_template('boutique.html', 
                           boutique=boutique, 
                           articles_par_categorie=articles_par_categorie, 
                           reseaux=reseaux, 
                           avis=avis)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier si l'utilisateur existe et récupérer son rôle
        cursor.execute("""
            SELECT pkUtilisateur, role
            FROM Utilisateur
            WHERE email = %s AND motDePasse = %s
        """, (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, role = user
            # Stocker le rôle dans un cookie
            response = make_response(redirect('/'))
            response.set_cookie('user_role', role, max_age=30*24*60*60)  # Cookie valide 30 jours
            response.set_cookie('user_id', str(user_id), max_age=30*24*60*60)  # Stocker aussi l'ID utilisateur
            
        else:
            flash("Email ou mot de passe incorrect.", "danger")
            return render_template('login.html')

        session['email'] = email
        session['role'] = role  
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        role = request.form['role']
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        date_naissance = request.form['date_naissance']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insérer un nouvel utilisateur
            cursor.execute("""
                INSERT INTO Utilisateur (role, nom, prenom, email, motDePasse, dateNaissance)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (role, nom, prenom, email, password, date_naissance))
            conn.commit()
            flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
            return redirect('/login')
        except psycopg2.Error as e:
            flash("Erreur lors de la création du compte : " + str(e), "danger")
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', email=session['email'], role=session.get('role'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
