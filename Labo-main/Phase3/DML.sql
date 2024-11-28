-- Pays
INSERT INTO Pays (nom, fraisLivraison) VALUES
('France', 5.00),
('Suisse', 10.00);

-- Adresse
INSERT INTO Adresse (rue, no, ville, codePostal, fkPays) VALUES
('Rue de la Paix', '10', 'Paris', '75001', 1);

-- Utilisateur
INSERT INTO Utilisateur (role, nom, prenom, email, dateNaissance, motDePasse, fkAdresseLivraison, fkAdresseFacturation) VALUES
('Client', 'Dupont', 'Jean', 'jean.dupont@example.com', '1980-05-15', 'password123', 1, 1),
('Vendeur', 'Martin', 'Claire', 'claire.martin@example.com', '1990-10-20', 'securepwd456', 1, 1);

-- Boutique
INSERT INTO Boutique (nom, urlOrigine, fkUtilisateur) VALUES
('Boutique Claire', 'https://shopclaire.com', 2);

-- Catégorie
INSERT INTO Categorie (nom) VALUES
('Vêtements');

-- Produit
INSERT INTO Produit (nom, description, dateAjout, prix, sexe, fkCategorie, fkBoutique) VALUES
('T-Shirt', 'T-shirt en coton bio', CURRENT_DATE, 20.00, 'Unisexe', 1, 1);

-- Article
INSERT INTO Article (pkProduit, taille, quantiteDisponible) VALUES
(1, 'M', 50);

-- Commande
INSERT INTO Commande (date, prix, typePaiement, état, fkUtilisateur) VALUES
(CURRENT_TIMESTAMP, 40.00, 'paypal', 'commandé', 1);

-- Contient
INSERT INTO Contient (fkCommande, fkArticleProduit, fkArticleTaille, quantité) VALUES
(1, 1, 'M', 2);

-- Avis
INSERT INTO Avis (fkProduit, fkUtilisateur, note, commentaire)
VALUES (1, 1, 4.5, 'Très bon produit');
