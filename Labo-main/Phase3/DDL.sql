-- Supprimer toutes les tables existantes pour éviter les conflits
DO $$ 
BEGIN
    EXECUTE (
        SELECT string_agg('DROP TABLE IF EXISTS ' || tablename || ' CASCADE;', ' ')
        FROM pg_tables
        WHERE schemaname = 'public'
    );
END $$;

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
    fkPays INT NOT NULL REFERENCES Pays(pkPays)
);

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

CREATE TABLE Boutique (
    pkBoutique SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    urlOrigine VARCHAR(255),
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur)
);

CREATE TABLE Categorie (
    pkCategorie SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

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

CREATE TABLE Article (
    pkProduit INT NOT NULL REFERENCES Produit(pkProduit),
    taille VARCHAR(10) NOT NULL,
    quantiteDisponible INT NOT NULL,
    PRIMARY KEY (pkProduit, taille)
);

CREATE TABLE Commande (
    pkCommande SERIAL PRIMARY KEY,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prix NUMERIC(10, 2) NOT NULL,
    typePaiement VARCHAR(20) NOT NULL CHECK (typePaiement IN ('twint', 'paypal', 'cb')),
    état VARCHAR(20) NOT NULL CHECK (état IN ('panier', 'commandé', 'livré')),
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur)
);

CREATE TABLE Contient (
    fkCommande INT NOT NULL REFERENCES Commande(pkCommande),
    fkArticleProduit INT NOT NULL,
    fkArticleTaille VARCHAR(10) NOT NULL,
    quantité INT NOT NULL,
    PRIMARY KEY (fkCommande, fkArticleProduit, fkArticleTaille),
    FOREIGN KEY (fkArticleProduit, fkArticleTaille) REFERENCES Article(pkProduit, taille)
);

CREATE TABLE Avis (
    fkProduit INT NOT NULL REFERENCES Produit(pkProduit),
    fkUtilisateur INT NOT NULL REFERENCES Utilisateur(pkUtilisateur),
    note NUMERIC(2, 1) CHECK (note IN (1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)),
    commentaire TEXT,
    PRIMARY KEY (fkProduit, fkUtilisateur)
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

    RETURN NEW; -- Permet d'insérer la ligne si la vérification passe
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trigger_validate_avis
BEFORE INSERT ON Avis
FOR EACH ROW
EXECUTE FUNCTION validate_avis();

