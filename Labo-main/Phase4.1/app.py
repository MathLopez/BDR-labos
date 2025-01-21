from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)
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
    return psycopg2.connect(**DB_CONFIG)

# -------------------------
# Routes pour les utilisateurs
# -------------------------

@app.route("/utilisateur/inscription", methods=["POST"])
def inscription():
    data = request.json
    query = """
    INSERT INTO Utilisateur (role, nom, prenom, email, dateNaissance, motDePasse, fkAdresseLivraison, fkAdresseFacturation)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING pkUtilisateur;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['role'], data['nom'], data['prenom'], data['email'], 
            data['dateNaissance'], data['motDePasse'], data['fkAdresseLivraison'], data['fkAdresseFacturation']
        ))
        user_id = cur.fetchone()['pkUtilisateur']
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "user_id": user_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/utilisateur/connexion", methods=["POST"])
def connexion():
    data = request.json
    query = """
    SELECT pkUtilisateur, nom, prenom, role 
    FROM Utilisateur 
    WHERE email = %s AND motDePasse = %s;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (data['email'], data['motDePasse']))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return jsonify({"success": True, "user": user})
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# Routes pour les produits
# -------------------------

@app.route("/produits", methods=["GET"])
def get_products():
    query = """
    SELECT p.pkProduit, p.nom, p.description, p.prix, c.nom AS categorie, b.nom AS boutique
    FROM Produit p
    JOIN Categorie c ON p.fkCategorie = c.pkCategorie
    JOIN Boutique b ON p.fkBoutique = b.pkBoutique;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        products = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"success": True, "products": products})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/produit/<int:produit_id>", methods=["GET"])
def get_product(produit_id):
    query = """
    SELECT p.pkProduit, p.nom, p.description, p.prix, p.dateAjout, c.nom AS categorie, b.nom AS boutique
    FROM Produit p
    JOIN Categorie c ON p.fkCategorie = c.pkCategorie
    JOIN Boutique b ON p.fkBoutique = b.pkBoutique
    WHERE p.pkProduit = %s;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (produit_id,))
        product = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"success": True, "product": product})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/produit", methods=["POST"])
def add_product():
    data = request.json
    query = """
    INSERT INTO Produit (nom, description, prix, sexe, fkCategorie, fkBoutique)
    VALUES (%s, %s, %s, %s, %s, %s) RETURNING pkProduit;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['nom'], data['description'], data['prix'], 
            data['sexe'], data['fkCategorie'], data['fkBoutique']
        ))
        product_id = cur.fetchone()['pkProduit']
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "product_id": product_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# Routes pour les commandes
# -------------------------

@app.route("/commande", methods=["POST"])
def create_order():
    data = request.json
    query = """
    INSERT INTO Commande (prix, typePaiement, état, fkUtilisateur)
    VALUES (%s, %s, %s, %s) RETURNING pkCommande;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['prix'], data['typePaiement'], data['état'], data['fkUtilisateur']
        ))
        order_id = cur.fetchone()['pkCommande']
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "order_id": order_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/commande/<int:utilisateur_id>", methods=["GET"])
def get_orders(utilisateur_id):
    query = """
    SELECT c.pkCommande, c.date, c.prix, c.état, p.nom AS produit, co.quantité
    FROM Commande c
    JOIN Contient co ON c.pkCommande = co.fkCommande
    JOIN Produit p ON co.fkArticleProduit = p.pkProduit
    WHERE c.fkUtilisateur = %s;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (utilisateur_id,))
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"success": True, "orders": orders})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# Routes pour les avis
# -------------------------

@app.route("/avis/<int:produit_id>", methods=["GET"])
def get_reviews(produit_id):
    query = """
    SELECT a.note, a.commentaire, u.nom, u.prenom
    FROM Avis a
    JOIN Utilisateur u ON a.fkUtilisateur = u.pkUtilisateur
    WHERE a.fkProduit = %s;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (produit_id,))
        reviews = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"success": True, "reviews": reviews})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/avis", methods=["POST"])
def add_review():
    data = request.json
    query = """
    INSERT INTO Avis (fkProduit, fkUtilisateur, note, commentaire)
    VALUES (%s, %s, %s, %s);
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['fkProduit'], data['fkUtilisateur'], 
            data['note'], data.get('commentaire', None)
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Avis ajouté avec succès."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# Routes pour les boutiques
# -------------------------

@app.route("/boutiques", methods=["GET"])
def get_boutiques():
    query = """
    SELECT b.pkBoutique, b.nom, b.urlOrigine, u.nom AS propriétaire
    FROM Boutique b
    JOIN Utilisateur u ON b.fkUtilisateur = u.pkUtilisateur;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        boutiques = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"success": True, "boutiques": boutiques})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/boutique/<int:boutique_id>", methods=["GET"])
def get_boutique(boutique_id):
    query = """
    SELECT b.pkBoutique, b.nom, b.urlOrigine, u.nom AS propriétaire
    FROM Boutique b
    JOIN Utilisateur u ON b.fkUtilisateur = u.pkUtilisateur
    WHERE b.pkBoutique = %s;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (boutique_id,))
        boutique = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"success": True, "boutique": boutique})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/boutique", methods=["POST"])
def add_boutique():
    data = request.json
    query = """
    INSERT INTO Boutique (nom, urlOrigine, fkUtilisateur)
    VALUES (%s, %s, %s) RETURNING pkBoutique;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['nom'], data.get('urlOrigine', None), data['fkUtilisateur']
        ))
        boutique_id = cur.fetchone()['pkBoutique']
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "boutique_id": boutique_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# Routes pour les catégories
# -------------------------

@app.route("/categories", methods=["GET"])
def get_categories():
    query = """
    SELECT pkCategorie, nom
    FROM Categorie;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        categories = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"success": True, "categories": categories})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/categorie/<int:categorie_id>", methods=["GET"])
def get_category(categorie_id):
    query = """
    SELECT pkCategorie, nom
    FROM Categorie
    WHERE pkCategorie = %s;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (categorie_id,))
        category = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"success": True, "category": category})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/categorie", methods=["POST"])
def add_category():
    data = request.json
    query = """
    INSERT INTO Categorie (nom)
    VALUES (%s) RETURNING pkCategorie;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (data['nom'],))
        category_id = cur.fetchone()['pkCategorie']
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "category_id": category_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
