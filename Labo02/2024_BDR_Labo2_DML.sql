INSERT INTO Client (pseudo, dateNaissance, adresseFacturation, email) VALUES ('YoLo666', '2010-12-12', 'Rte du lac 36, 1400 Yverdon-les-Bains', 'YoLo666@gmail.com');
INSERT INTO Client (pseudo, dateNaissance, adresseFacturation, email) VALUES ('HeadShot2012', '2012-11-04', 'Rte du Jorat 18, 1820 Montreux', 'HeadShot2012@gmail.com');

INSERT INTO Fabricant (nom) VALUES ('Nintendo');
INSERT INTO Fabricant (nom) VALUES ('Sony');
INSERT INTO Fabricant (nom) VALUES ('Microsoft');

INSERT INTO Console (nom, anneeParution, nomFabricant) VALUES ('Wii', 2006, 'Nintendo');
INSERT INTO Console (nom, anneeParution, nomFabricant) VALUES ('Switch', 2017, 'Nintendo');
INSERT INTO Console (nom, anneeParution, nomFabricant) VALUES ('PS3', 2006, 'Sony');
INSERT INTO Console (nom, anneeParution, nomFabricant) VALUES ('PS4', 2013, 'Sony');
INSERT INTO Console (nom, anneeParution, nomFabricant) VALUES ('Xbox One', 2013, 'Microsoft');

INSERT INTO Editeur (nom, siegeSocial) VALUES ('Devolver Digital', 'Austin, États-Unis');
INSERT INTO Editeur (nom, siegeSocial) VALUES ('Blizzard Entertainment', 'Irvine, États-Unis');
INSERT INTO Editeur (nom, siegeSocial) VALUES ('Square Enix', 'Tokyo, Drapeau du Japon Japon');
INSERT INTO Editeur (nom, siegeSocial) VALUES ('Sony Interactive Entertainment', 'San Mateo, États-Unis');

INSERT INTO Genre (nom) VALUES ('hack''n''slash');
INSERT INTO Genre (nom) VALUES ('Action-RPG');
INSERT INTO Genre (nom) VALUES ('Shooter');

INSERT INTO Article (nom, description, dateSortie, prix) VALUES ('Hotline Miami', 'L''intrigue se déroule en 1989 à Miami. Un personnage inconnu, mais que les fans nomment Jacket en référence à son blouson, reçoit des appels qui lui ordonnent de commettre des crimes contre la mafia russe locale.', '2013-03-18', 20);
INSERT INTO JeuVideo (idArticle, ageMinimum, idEditeur) VALUES (1, 16, 1);
INSERT INTO JeuVideo_Genre (idJeuVideo, nomGenre) VALUES (1, 'Shooter');
INSERT INTO Article (nom, description, dateSortie, prix) VALUES ('Nier:Automata', 'Se déroulant au cœur d''une guerre par procuration entre les machines créées par les envahisseurs d''un autre monde et les restes de l''humanité, l''histoire suit les batailles de l''androïde de combat 2B, son compagnon 9S, et le prototype obsolète A2', '2017-02-23', 60);
INSERT INTO JeuVideo (idArticle, ageMinimum, idEditeur) VALUES (2, 18, 3); 
INSERT INTO Article (nom, description, dateSortie, prix) VALUES ('Diabl0 IV', 'le quatrième épisode principal de la série Diablo, faisant suite à Diablo III sorti en 2012', '2023-06-06', 70);
INSERT INTO JeuVideo (idArticle, ageMinimum, idEditeur) VALUES (3, 18, 2); 
INSERT INTO JeuVideo_Genre (idJeuVideo, nomGenre) VALUES (3, 'hack''n''slash');
INSERT INTO Article (nom, description, dateSortie, prix) VALUES ('Diablo IV: La vaisselle de la haine', 'Tout est dans le titre', '2028-10-08', 40);
INSERT INTO DLC (idArticle, necessiteJeuDeBase, idJeuVideo) VALUES (4, TRUE, 3);
INSERT INTO Article (nom, description, dateSortie, prix) VALUES ('Demon''s Souls', 'Le joueur prend le contrôle d''un héros chargé de terrasser les démons et ramener la paix à Bolétaria', '2009-02-05', 10);
INSERT INTO JeuVideo (idArticle, ageMinimum, idEditeur) VALUES (5, 18, 1);
INSERT INTO JeuVideo_Genre (idJeuVideo, nomGenre) VALUES (5, 'Action-RPG');

INSERT INTO Article_Console (idArticle, nomConsole) VALUES (1, 'PS4');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (2, 'Switch');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (2, 'PS4');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (2, 'Xbox One');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (3, 'PS4');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (3, 'Xbox One');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (4, 'PS4');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (4, 'Xbox One');
INSERT INTO Article_Console (idArticle, nomConsole) VALUES (5, 'PS3');

INSERT INTO Client_Article (pseudoClient, idArticle, dateAchat) VALUES ('YoLo666', 2, '2017-02-23');
INSERT INTO Client_Article (pseudoClient, idArticle, dateAchat) VALUES ('YoLo666', 3, '2024-01-01');
INSERT INTO Client_Article (pseudoClient, idArticle, dateAchat) VALUES ('HeadShot2012', 1, '2014-06-06');