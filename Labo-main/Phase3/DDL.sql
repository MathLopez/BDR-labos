-- Création de la base de données
CREATE DATABASE ShopHabits;
\c ShopHabits;

-- Table Pays
CREATE TABLE Pays (
    pkPays SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    fraisLivraison NUMERIC(10, 2) NOT NULL
);

-- Table Adresse
CREATE TABLE Adresse (
    pkAdresse SERIAL PRIMARY KEY,
    rue VARCHAR(255) NOT NULL,
    no VARCHAR(50) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    codePostal VARCHAR(20) NOT NULL,
    fkPays INT NOT NULL REFERENCES Pays(pkPays)
);

-- Table Utilisateur
CREATE TABLE Utilisateur (
    pkUtilisateur SERIAL PRIMARY KEY,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Client', 'Vendeur', 'Admin')),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    dateNaissance DATE NOT NULL,
    motDePasse VARCHAR(255) NOT NULL,
    fkAdresseLivraison INT REFERENCES Adresse(pkAdresse),
    fkAdresseFacturation INT REFERENCES Adresse(pkAdresse)
);

-- Table Boutique
CREATE TABLE Boutique (
    pkBoutique SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    urlOrigine VARCHAR(255),
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur)
        CHECK (EXISTS (SELECT 1 FROM Utilisateur WHERE pkUtilisateur = fkUtilisateur AND role = 'Vendeur'))
);

-- Table Categorie
CREATE TABLE Categorie (
    pkCategorie SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

-- Table Produit
CREATE TABLE Produit (
    pkProduit SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    dateAjout DATE DEFAULT CURRENT_DATE,
    prix NUMERIC(10, 2) NOT NULL,
    sexe VARCHAR(10) CHECK (sexe IN ('Homme', 'Femme', 'Unisexe')),
    fkCategorie INT NOT NULL REFERENCES Categorie(pkCategorie),
    fkBoutique INT NOT NULL REFERENCES Boutique(pkBoutique)
);

-- Table Article
CREATE TABLE Article (
    pkProduit INT NOT NULL REFERENCES Produit(pkProduit),
    taille VARCHAR(10) NOT NULL,
    quantiteDisponible INT NOT NULL,
    PRIMARY KEY (pkProduit, taille)
);

-- Table Commande
CREATE TABLE Commande (
    pkCommande SERIAL PRIMARY KEY,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prix NUMERIC(10, 2) NOT NULL,
    typePaiement VARCHAR(20) NOT NULL CHECK (typePaiement IN ('twint', 'paypal', 'cb')),
    état VARCHAR(20) NOT NULL CHECK (état IN ('panier', 'commandé', 'livré')),
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur)
);

-- Table Contient
CREATE TABLE Contient (
    fkCommande INT NOT NULL REFERENCES Commande(pkCommande),
    fkArticleProduit INT NOT NULL,
    fkArticleTaille VARCHAR(10) NOT NULL,
    quantité INT NOT NULL,
    PRIMARY KEY (fkCommande, fkArticleProduit, fkArticleTaille),
    FOREIGN KEY (fkArticleProduit, fkArticleTaille) REFERENCES Article(pkProduit, taille)
);

-- Table RéseauSocial
CREATE TABLE RéseauSocial (
    pkRéseau SERIAL PRIMARY KEY,
    typeSocial VARCHAR(20) NOT NULL CHECK (typeSocial IN (
        'Facebook', 'Instagram', 'X', 'TikTok', 'Youtube', 
        'Snapchat', 'LinkedIn', 'Pinterest', 'Telegram', 
        'Discord', 'Reddit', 'Threads', 'Flickr'
    )),
    url VARCHAR(255) NOT NULL,
    fkBoutique INT NOT NULL REFERENCES Boutique(pkBoutique)
);

-- Table Avis
CREATE TABLE Avis (
    fkProduit INT NOT NULL REFERENCES Produit(pkProduit),
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur),
    note NUMERIC(2, 1) CHECK (note IN (1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)),
    commentaire TEXT,
    PRIMARY KEY (fkProduit, fkUtilisateur),
    CHECK (fkUtilisateur IN (
        SELECT fkUtilisateur 
        FROM Commande c
        JOIN Contient ct ON c.pkCommande = ct.fkCommande
        WHERE ct.fkArticleProduit = fkProduit AND c.état IN ('commandé', 'livré')
    ))
);
