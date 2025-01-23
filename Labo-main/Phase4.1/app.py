from flask import Flask, render_template, jsonify, request, make_response, redirect, flash, session, url_for, send_from_directory
from datetime import date, timedelta
from functools import wraps
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

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        raise

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT pkBoutique, nom FROM Boutique LIMIT 5")
    boutiques = cursor.fetchall()

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

    cursor.execute("SELECT nom FROM Categorie")
    categories = [row[0] for row in cursor.fetchall()]

    category = request.args.get('category')
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

    return render_template('articles.html', articles=articles, categories=categories, selected_category=category)

@app.route('/article/<int:product_id>', methods=['GET'])
def product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.pkProduit, p.nom, p.description, p.prix, c.nom AS category_name
        FROM Produit p
        JOIN Categorie c ON p.fkCategorie = c.pkCategorie
        WHERE p.pkProduit = %s
    """, (product_id,))
    product = cursor.fetchone()

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

    cart = request.cookies.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = []

    for item in cart:
        if item['product_id'] == product_id and item['size'] == size:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'size': size, 'quantity': quantity})

    response = make_response(redirect('/cart'))
    response.set_cookie('cart', json.dumps(cart), max_age=30*24*60*60)
    return response

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form['product_id']
    size = request.form['size']

    cart = request.cookies.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = []

    cart = [item for item in cart if not (item['product_id'] == product_id and item['size'] == size)]

    response = make_response(redirect('/cart'))
    response.set_cookie('cart', json.dumps(cart), max_age=30*24*60*60)
    return response

@app.route('/cart', methods=['GET'])
def cart():
    cart = request.cookies.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = []

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

@app.route('/boutique/<int:boutique_id>')
def boutique(boutique_id):
   
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nom, urlOrigine
        FROM Boutique
        WHERE pkBoutique = %s
    """, (boutique_id,))
    boutique = cursor.fetchone()

    if not boutique:
        conn.close()
        return "Boutique introuvable", 404

    cursor.execute("""
        SELECT c.nom AS categorie, p.pkProduit, p.nom, p.prix
        FROM Produit p
        JOIN Categorie c ON p.fkCategorie = c.pkCategorie
        WHERE p.fkBoutique = %s
        ORDER BY c.nom, p.nom
    """, (boutique_id,))
    articles = cursor.fetchall()

    from collections import defaultdict
    articles_par_categorie = defaultdict(list)
    for categorie, pkProduit, nom, prix in articles:
        articles_par_categorie[categorie].append({
            "pkProduit": pkProduit,
            "nom": nom,
            "prix": prix
        })

    cursor.execute("""
        SELECT typeSocial, url
        FROM RéseauSocial
        WHERE fkBoutique = %s
    """, (boutique_id,))
    reseaux = cursor.fetchall()

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

        cursor.execute("""
            SELECT pkUtilisateur, role, email
            FROM Utilisateur
            WHERE email = %s AND motDePasse = %s
        """, (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, role, email = user
            session['user_id'] = user_id
            session['role'] = role
            session['email'] = email
            if role == 'Acheteur':
                return redirect('/profile/acheteur')
            elif role == 'Vendeur':
                return redirect('/vendeur')
            elif role == 'Admin':
                return redirect('/admin')
            else:
                flash('Identifiants invalides', 'danger')
        else:
            flash("Email ou mot de passe incorrect.", "danger")
            return render_template('login.html')

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

        print(f"Signup attempt: role={role}, nom={nom}, prenom={prenom}, email={email}, date_naissance={date_naissance}")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insérer un nouvel utilisateur
            cursor.execute("""
                INSERT INTO Utilisateur (role, nom, prenom, email, motDePasse, dateNaissance)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING pkUtilisateur
            """, (role, nom, prenom, email, password, date_naissance))
            
            # Récupérer l'ID de l'utilisateur créé
            user_id = cursor.fetchone()[0]

            # Si l'utilisateur est un vendeur, créer une boutique associée
            if role == 'Vendeur':
                cursor.execute("""
                    INSERT INTO Boutique (nom, fkUtilisateur)
                    VALUES (%s, %s)
                """, (f"Boutique de {prenom} {nom}", user_id))
            
            # Valider les transactions
            conn.commit()
            flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
            return redirect('/login')
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            flash("Erreur lors de la création du compte : " + str(e), "danger")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/access')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    role = session['role']
    if role == 'Acheteur':
        return redirect(url_for('profile'))
    elif role == 'Vendeur':
        return redirect(url_for('boutique', boutique_id=utilisateur_boutique_id(session['user_id'])))
    elif role == 'Admin':
        return redirect(url_for('admin_dashboard'))
    
@app.route('/profile')
def profile_acheteur():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.pkCommande, c.date, c.prix, c.état
        FROM Commande c
        WHERE c.fkUtilisateur = %s
        ORDER BY c.date DESC
    """, (session['user_id'],))
    user_commandes = cursor.fetchall()

    conn.close()

    return render_template('profile.html', commandes=user_commandes, user=session)

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'Admin':
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT pkUtilisateur, prenom, nom, email, role FROM Utilisateur")
    utilisateurs = cursor.fetchall()

    cursor.execute("SELECT pkProduit, nom, prix FROM Produit")
    articles = cursor.fetchall()

    cursor.execute("SELECT pkBoutique, nom FROM Boutique")
    boutiques = cursor.fetchall()

    cursor.execute("SELECT avis.fkutilisateur, avis.fkproduit, commentaire FROM Avis")
    avis = cursor.fetchall()

    cursor.execute("SELECT pkCategorie, nom FROM Categorie")
    categories = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_dashboard.html', 
        utilisateurs=utilisateurs, 
        articles=articles, 
        boutiques=boutiques, 
        avis=avis, 
        categories=categories
    )

@app.route('/admin/add_categorie', methods=['POST'])
def add_categorie():
    if session.get('role') != 'Admin':
        return redirect(url_for('profile'))

    # Récupérer le nom de la catégorie depuis le formulaire
    nom_categorie = request.form.get('nom_categorie')

    if not nom_categorie:
        flash("Le nom de la catégorie est obligatoire.", "error")
        return redirect('/admin')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier si la catégorie existe déjà
    cursor.execute("SELECT 1 FROM Categorie WHERE nom = %s", (nom_categorie,))
    if cursor.fetchone():
        flash("Cette catégorie existe déjà.", "error")
        conn.close()
        return redirect('/admin')

    # Insérer la nouvelle catégorie
    cursor.execute("INSERT INTO Categorie (nom) VALUES (%s)", (nom_categorie,))
    conn.commit()
    conn.close()

    flash("Catégorie ajoutée avec succès.", "success")
    return redirect('/admin')

@app.route('/admin/delete_categorie/<int:pkCategorie>', methods=['GET'])
def delete_categorie(pkCategorie):
    if session.get('role') != 'Admin':
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Supprimer la catégorie
    cursor.execute("DELETE FROM Categorie WHERE pkCategorie = %s", (pkCategorie,))
    conn.commit()
    conn.close()

    flash("Catégorie supprimée avec succès.", "success")
    return redirect('/admin')


@app.route('/admin/delete_utilisateur/<int:id>', methods=['GET'])
def delete_utilisateur(id):
    if session.get('role') != 'Admin':
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Utilisateur WHERE pkUtilisateur = %s", (id,))
    conn.commit()

    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_article/<int:id>', methods=['GET'])
def delete_article(id):
    if session.get('role') != 'Admin':
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Produit WHERE pkProduit = %s", (id,))
    conn.commit()

    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_boutique/<int:id>', methods=['GET'])
def delete_boutique(id):
    if session.get('role') != 'Admin':
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Boutique WHERE PkBoutique = %s", (id,))
    conn.commit()

    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_avis/<int:fkProduit>/<int:fkUtilisateur>', methods=['GET'])
def delete_avis(fkProduit, fkUtilisateur):
    if session.get('role') != 'Admin':
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM Avis
        WHERE fkProduit = %s AND fkUtilisateur = %s
    """, (fkProduit, fkUtilisateur))
    conn.commit()

    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route("/profile/info", methods=["GET"])
def get_profile_info():
    user_id = session.get('user_id')

    query = """
    SELECT nom, prenom, email, dateNaissance
    FROM Utilisateur
    WHERE pkUtilisateur = %s;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return jsonify({
                "success": True,
                "user": {
                    "nom": user[0],
                    "prenom": user[1],
                    "email": user[2],
                    "dateNaissance": user[3].strftime('%Y-%m-%d')
                }
            })
        return jsonify({
            "success": False,
            "error": "Utilisateur non trouvé"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/profile/update", methods=["POST"])
def update_profile():
    data = request.form
    user_id = session.get('user_id')
    
    query = """
    UPDATE Utilisateur
    SET nom = %s, prenom = %s, email = %s
    WHERE pkUtilisateur = %s;
    """
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['nom'],
            data['prenom'],
            data['email'],
            user_id
        ))
        conn.commit()
        
        # If password is provided, update it
        if data['password']:
            update_password_query = """
            UPDATE Utilisateur
            SET motDePasse = %s
            WHERE pkUtilisateur = %s;
            """
            cur.execute(update_password_query, (
                data['password'],
                user_id
            ))
            conn.commit()
        
        cur.close()
        conn.close()
        flash("Profil mis à jour avec succès", "success")
        return redirect(url_for('profile_acheteur'))
    except Exception as e:
        flash(f"Erreur lors de la mise à jour du profil: {str(e)}", "danger")
        return redirect(url_for('profile_acheteur'))@app.route("/profile/password", methods=["POST"])

def update_password():
    data = request.json
    user_id = session.get('user_id')

    verify_query = """
    SELECT pkUtilisateur
    FROM Utilisateur
    WHERE pkUtilisateur = %s AND motDePasse = %s;
    """

    update_query = """
    UPDATE Utilisateur
    SET motDePasse = %s
    WHERE pkUtilisateur = %s;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(verify_query, (user_id, data['currentPassword']))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Mot de passe actuel incorrect"
            })

        cur.execute(update_query, (data['newPassword'], user_id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Mot de passe mis à jour avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/profile/orders", methods=["GET"])
def get_profile_orders():
    user_id = session.get('user_id')

    query = """
    SELECT pkCommande, date, prix, état
    FROM Commande
    WHERE fkUtilisateur = %s
    ORDER BY date DESC;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        orders = cur.fetchall()
        cur.close()
        conn.close()

        orders_list = [{
            "pkCommande": order[0],
            "date": order[1].isoformat(),
            "prix": float(order[2]),
            "état": order[3]
        } for order in orders]

        return jsonify({
            "success": True,
            "orders": orders_list
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/cart/items', methods=["GET"])
def get_cart_items():
    user_id = session.get('user_id')

    query = """
    SELECT p.pkProduit, p.nom, p.prix, c.quantité, c.fkArticleTaille as taille
    FROM Commande cmd
    JOIN Contient c ON cmd.pkCommande = c.fkCommande
    JOIN Produit p ON c.fkArticleProduit = p.pkProduit
    WHERE cmd.fkUtilisateur = %s AND cmd.état = 'panier';
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        items = [
            {
                "pkProduit": row[0],
                "nom": row[1],
                "prix": float(row[2]),
                "quantité": row[3],
                "taille": row[4]
            }
            for row in cur.fetchall()
        ]

        subtotal = sum(item["prix"] * item["quantité"] for item in items)
        shipping = 0
        total = subtotal + shipping
        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "items": items,
            "summary": {
                "subtotal": subtotal,
                "shipping": shipping,
                "total": total
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/cart/update", methods=["POST"])
def update_cart_item():
    data = request.json
    user_id = session.get('user_id')

    query = """
    UPDATE Contient c
    SET quantité = quantité + %s
    FROM Commande cmd
    WHERE cmd.pkCommande = c.fkCommande
    AND cmd.fkUtilisateur = %s
    AND cmd.état = 'panier'
    AND c.fkArticleProduit = %s
    AND c.fkArticleTaille = %s;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['change'],
            user_id,
            data['productId'],
            data['size']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/cart/remove", methods=["POST"])
def remove_cart_item():
    data = request.json
    user_id = session.get('user_id')

    query = """
    DELETE FROM Contient c
    USING Commande cmd
    WHERE cmd.pkCommande = c.fkCommande
    AND cmd.fkUtilisateur = %s
    AND cmd.état = 'panier'
    AND c.fkArticleProduit = %s
    AND c.fkArticleTaille = %s;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            user_id,
            data['productId'],
            data['size']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/cart/checkout", methods=["POST"])
def checkout():
    user_id = session.get('user_id')

    query = """
    UPDATE Commande
    SET état = 'commandé'
    WHERE fkUtilisateur = %s AND état = 'panier'
    RETURNING pkCommande;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "orderId": order_id
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/checkout", methods=["GET"])
def checkout_page():
    return send_from_directory('www', 'checkout.html')

@app.route("/checkout/summary", methods=["GET"])
def get_checkout_summary():
    user_id = session.get('user_id')

    query = """
    SELECT p.pkProduit, p.nom, p.prix, c.quantité
    FROM Commande cmd
    JOIN Contient c ON cmd.pkCommande = c.fkCommande
    JOIN Produit p ON c.fkArticleProduit = p.pkProduit
    WHERE cmd.fkUtilisateur = %s AND cmd.état = 'panier';
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        items = [
            {
                "pkProduit": row[0],
                "nom": row[1],
                "prix": float(row[2]),
                "quantité": row[3]
            }
            for row in cur.fetchall()
        ]

        subtotal = sum(item["prix"] * item["quantité"] for item in items)
        shipping = 10.00
        total = subtotal + shipping

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "items": items,
            "summary": {
                "subtotal": subtotal,
                "shipping": shipping,
                "total": total
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/checkout/process", methods=["POST"])
def process_checkout():
    data = request.json
    user_id = session.get('user_id')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Commande
            SET état = 'commandé',
                typePaiement = %s
            WHERE fkUtilisateur = %s AND état = 'panier'
            RETURNING pkCommande;
        """, (data['paymentMethod'], user_id))

        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "orderId": order_id,
            "message": "Commande traitée avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/register", methods=["GET"])
def register_page():
    return send_from_directory('www', 'register.html')

@app.route("/register", methods=["POST"])
def register_user():
    data = request.json

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Adresse (rue, no, ville, codePostal, fkPays)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING pkAdresse;
        """, (
            data['adresseLivraison']['rue'],
            data['adresseLivraison']['no'],
            data['adresseLivraison']['ville'],
            data['adresseLivraison']['codePostal'],
            data['adresseLivraison']['fkPays']
        ))
        adresse_livraison_id = cur.fetchone()[0]

        if data['adresseFacturation']:
            cur.execute("""
                INSERT INTO Adresse (rue, no, ville, codePostal, fkPays)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING pkAdresse;
            """, (
                data['adresseFacturation']['rue'],
                data['adresseFacturation']['no'],
                data['adresseFacturation']['ville'],
                data['adresseFacturation']['codePostal'],
                data['adresseFacturation']['fkPays']
            ))
            adresse_facturation_id = cur.fetchone()[0]
        else:
            adresse_facturation_id = adresse_livraison_id

        cur.execute("""
            INSERT INTO Utilisateur (
                role, nom, prenom, email, dateNaissance, motDePasse,
                fkAdresseLivraison, fkAdresseFacturation
            )
            VALUES ('Client', %s, %s, %s, %s, %s, %s, %s)
            RETURNING pkUtilisateur;
        """, (
            data['nom'],
            data['prenom'],
            data['email'],
            data['dateNaissance'],
            data['password'],
            adresse_livraison_id,
            adresse_facturation_id
        ))

        user_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({
            "success": True,
            "userId": user_id,
            "message": "Inscription réussie"
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        })
    finally:
        cur.close()
        conn.close()

@app.route("/api/countries", methods=["GET"])
def get_countries():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT pkPays, nom FROM Pays ORDER BY nom;")
        countries = [{"pkPays": row[0], "nom": row[1]} for row in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "countries": countries
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })
# Route principale pour le vendeur
@app.route('/vendeur')
def vendeur():
    conn = get_db_connection()
    cur = conn.cursor()

    # Récupérer les informations de la boutique
    cur.execute("""
        SELECT pkBoutique, nom, urlOrigine 
        FROM Boutique 
        WHERE fkUtilisateur = %s
    """, (session['user_id'],))
    boutique = cur.fetchone()

    # Récupérer les produits de la boutique
    cur.execute("""
        SELECT pkProduit, nom, description, prix, sexe 
        FROM Produit 
        WHERE fkBoutique = %s
    """, (boutique[0],))
    produits = cur.fetchall()

    # Récupérer les commandes associées à la boutique
    cur.execute("""
        SELECT Commande.pkCommande, Commande.date, Commande.prix, Commande.état 
        FROM Commande
        JOIN Contient ON Contient.fkCommande = Commande.pkCommande
        JOIN Article ON Article.pkProduit = Contient.fkArticleProduit
        JOIN Produit ON Produit.pkProduit = Article.pkProduit
        WHERE Produit.fkBoutique = %s
    """, (boutique[0],))
    commandes = cur.fetchall()

    # Récupérer les avis sur les produits de la boutique
    cur.execute("""
        SELECT Avis.fkProduit, Avis.note, Avis.commentaire, Produit.nom 
        FROM Avis
        JOIN Produit ON Produit.pkProduit = Avis.fkProduit
        WHERE Produit.fkBoutique = %s
    """, (boutique[0],))
    avis = cur.fetchall()

    cur.execute("SELECT unnest(enum_range(NULL::TypeSocialEnum))")
    types_reseaux = cur.fetchall()
    
    cur.close()
    conn.close()

    return render_template('vendeur.html', boutique=boutique, produits=produits, commandes=commandes, avis=avis, types_reseaux=types_reseaux)

# Route pour configurer la boutique
@app.route('/vendeur/configurer', methods=['POST'])
def configurer_boutique():
    nom_boutique = request.form['nom_boutique']
    url_origine = request.form['url']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE Boutique 
        SET nom = %s, urlOrigine = %s 
        WHERE fkUtilisateur = %s
    """, (nom_boutique, url_origine, session['user_id']))
    conn.commit()

    cur.close()
    conn.close()

    flash("Configuration de la boutique mise à jour avec succès.", "success")
    return redirect(url_for('vendeur'))

# Route pour ajouter un produit
@app.route('/vendeur/produit/ajouter', methods=['GET', 'POST'])
def ajouter_produit():
    conn = get_db_connection()
    cur = conn.cursor()

    # Récupérer la boutique associée à l'utilisateur connecté
    cur.execute("""
        SELECT pkBoutique, nom 
        FROM Boutique 
        WHERE fkUtilisateur = %s
    """, (session['user_id'],))
    boutique = cur.fetchone()

    if not boutique:
        flash("Aucune boutique trouvée pour cet utilisateur.", "error")
        return redirect('/vendeur')

    # Récupérer toutes les catégories disponibles
    cur.execute("SELECT pkCategorie, nom FROM Categorie")
    categories = cur.fetchall()

    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom_produit']
        prix = request.form['prix_produit']
        description = request.form['description_produit']
        sexe = request.form.get('sexe_produit')  # Homme/Femme/Unisexe
        categorie_id = request.form.get('categorie')  # ID de la catégorie sélectionnée
        type_produit = request.form.get('type_produit')  # Type de produit (Chaussure, Habit, Accessoire)

        # Validation des données du formulaire
        if not categorie_id:
            flash("Veuillez sélectionner une catégorie.", "error")
            return redirect('/vendeur/produit/ajouter')

        # Insertion du produit
        cur.execute("""
            INSERT INTO Produit (nom, description, prix, sexe, fkCategorie, fkBoutique)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING pkProduit
        """, (nom, description, prix, sexe, categorie_id, boutique[0]))
        produit_id = cur.fetchone()[0]

        # Gestion des tailles et quantités si le produit est une chaussure ou un habit
        tailles = []
        if type_produit == 'Chaussure':
            tailles = [str(i) for i in range(36, 46)]
        elif type_produit == 'Habit':
            tailles = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

        if tailles:
            for taille in tailles:
                quantite = request.form.get(f'quantite_{taille}', 0)
                cur.execute("""
                    INSERT INTO Article (pkProduit, taille, quantiteDisponible)
                    VALUES (%s, %s, %s)
                """, (produit_id, taille, quantite))

        conn.commit()
        flash("Produit ajouté avec succès !", "success")
        return redirect('/vendeur')

    cur.close()
    conn.close()
    return render_template('ajouter_produit.html', boutique=boutique, categories=categories)



# Route pour supprimer un produit
@app.route('/vendeur/produit/supprimer/<int:produit_id>')
def supprimer_produit(produit_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM Produit WHERE pkProduit = %s", (produit_id,))
    conn.commit()

    cur.close()
    conn.close()

    flash("Produit supprimé avec succès.", "success")
    return redirect(url_for('vendeur'))

# Route pour valider une commande
@app.route('/vendeur/commande/valider/<int:commande_id>')
def valider_commande(commande_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE Commande 
        SET état = 'livré' 
        WHERE pkCommande = %s
    """, (commande_id,))
    conn.commit()

    cur.close()
    conn.close()

    flash("Commande validée avec succès.", "success")
    return redirect(url_for('vendeur'))

@app.route('/vendeur/reseaux', methods=['GET', 'POST'])
def gestion_reseaux_sociaux():
    if 'user_id' not in session:
        flash("Veuillez vous connecter.", "danger")
        return redirect('/login')

    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Vérifier si l'utilisateur a une boutique
        cursor.execute("SELECT pkBoutique FROM Boutique WHERE fkUtilisateur = %s", (user_id,))
        boutique = cursor.fetchone()

        if not boutique:
            flash("Aucune boutique associée à cet utilisateur.", "danger")
            return redirect('/vendeur')

        boutique_id = boutique[0]
        
        # Récupérer les types de réseaux sociaux disponibles
        cursor.execute("SELECT unnest(enum_range(NULL::TypeSocialEnum))")
        types_reseaux = cursor.fetchall()

        if request.method == 'POST':
            type_social = request.form['type_social']
            url = request.form['url']

            # Insérer le nouveau réseau social
            cursor.execute("""
                INSERT INTO RéseauSocial (typeSocial, url, fkBoutique)
                VALUES (%s, %s, %s)
            """, (type_social, url, boutique_id))
            conn.commit()
            flash("Réseau social ajouté avec succès.", "success")
            return render_template('vendeur.html')

        # Récupérer les réseaux sociaux existants
        cursor.execute("""
            SELECT pkRéseau, typeSocial, url 
            FROM RéseauSocial 
            WHERE fkBoutique = %s
        """, (boutique_id,))
        reseaux_sociaux = cursor.fetchall()

    except Exception as e:
        flash(f"Erreur lors de la gestion des réseaux sociaux : {e}", "danger")
        reseaux_sociaux = []
        types_reseaux = []
    finally:
        conn.close()

    return render_template('vendeur.html', reseaux_sociaux=[
        {'id': r[0], 'type_social': r[1], 'url': r[2]} for r in reseaux_sociaux
    ], types_reseaux=[r[0] for r in types_reseaux])  # Passer les types de réseaux sociaux disponibles


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
