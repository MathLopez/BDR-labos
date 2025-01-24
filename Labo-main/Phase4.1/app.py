from flask import Flask, render_template, request, make_response, redirect, flash, session, url_for
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

def get_boutique_id_for_current_user():
    # Vérifiez que l'utilisateur est connecté
    if 'user_id' not in session:
        raise Exception("Utilisateur non connecté.")

    # Récupérez l'ID de l'utilisateur connecté
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Recherchez l'ID de la boutique associée à cet utilisateur
        cur.execute("""
            SELECT pkBoutique
            FROM Boutique
            WHERE fkUtilisateur = %s
        """, (user_id,))
        result = cur.fetchone()

        if result is None:
            raise Exception("Aucune boutique associée à cet utilisateur.")

        return result[0]  # pkBoutique
    finally:
        cur.close()
        conn.close()

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

@app.route('/checkout', methods=['GET'])
def checkout():
    if 'email' not in session:
        return redirect(url_for('signup'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Récupération des informations utilisateur
        cursor.execute("""
            SELECT pkUtilisateur, fkAdresseLivraison, fkAdresseFacturation
            FROM Utilisateur
            WHERE email = %s
        """, (session['email'],))
        user = cursor.fetchone()

        if not user:
            return redirect(url_for('signup'))

        pkUtilisateur, fkAdresseLivraison, fkAdresseFacturation = user

        # Vérification des adresses
        if not fkAdresseLivraison or not fkAdresseFacturation:
            return redirect(url_for('profile'))

        # Récupération des adresses
        cursor.execute("""
            SELECT a.rue, a.no, a.ville, a.codePostal, p.nom, p.fraisLivraison
            FROM Adresse a
            JOIN Pays p ON a.fkPays = p.pkPays
            WHERE a.pkAdresse = %s
        """, (fkAdresseLivraison,))
        adresse_livraison = cursor.fetchone()

        cursor.execute("""
            SELECT a.rue, a.no, a.ville, a.codePostal, p.nom
            FROM Adresse a
            JOIN Pays p ON a.fkPays = p.pkPays
            WHERE a.pkAdresse = %s
        """, (fkAdresseFacturation,))
        adresse_facturation = cursor.fetchone()

        # Lecture du panier à partir des cookies
        cart_cookie = request.cookies.get('cart')
        if not cart_cookie:
            panier = []
        else:
            cart = json.loads(cart_cookie)
            # Récupérer les informations des produits en base
            panier = []
            for item in cart:
                cursor.execute("""
                    SELECT p.nom, a.taille, p.prix, %s AS quantité, p.prix * %s AS prix_total
                    FROM Produit p
                    JOIN Article a ON p.pkProduit = a.pkProduit
                    WHERE p.pkProduit = %s AND a.taille = %s
                """, (item['quantity'], item['quantity'], item['product_id'], item['size']))
                produit = cursor.fetchone()
                if produit:
                    panier.append({
                        'nom': produit[0],
                        'taille': produit[1],
                        'prix_unitaire': produit[2],
                        'quantité': produit[3],
                        'prix_total': produit[4]
                    })

        # Calcul des totaux
        total_commande = sum([article['prix_total'] for article in panier])
        frais_livraison = adresse_livraison[5]
        total_a_payer = total_commande + frais_livraison

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'checkout.html',
        adresse_livraison={
            'rue': adresse_livraison[0],
            'no': adresse_livraison[1],
            'ville': adresse_livraison[2],
            'code_postal': adresse_livraison[3],
            'pays': adresse_livraison[4],
        },
        adresse_facturation={
            'rue': adresse_facturation[0],
            'no': adresse_facturation[1],
            'ville': adresse_facturation[2],
            'code_postal': adresse_facturation[3],
            'pays': adresse_facturation[4],
        },
        panier=panier,
        total_commande=total_commande,
        frais_livraison=frais_livraison,
        total_a_payer=total_a_payer
    )

@app.route('/confirm-order', methods=['POST'])
def confirm_order():
    if 'email' not in session:
        return redirect(url_for('signup'))

    payment_method = request.form['payment_method']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Récupération de l'utilisateur
        cursor.execute("""
            SELECT pkUtilisateur
            FROM Utilisateur
            WHERE email = %s
        """, (session['email'],))
        user_id = cursor.fetchone()[0]

        # Lecture du panier à partir des cookies
        cart_cookie = request.cookies.get('cart')
        if not cart_cookie:
            flash("Votre panier est vide.", "danger")
            return redirect(url_for('home'))

        cart = json.loads(cart_cookie)
        total_commande = 0

        # Création de la commande
        cursor.execute("""
            INSERT INTO Commande (prix, typePaiement, état, fkUtilisateur)
            VALUES (0, %s, 'commandé', %s)
            RETURNING pkCommande
        """, (payment_method, user_id))
        commande_id = cursor.fetchone()[0]

        # Ajout des articles à la commande
        for item in cart:
            cursor.execute("""
                SELECT prix
                FROM Produit
                WHERE pkProduit = %s
            """, (item['product_id'],))
            prix_unitaire = cursor.fetchone()[0]

            total_commande += prix_unitaire * item['quantity']

            cursor.execute("""
                INSERT INTO Contient (fkCommande, fkArticleProduit, fkArticleTaille, quantité)
                VALUES (%s, %s, %s, %s)
            """, (commande_id, item['product_id'], item['size'], item['quantity']))

        # Mise à jour du prix total de la commande
        cursor.execute("""
            UPDATE Commande
            SET prix = %s
            WHERE pkCommande = %s
        """, (total_commande, commande_id))

        conn.commit()

        # Vider le panier (supprimer les cookies)
        response = make_response(redirect(url_for('home')))
        response.set_cookie('cart', '', max_age=0)
        flash("Commande confirmée avec succès !", "success")
        return response

    finally:
        cursor.close()
        conn.close()



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
                return redirect('/profile')
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
            # Insérer des adresses par défaut (vides) pour livraison et facturation
            cursor.execute("""
                INSERT INTO Adresse (rue, no, ville, codePostal, fkPays)
                VALUES ('', '', '', '', 1) RETURNING pkAdresse
            """)
            adresse_livraison_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO Adresse (rue, no, ville, codePostal, fkPays)
                VALUES ('', '', '', '', 1) RETURNING pkAdresse
            """)
            adresse_facturation_id = cursor.fetchone()[0]

            # Insérer un nouvel utilisateur avec les deux adresses associées
            cursor.execute("""
                INSERT INTO Utilisateur (role, nom, prenom, email, motDePasse, dateNaissance, fkAdresseLivraison, fkAdresseFacturation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING pkUtilisateur
            """, (role, nom, prenom, email, password, date_naissance, adresse_livraison_id, adresse_facturation_id))

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
    
@app.route('/profile', methods=['GET', 'POST'])
def profile_acheteur():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if request.method == 'POST':
            # Récupération des données du formulaire
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            password = request.form['password']

            # Données d'adresse de livraison
            rue_livraison = request.form['rue_livraison']
            no_livraison = request.form['no_livraison']
            ville_livraison = request.form['ville_livraison']
            code_postal_livraison = request.form['code_postal_livraison']
            pays_livraison = request.form['pays_livraison']

            # Données d'adresse de facturation
            rue_facturation = request.form['rue_facturation']
            no_facturation = request.form['no_facturation']
            ville_facturation = request.form['ville_facturation']
            code_postal_facturation = request.form['code_postal_facturation']
            pays_facturation = request.form['pays_facturation']

            # Mise à jour des informations personnelles
            cursor.execute("""
                UPDATE Utilisateur
                SET nom = %s, prenom = %s, email = %s
                WHERE pkUtilisateur = %s
            """, (nom, prenom, email, session['user_id']))

            # Mise à jour du mot de passe si nécessaire
            if password:
                hashed_password = hash_password(password)
                cursor.execute("""
                    UPDATE Utilisateur
                    SET motDePasse = %s
                    WHERE pkUtilisateur = %s
                """, (hashed_password, session['user_id']))

            # Mise à jour de l'adresse de livraison
            cursor.execute("""
                UPDATE Adresse
                SET rue = %s, no = %s, ville = %s, codePostal = %s, fkPays = %s
                WHERE pkAdresse = (
                    SELECT fkAdresseLivraison
                    FROM Utilisateur
                    WHERE pkUtilisateur = %s
                )
            """, (rue_livraison, no_livraison, ville_livraison, code_postal_livraison, pays_livraison, session['user_id']))

            # Mise à jour de l'adresse de facturation
            cursor.execute("""
                UPDATE Adresse
                SET rue = %s, no = %s, ville = %s, codePostal = %s, fkPays = %s
                WHERE pkAdresse = (
                    SELECT fkAdresseFacturation
                    FROM Utilisateur
                    WHERE pkUtilisateur = %s
                )
            """, (rue_facturation, no_facturation, ville_facturation, code_postal_facturation, pays_facturation, session['user_id']))

            # Sauvegarde des modifications
            conn.commit()
            flash("Profil mis à jour avec succès.", "success")

        # Récupération des informations utilisateur
        cursor.execute("""
            SELECT nom, prenom, email, fkAdresseLivraison, fkAdresseFacturation
            FROM Utilisateur
            WHERE pkUtilisateur = %s
        """, (session['user_id'],))
        user_data = cursor.fetchone()

        # Récupération de l'adresse de livraison
        cursor.execute("""
            SELECT rue, no, ville, codePostal, fkPays
            FROM Adresse
            WHERE pkAdresse = %s
        """, (user_data[3],))
        adresse_livraison = cursor.fetchone()

        # Récupération de l'adresse de facturation
        cursor.execute("""
            SELECT rue, no, ville, codePostal, fkPays
            FROM Adresse
            WHERE pkAdresse = %s
        """, (user_data[4],))
        adresse_facturation = cursor.fetchone()

        # Récupération des commandes de l'utilisateur
        cursor.execute("""
            SELECT c.pkCommande, c.date, c.prix, c.état
            FROM Commande c
            WHERE c.fkUtilisateur = %s
            ORDER BY c.date DESC
        """, (session['user_id'],))
        user_commandes = cursor.fetchall()

        # Récupération de la liste des pays
        cursor.execute("""
            SELECT pkPays, nom
            FROM Pays
            ORDER BY nom
        """)
        pays_liste = cursor.fetchall()

    except psycopg2.Error as e:
        conn.rollback()
        flash(f"Erreur : {str(e)}", "danger")
        user_data, adresse_livraison, adresse_facturation, user_commandes, pays_liste = None, None, None, None, None
    finally:
        cursor.close()
        conn.close()

    # Retourne les données à la page 'profile.html'
    return render_template('profile.html', commandes=user_commandes, user={
        'nom': user_data[0] if user_data else '',
        'prenom': user_data[1] if user_data else '',
        'email': user_data[2] if user_data else '',
        'adresse_livraison': {
            'rue': adresse_livraison[0] if adresse_livraison else '',
            'no': adresse_livraison[1] if adresse_livraison else '',
            'ville': adresse_livraison[2] if adresse_livraison else '',
            'code_postal': adresse_livraison[3] if adresse_livraison else '',
            'fkPays': adresse_livraison[4] if adresse_livraison else ''
        },
        'adresse_facturation': {
            'rue': adresse_facturation[0] if adresse_facturation else '',
            'no': adresse_facturation[1] if adresse_facturation else '',
            'ville': adresse_facturation[2] if adresse_facturation else '',
            'code_postal': adresse_facturation[3] if adresse_facturation else '',
            'fkPays': adresse_facturation[4] if adresse_facturation else ''
        }
    }, pays_liste=pays_liste)




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

    if not boutique:
        cur.close()
        conn.close()
        flash("Aucune boutique associée à cet utilisateur.", "danger")
        return redirect('/')

    # Récupérer les produits de la boutique avec les stocks
    cur.execute("""
        SELECT 
            Produit.pkProduit, 
            Produit.nom, 
            Produit.description, 
            Produit.prix, 
            Produit.sexe, 
            SUM(Article.quantiteDisponible) AS total_quantite
        FROM Produit
        LEFT JOIN Article ON Produit.pkProduit = Article.pkProduit
        WHERE Produit.fkBoutique = %s
        GROUP BY Produit.pkProduit, Produit.nom, Produit.description, Produit.prix, Produit.sexe
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

    # Récupérer les réseaux sociaux associés à la boutique
    cur.execute("""
        SELECT typeSocial, url 
        FROM RéseauSocial
        WHERE fkBoutique = %s
    """, (boutique[0],))
    reseaux_sociaux = cur.fetchall()
    # Récupérer les types de réseaux sociaux possibles
    cur.execute("SELECT unnest(enum_range(NULL::TypeSocialEnum))")
    types_reseaux = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'vendeur.html', 
        boutique=boutique, 
        produits=produits, 
        commandes=commandes, 
        avis=avis, 
        reseaux_sociaux=reseaux_sociaux, 
        types_reseaux=types_reseaux
    )

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

        if not categorie_id:
            flash("Veuillez sélectionner une catégorie.", "error")
            return redirect('/vendeur/produit/ajouter')

        # Insertion du produit
        cur.execute("""
            INSERT INTO Produit (nom, description, prix, sexe, fkCategorie, fkBoutique)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING pkProduit
        """, (nom, description, prix, sexe, categorie_id, boutique[0]))
        produit_id = cur.fetchone()[0]

        # Gestion des tailles et quantités
        if type_produit in ['Chaussure', 'Habit']:
            tailles = [str(i) for i in range(36, 46)] if type_produit == 'Chaussure' else ['XS', 'S', 'M', 'L', 'XL', 'XXL']
            for taille in tailles:
                quantite = request.form.get(f'quantite_{taille}', 0)
                if int(quantite) > 0:  # Ajouter uniquement si la quantité est > 0
                    cur.execute("""
                        INSERT INTO Article (pkProduit, taille, quantiteDisponible)
                        VALUES (%s, %s, %s)
                    """, (produit_id, taille, quantite))
        else:  # Accessoire
            quantite = request.form.get('quantite_accessoire', 0)
            if int(quantite) > 0:
                cur.execute("""
                    INSERT INTO Article (pkProduit, taille, quantiteDisponible)
                    VALUES (%s, %s, %s)
                """, (produit_id, 'Unique', quantite))

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

@app.route('/vendeur/reseau/ajouter', methods=['POST'])
def ajouter_reseau():
    # Récupération des données du formulaire
    type_social = request.form['typeSocial']
    url = request.form['url']
    boutique_id = get_boutique_id_for_current_user()
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insérer un nouveau réseau social
        cur.execute("""
            INSERT INTO RéseauSocial (typeSocial, url, fkBoutique)
            VALUES (%s, %s, %s)
        """, (type_social, url, boutique_id))
        conn.commit()
        flash('Réseau social ajouté avec succès.', 'success')
    except Exception as e:
        flash(f'Erreur lors de l’ajout : {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect('/vendeur')

@app.route('/vendeur/reseau/modifier', methods=['POST'])
def modifier_reseau():
    # Récupération des données du formulaire
    reseau_id = request.form['id']
    new_url = request.form['url']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Modifier l'URL du réseau social
        cur.execute("""
            UPDATE RéseauSocial
            SET url = %s
            WHERE pkRéseau = %s
        """, (new_url, reseau_id))
        conn.commit()
        flash('Réseau social modifié avec succès.', 'success')
    except Exception as e:
        flash(f'Erreur lors de la modification : {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect('/vendeur')

@app.route('/vendeur/reseau/supprimer', methods=['POST'])
def supprimer_reseau():
    # Récupération de l'ID du réseau social
    reseau_id = request.form['id']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Supprimer le réseau social
        cur.execute("""
            DELETE FROM RéseauSocial
            WHERE pkRéseau = %s
        """, (reseau_id,))
        conn.commit()
        flash('Réseau social supprimé avec succès.', 'success')
    except Exception as e:
        flash(f'Erreur lors de la suppression : {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect('/vendeur')

@app.route('/modifier_produit/<int:pkProduit>', methods=['GET', 'POST'])
def modifier_produit(pkProduit):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        description = request.form['description']
        prix = request.form['prix']
        sexe = request.form.get('sexe', None)  # Peut être vide, selon le type de produit

        try:
            # Mettre à jour les données du produit
            cur.execute("""
                UPDATE Produit
                SET nom = %s, description = %s, prix = %s, sexe = %s
                WHERE pkProduit = %s
            """, (nom, description, prix, sexe, pkProduit))
            conn.commit()

            flash("Le produit a été mis à jour avec succès.", "success")
            return redirect(f'/modifier_produit/{pkProduit}/')  # Redirige vers la modification du stock
        except Exception as e:
            conn.rollback()
            flash(f"Une erreur s'est produite : {e}", "danger")
    else:
        # Récupérer les informations actuelles du produit
        cur.execute("""
            SELECT nom, description, prix, sexe 
            FROM Produit
            WHERE pkProduit = %s
        """, (pkProduit,))
        produit = cur.fetchone()

        if not produit:
            cur.close()
            conn.close()
            flash("Le produit demandé n'existe pas.", "danger")
            return redirect('/vendeur')

        # Récupérer les stocks par taille
        cur.execute("""
            SELECT taille, quantiteDisponible
            FROM Article
            WHERE pkProduit = %s
        """, (pkProduit,))
        stocks = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('modifier_produit.html', produit=produit, pkProduit=pkProduit, stocks=stocks)


@app.route('/modifier_stock/<int:pkProduit>/<string:taille>', methods=['POST'])
def modifier_stock(pkProduit, taille):
    conn = get_db_connection()
    cur = conn.cursor()

    nouvelle_quantite = request.form['quantite']
    
    try:
        # Mettre à jour la quantité du stock pour cette taille
        cur.execute("""
            UPDATE Article
            SET quantiteDisponible = %s
            WHERE pkProduit = %s AND taille = %s
        """, (nouvelle_quantite, pkProduit, taille))
        conn.commit()

        flash("Le stock a été mis à jour avec succès.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Une erreur s'est produite : {e}", "danger")

    cur.close()
    conn.close()

    return redirect(f'/modifier_produit/{pkProduit}')

@app.route('/supprimer_stock/<int:pkProduit>/<string:taille>', methods=['POST'])
def supprimer_stock(pkProduit, taille):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Supprimer le stock de cette taille
        cur.execute("""
            DELETE FROM Article
            WHERE pkProduit = %s AND taille = %s
        """, (pkProduit, taille))
        conn.commit()

        flash("Le stock a été supprimé avec succès.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Une erreur s'est produite : {e}", "danger")

    cur.close()
    conn.close()

    return redirect(f'/modifier_produit/{pkProduit}')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
