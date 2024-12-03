SET client_encoding TO 'UTF8';


DROP VIEW IF EXISTS vCoach;
DROP VIEW IF EXISTS vGymnaste;

DROP TABLE IF EXISTS Inscription;
DROP TABLE IF EXISTS Evenement;
DROP TABLE IF EXISTS Gymnaste_Discipline;
DROP TABLE IF EXISTS Gymnaste;
DROP TABLE IF EXISTS Coach;
DROP TABLE IF EXISTS Personne;
DROP TABLE IF EXISTS Federation;
DROP TABLE IF EXISTS Pays;
DROP TABLE IF EXISTS Discipline;


CREATE TABLE Discipline (
	code char(3),
	nom varchar(20) NOT NULL,
	CONSTRAINT PK_Discipline PRIMARY KEY (code)
);


CREATE TABLE Pays (
	id serial,
	nom varchar(20) NOT NULL,
	CONSTRAINT PK_Pays PRIMARY KEY (id),
	CONSTRAINT UC_Pays_nom UNIQUE (nom)
);


CREATE TABLE Federation (
	id serial,
	idPays integer NOT NULL,
	nom varchar(50) NOT NULL,
	CONSTRAINT PK_Federation PRIMARY KEY (id),
	CONSTRAINT UC_Federation_nom UNIQUE (nom),
	CONSTRAINT FK_Federation_idPays
		FOREIGN KEY (idPays)
		REFERENCES Pays (id)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);


CREATE TABLE Personne (
	id serial,
	idPays integer NOT NULL,
	nom varchar(50) NOT NULL,
	prenom varchar(50) NOT NULL,
	dateNaissance timestamp NOT NULL,
	CONSTRAINT PK_Personne PRIMARY KEY (id),
	CONSTRAINT FK_Personne_idPays
		FOREIGN KEY (idPays)
		REFERENCES Pays (id)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);


CREATE TABLE Coach (
	idPersonne integer,
	codeDiscipline char(3) NOT NULL,
	CONSTRAINT PK_Coach PRIMARY KEY (idPersonne),
	CONSTRAINT FK_Coach_idPersonne
		FOREIGN KEY (idPersonne)
		REFERENCES Personne (id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT FK_Coach_codeDiscipline
		FOREIGN KEY (codeDiscipline)
		REFERENCES Discipline (code)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);


CREATE TABLE Gymnaste (
	idPersonne integer,
	idCoach integer,
	idFederation integer NOT NULL,
	CONSTRAINT PK_Gymnaste PRIMARY KEY (idPersonne),
	CONSTRAINT FK_Gymnaste_idPersonne
		FOREIGN KEY (idPersonne)
		REFERENCES Personne (id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT FK_Gymnaste_idCoach
		FOREIGN KEY (idCoach)
		REFERENCES Coach (idPersonne)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT,
	CONSTRAINT FK_Gymnaste_idFederation
		FOREIGN KEY (idFederation)
		REFERENCES Federation (id)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);


CREATE TABLE Gymnaste_Discipline (
	idGymnaste integer,
	codeDiscipline char(3),
	CONSTRAINT PK_Gymnaste_Discipline PRIMARY KEY (idGymnaste, codeDiscipline),
	CONSTRAINT FK_Gymnaste_Discipline_idGymnaste
		FOREIGN KEY (idGymnaste)
		REFERENCES Gymnaste (idPersonne)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT,
	CONSTRAINT FK_Gymnaste_Discipline_codeDiscipline
		FOREIGN KEY (codeDiscipline)
		REFERENCES Discipline (code)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);


CREATE TABLE Evenement (
	id serial,
	idFederation integer NOT NULL,
	nom varchar(50) NOT NULL,
	dateOuverture timestamp NOT NULL,
	fraisInscription integer NOT NULL,
	CONSTRAINT PK_Evenement PRIMARY KEY (id),
	CONSTRAINT UC_Evenement_nom UNIQUE (nom),
	CONSTRAINT FK_Evenement_idFederation
		FOREIGN KEY (idFederation)
		REFERENCES Federation (id)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);


CREATE TABLE Inscription (
	idGymnaste integer,
	idEvenement integer,
	date timestamp NOT NULL,
	CONSTRAINT PK_Inscription PRIMARY KEY (idGymnaste, idEvenement),
	CONSTRAINT FK_Inscription_idGymnaste
		FOREIGN KEY (idGymnaste)
		REFERENCES Gymnaste (idPersonne)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT,
	CONSTRAINT FK_Inscription_idEvenement
		FOREIGN KEY (idEvenement)
		REFERENCES Evenement (id)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);



CREATE VIEW vCoach
AS
	SELECT
		Personne.id,
		Personne.nom,
		Personne.prenom,
		Personne.dateNaissance,
		Personne.idPays,
		Coach.codeDiscipline
	FROM
		Coach
		INNER JOIN Personne ON
			Coach.idPersonne = Personne.id;


CREATE VIEW vGymnaste
AS
	SELECT
		Personne.id,
		Personne.nom,
		Personne.prenom,
		Personne.dateNaissance,
		Personne.idPays,
		Gymnaste.idFederation,
		Gymnaste.idCoach
	FROM
		Gymnaste
		INNER JOIN Personne ON
			Gymnaste.idPersonne = Personne.id;








INSERT INTO Discipline (code, nom) VALUES ('GFA', 'Gymnastics For All');
INSERT INTO Discipline (code, nom) VALUES ('RGI', 'Rhythmic Individual');
INSERT INTO Discipline (code, nom) VALUES ('AER', 'Aerobic Gymnastics');
INSERT INTO Discipline (code, nom) VALUES ('TRA', 'Trampoline');


INSERT INTO Pays (nom) VALUES ('Switzerland');
INSERT INTO Pays (nom) VALUES ('Great Britain');
INSERT INTO Pays (nom) VALUES ('Spain');
INSERT INTO Pays (nom) VALUES ('Canada');
INSERT INTO Pays (nom) VALUES ('Burkina Faso');


INSERT INTO Federation (nom, idPays) VALUES ('FEDERATION SUISSE DE GYMNASTIQUE', (SELECT id FROM Pays WHERE nom = 'Switzerland'));
INSERT INTO Federation (nom, idPays) VALUES ('BRITISH GYMNASTICS', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Federation (nom, idPays) VALUES ('REAL FEDERACION ESPANOLA DE GIMNASIA', (SELECT id FROM Pays WHERE nom = 'Spain'));
INSERT INTO Federation (nom, idPays) VALUES ('CANADIAN GYMNASTICS FEDERATION', (SELECT id FROM Pays WHERE nom = 'Canada'));


INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('VII Copa Interacional Catalunya', '2025-11-23', 50, (SELECT id FROM Federation WHERE nom = 'REAL FEDERACION ESPANOLA DE GIMNASIA'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('FIG World Cup 2023 - GFA - TRA', '2023-09-14', 20, (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('FIG World Cup 2023 - RGI', '2023-09-14', 10, (SELECT id FROM Federation WHERE nom = 'BRITISH GYMNASTICS'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('FIG World Cup 2023 - AER', '2023-09-14', 8, (SELECT id FROM Federation WHERE nom = 'BRITISH GYMNASTICS'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('FIG World Cup 2022', '2022-07-14', 40, (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('Match Junior SUI-FRA-GER 2022', '2022-03-09', 100, (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('FIG World Cup 2021', '2021-03-09', 150, (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('VIII Copa Interacional Catalunya', '2029-11-23', 40, (SELECT id FROM Federation WHERE nom = 'REAL FEDERACION ESPANOLA DE GIMNASIA'));
INSERT INTO Evenement (nom, dateOuverture, fraisInscription, idFederation) VALUES ('TRA RGI World Cup 2022', '2022-03-12', 80, (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'));


-- coachs
-- 1
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Hernandez', 'Luis', '1986-11-08', (SELECT id FROM Pays WHERE nom = 'Spain'));
INSERT INTO Coach (idPersonne, codeDiscipline) VALUES ((SELECT MAX(id) FROM Personne), 'AER');
-- 2
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Gallardo', 'Gabriel', '1976-05-06', (SELECT id FROM Pays WHERE nom = 'Spain'));
INSERT INTO Coach (idPersonne, codeDiscipline) VALUES ((SELECT MAX(id) FROM Personne), 'AER');
-- 3
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Bérubé', 'Vincent', '1993-01-30', (SELECT id FROM Pays WHERE nom = 'Canada'));
INSERT INTO Coach (idPersonne, codeDiscipline) VALUES ((SELECT MAX(id) FROM Personne), 'TRA');
-- 4
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Schmid', 'Hans', '1983-01-30', (SELECT id FROM Pays WHERE nom = 'Switzerland'));
INSERT INTO Coach (idPersonne, codeDiscipline) VALUES ((SELECT MAX(id) FROM Personne), 'RGI');
-- 5
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Traore', 'Aicha', '1995-02-27', (SELECT id FROM Pays WHERE nom = 'Burkina Faso'));
INSERT INTO Coach (idPersonne, codeDiscipline) VALUES ((SELECT MAX(id) FROM Personne), 'RGI');
-- 6
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Hunt', 'Finley', '1994-06-01', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Coach (idPersonne, codeDiscipline) VALUES ((SELECT MAX(id) FROM Personne), 'GFA');


-- gymnastes
-- 7
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Plaisance', 'Isabella', '2004-11-08', (SELECT id FROM Pays WHERE nom = 'Spain'));
INSERT INTO Gymnaste (idPersonne, idFederation) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'REAL FEDERACION ESPANOLA DE GIMNASIA'));
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
-- 8
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Aguas', 'Shaunta', '1986-11-07', (SELECT id FROM Pays WHERE nom = 'Spain'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'REAL FEDERACION ESPANOLA DE GIMNASIA'), 1);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
-- 9
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Lubinsky', 'Al', '2006-11-08', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'CANADIAN GYMNASTICS FEDERATION'));
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'GFA');
-- 10
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Vaillancourt', 'Laurence', '1975-11-08', (SELECT id FROM Pays WHERE nom = 'Canada'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'CANADIAN GYMNASTICS FEDERATION'), 2);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'GFA');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'TRA');
-- 11
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Deeann', 'Hibbert', '2015-11-07', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'CANADIAN GYMNASTICS FEDERATION'), 1);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'TRA');
-- 12
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Defazio', 'Annice', '2004-12-08', (SELECT id FROM Pays WHERE nom = 'Switzerland'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'), 1);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
-- 13
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Burgdorf', 'Providencia', '2004-11-08', (SELECT id FROM Pays WHERE nom = 'Switzerland'));
INSERT INTO Gymnaste (idPersonne, idFederation) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'));
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
-- 14
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Weinberger', 'Ozie', '2004-06-08', (SELECT id FROM Pays WHERE nom = 'Switzerland'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'), 5);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'GFA');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'TRA');
-- 15
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Nygaard', 'Preston', '2002-10-08', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'BRITISH GYMNASTICS'), 5);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
-- 16
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Harvell', 'Harold', '2003-11-08', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'BRITISH GYMNASTICS'), 6);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'GFA');
-- 17
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Hutson', 'Dwight', '1981-03-04', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'BRITISH GYMNASTICS'), 5);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
-- 18
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Lovelace', 'Gena', '2006-11-14', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'BRITISH GYMNASTICS'));
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
-- 19
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Halls', 'Krysta', '1997-03-03', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'BRITISH GYMNASTICS'), 6);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'TRA');
-- 20
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Hinrichs', 'Shiela', '2005-05-30', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'REAL FEDERACION ESPANOLA DE GIMNASIA'));
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'GFA');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'TRA');
-- 21
INSERT INTO Personne(nom, prenom, dateNaissance, idPays) VALUES ('Bender', 'Leeann', '2006-03-28', (SELECT id FROM Pays WHERE nom = 'Great Britain'));
INSERT INTO Gymnaste (idPersonne, idFederation, idCoach) VALUES ((SELECT MAX(id) FROM Personne), (SELECT id FROM Federation WHERE nom = 'FEDERATION SUISSE DE GYMNASTIQUE'), 6);
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'AER');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'RGI');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'TRA');
INSERT INTO Gymnaste_Discipline (idGymnaste, codeDiscipline) VALUES ((SELECT MAX(idPersonne) FROM Gymnaste), 'GFA');


INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (7, 1, '2023-10-24');

INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (9, 2, '2021-10-24');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (19, 2, '2022-01-24');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (21, 2, '2022-03-22');

INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (8, 4, '2022-12-24');

INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (7, 5, '2022-05-11');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (8, 5, '2022-05-11');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (9, 5, '2022-05-12');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (10, 5, '2022-05-13');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (11, 5, '2022-05-14');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (12, 5, '2022-05-15');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (13, 5, '2022-05-16');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (14, 5, '2022-05-17');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (15, 5, '2022-05-18');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (17, 5, '2022-05-20');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (18, 5, '2022-05-24');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (19, 5, '2022-05-22');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (20, 5, '2022-05-23');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (21, 5, '2022-05-24');

INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (21, 7, '2021-03-10');

INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (7, 8, '2023-10-21');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (11, 8, '2023-10-24');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (12, 8, '2023-11-01');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (20, 8, '2023-11-11');

INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (13, 9, '2022-04-14');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (14, 9, '2022-03-12');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (8, 9, '2021-10-24');
INSERT INTO Inscription (idGymnaste, idEvenement, date) VALUES (9, 9, '2021-12-01');

