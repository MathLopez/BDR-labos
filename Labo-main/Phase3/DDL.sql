-- Supprimer toutes les tables existantes pour éviter les conflits
DO $$ 
BEGIN
    EXECUTE (
        SELECT string_agg('DROP TABLE IF EXISTS ' || tablename || ' CASCADE;', ' ')
        FROM pg_tables
        WHERE schemaname = 'public'
    );
END $$;

-- Création des types ENUM
CREATE TYPE RoleEnum AS ENUM ('Client', 'Vendeur', 'Admin');
CREATE TYPE SexeEnum AS ENUM ('Homme', 'Femme', 'Unisexe');
CREATE TYPE TypePaiementEnum AS ENUM ('twint', 'paypal', 'cb');
CREATE TYPE EtatEnum AS ENUM ('panier', 'commandé', 'livré');
CREATE TYPE TypeSocialEnum AS ENUM (
    'Facebook', 'Instagram', 'X', 'TikTok', 'Youtube', 
    'Snapchat', 'LinkedIn', 'Pinterest', 'Telegram', 
    'Discord', 'Reddit', 'Threads', 'Flickr'
);

-- Création des tables
CREATE TABLE Pays (
    pkPays SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    fraisLivraison NUMERIC(10, 2) NOT NULL
);

CREATE TABLE Adresse (
    pkAdresse SERIAL PRIMARY KEY,
    rue VARCHAR(255) NOT NULL,
    no VARCHAR(50) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    codePostal VARCHAR(20) NOT NULL,
    fkPays INT NOT NULL REFERENCES Pays(pkPays) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Utilisateur (
    pkUtilisateur SERIAL PRIMARY KEY,
    role RoleEnum NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    dateNaissance DATE NOT NULL,
    motDePasse VARCHAR(255) NOT NULL,
    fkAdresseLivraison INT REFERENCES Adresse(pkAdresse) ON UPDATE CASCADE ON DELETE SET NULL,
    fkAdresseFacturation INT REFERENCES Adresse(pkAdresse) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE Boutique (
    pkBoutique SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    urlOrigine VARCHAR(255),
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Categorie (
    pkCategorie SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

CREATE TABLE Produit (
    pkProduit SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    dateAjout DATE DEFAULT CURRENT_DATE,
    prix NUMERIC(10, 2) NOT NULL,
    sexe SexeEnum,
    fkCategorie INT NOT NULL REFERENCES Categorie(pkCategorie) ON UPDATE CASCADE ON DELETE CASCADE,
    fkBoutique INT NOT NULL REFERENCES Boutique(pkBoutique) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Article (
    pkProduit INT NOT NULL REFERENCES Produit(pkProduit) ON UPDATE CASCADE ON DELETE CASCADE,
    taille VARCHAR(10) NOT NULL,
    quantiteDisponible INT NOT NULL,
    PRIMARY KEY (pkProduit, taille)
);

CREATE TABLE Commande (
    pkCommande SERIAL PRIMARY KEY,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prix NUMERIC(10, 2) NOT NULL,
    typePaiement TypePaiementEnum NOT NULL,
    état EtatEnum NOT NULL,
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Contient (
    fkCommande INT NOT NULL REFERENCES Commande(pkCommande) ON UPDATE CASCADE ON DELETE CASCADE,
    fkArticleProduit INT NOT NULL,
    fkArticleTaille VARCHAR(10) NOT NULL,
    quantité INT NOT NULL,
    PRIMARY KEY (fkCommande, fkArticleProduit, fkArticleTaille),
    FOREIGN KEY (fkArticleProduit, fkArticleTaille) REFERENCES Article(pkProduit, taille) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Avis (
    fkProduit INT NOT NULL REFERENCES Produit(pkProduit) ON UPDATE CASCADE ON DELETE CASCADE,
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur) ON UPDATE CASCADE ON DELETE CASCADE,
    note NUMERIC(2, 1) CHECK (note IN (1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)),
    commentaire TEXT,
    PRIMARY KEY (fkProduit, fkUtilisateur)
);

CREATE TABLE RéseauSocial (
    pkRéseau SERIAL PRIMARY KEY,
    typeSocial TypeSocialEnum NOT NULL,
    url VARCHAR(255) NOT NULL,
    fkBoutique INT NOT NULL REFERENCES Boutique(pkBoutique) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Fonction et trigger pour valider les avis
CREATE OR REPLACE FUNCTION validate_avis()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérification : l'utilisateur doit avoir commandé ou reçu le produit
    IF NOT EXISTS (
        SELECT 1
        FROM Commande c
        JOIN Contient ct ON c.pkCommande = ct.fkCommande
        WHERE c.fkUtilisateur = NEW.fkUtilisateur
          AND ct.fkArticleProduit = NEW.fkProduit
          AND c.état IN ('commandé', 'livré')
    ) THEN
        RAISE EXCEPTION 'Utilisateur % n''a pas commandé ou reçu le produit %', NEW.fkUtilisateur, NEW.fkProduit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_avis
BEFORE INSERT ON Avis
FOR EACH ROW
EXECUTE FUNCTION validate_avis();
