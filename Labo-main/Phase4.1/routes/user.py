from flask import Blueprint, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from connect_db.connect_db import get_db_connection
from functools import wraps

user_bp = Blueprint('user', __name__)

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return send_from_directory('www', 'login.html')
    
    elif request.method == "POST":
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Email et mot de passe requis"
            })

        query = """
        SELECT pkUtilisateur, nom, prenom, role 
        FROM Utilisateur 
        WHERE email = %s AND motDePasse = %s;
        """
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(query, (email, password))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user:
                return jsonify({
                    "success": True,
                    "user": {
                        "id": user[0],
                        "nom": user[1],
                        "prenom": user[2],
                        "role": user[3]
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Email ou mot de passe incorrect"
                })

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })

@user_bp.route("/profile", methods=["GET"])
def profile_page():
    return send_from_directory('www', 'profile.html')

@user_bp.route("/profile/info", methods=["GET"])
def get_profile_info():
    # In a real app, you'd get the user_id from the session
    # This is just for demonstration
    user_id = request.args.get('user_id')
    
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

@user_bp.route("/profile/update", methods=["POST"])
def update_profile():
    data = request.json
    # In a real app, you'd get the user_id from the session
    user_id = request.args.get('user_id')
    
    query = """
    UPDATE Utilisateur
    SET nom = %s, prenom = %s, email = %s, dateNaissance = %s
    WHERE pkUtilisateur = %s;
    """
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (
            data['nom'],
            data['prenom'],
            data['email'],
            data['dateNaissance'],
            user_id
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "success": True,
            "message": "Profil mis à jour avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@user_bp.route("/profile/password", methods=["POST"])
def update_password():
    data = request.json
    # In a real app, you'd get the user_id from the session
    user_id = request.args.get('user_id')
    
    # First verify current password
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
        
        # Verify current password
        cur.execute(verify_query, (user_id, data['currentPassword']))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Mot de passe actuel incorrect"
            })
        
        # Update password
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

@user_bp.route("/profile/orders", methods=["GET"])
def get_profile_orders():
    # In a real app, you'd get the user_id from the session
    user_id = request.args.get('user_id')
    
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

@user_bp.route('/logout', methods=['POST'])
def logout():
    # In a real application, you would:
    # 1. Clear the session
    # 2. Remove any authentication tokens
    # 3. Perform any necessary cleanup
    
    try:
        # session.clear()  # If using Flask-Session
        return jsonify({
            "success": True,
            "message": "Déconnexion réussie"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@user_bp.route("/cart", methods=["GET"])
def cart_page():
    return send_from_directory('www', 'cart.html')

@user_bp.route("/cart/items", methods=["GET"])
def get_cart_items():
    # In a real app, you'd get the user_id from the session
    user_id = request.args.get('user_id')
    
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
        
        # Calculate totals
        subtotal = sum(item["prix"] * item["quantité"] for item in items)
        shipping = 0  # You might want to calculate this based on user's location
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

@user_bp.route("/cart/update", methods=["POST"])
def update_cart_item():
    data = request.json
    user_id = request.args.get('user_id')
    
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

@user_bp.route("/cart/remove", methods=["POST"])
def remove_cart_item():
    data = request.json
    user_id = request.args.get('user_id')
    
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

@user_bp.route("/cart/checkout", methods=["POST"])
def checkout():
    user_id = request.args.get('user_id')
    
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

@user_bp.route("/checkout", methods=["GET"])
def checkout_page():
    return send_from_directory('www', 'checkout.html')

@user_bp.route("/checkout/summary", methods=["GET"])
def get_checkout_summary():
    user_id = request.args.get('user_id')
    
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
        shipping = 10.00  # Fixed shipping cost for demo
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

@user_bp.route("/checkout/process", methods=["POST"])
def process_checkout():
    data = request.json
    user_id = request.args.get('user_id')
    
    # In a real application, you would:
    # 1. Validate the payment information
    # 2. Process the payment with a payment provider
    # 3. Create a proper order record
    # 4. Handle inventory updates
    # 5. Send confirmation emails
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update the order status
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

@user_bp.route("/register", methods=["GET"])
def register_page():
    return send_from_directory('www', 'register.html')

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # First, insert the delivery address
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
        
        # If billing address is different, insert it
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
        
        # Insert the user
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
            data['password'],  # In production, hash this!
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

@register_routes.route("/api/countries", methods=["GET"])
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
