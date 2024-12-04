# Rapport BDR labo03
## Partie 1
1. Les frais moyens d'inscription des événements organisés par la fédération 'BRITISH
GYMNASTICS'.
```sql
SELECT 
    AVG(Evenement.fraisInscription) AS frais_moyens
FROM 
    Evenement
JOIN 
    Federation ON Evenement.idFederation = Federation.id
WHERE 
    Federation.nom = 'BRITISH GYMNASTICS';
```
2. Les gymnastes qui pratiquent la discipline dont leur entraineur est le spécialiste et qui
sont originaires du même pays.
```sql
SELECT g.idPersonne AS idGymnaste, pg.nom, pg.prenom
FROM Gymnaste g
JOIN Coach c ON g.idCoach = c.idPersonne
JOIN Personne pg ON g.idPersonne = pg.id
JOIN Personne pc ON c.idPersonne = pc.id
JOIN Gymnaste_Discipline gd ON g.idPersonne = gd.idGymnaste
WHERE gd.codeDiscipline = c.codeDiscipline
    AND pg.idPays = pc.idPays
```
3. Les coachs nés entre 1981 et 1996 (années comprises) qui entrainent au moins un
gymnaste plus âgé qu'eux.
```sql
SELECT DISTINCT c.idPersonne AS idCoach, pc.nom AS nomCoach, pc.prenom AS prenomCoach
FROM Coach c
JOIN Gymnaste g ON g.idCoach = c.idPersonne
JOIN Personne pg ON g.idPersonne = pg.id
JOIN Personne pc ON c.idPersonne = pc.id
WHERE pc.dateNaissance BETWEEN '1981-01-01' AND '1996-12-31'
    AND EXISTS (SELECT g.idPersonne FROM Gymnaste WHERE pc.dateNaissance > pg.dateNaissance)
```
4. Les coachs qui entrainent plus de 2 gymnastes qui se sont inscrits à au moins 1
événement.
```sql
SELECT c.idPersonne AS idCoach, pc.nom AS nomCoach, pc.prenom AS prenomCoach, COUNT(DISTINCT g.idPersonne) AS nombreGymnastes
FROM Coach c
JOIN Gymnaste g ON g.idCoach = c.idPersonne
JOIN Personne pc ON c.idPersonne = pc.id
JOIN Inscription i ON g.idPersonne = i.idGymnaste
GROUP BY c.idPersonne, pc.nom, pc.prenom
HAVING COUNT(DISTINCT g.idPersonne) > 2;
```
5. Pour les gymnastes ayant participé à au moins 2 événements, indiquer l’écart entre les
frais d’inscription les moins élevés et les plus élevés payés. Classer les résultats par ordre
alphabétique croissant du nom, puis du prénom des gymnastes.
```sql
SELECT g.idPersonne AS idGymnaste, p.nom AS nomGymnaste, p.prenom AS prenomGymnaste, MAX(e.fraisInscription) - MIN(e.fraisInscription) AS differenceFrais
FROM Gymnaste g
JOIN Inscription i ON g.idPersonne = i.idgymnaste 
JOIN Personne p ON g.idPersonne = p.id
JOIN evenement e ON i.idevenement = e.id
GROUP BY g.idPersonne, p.nom, p.prenom
HAVING COUNT(DISTINCT i.idEvenement) >= 2
ORDER BY p.nom ASC, p.prenom ASC;
```
6. Indiquer (gymnaste + événement avec sa date d’ouverture + nombre de jours de retard)
toutes les inscriptions faites après la date d’ouverture d'un événement.
```sql
SELECT g.idPersonne AS idGymnaste, 
       p.nom AS nomGymnaste, 
       p.prenom AS prenomGymnaste, 
       e.nom AS nomEvenement, 
       TO_CHAR(e.dateOuverture, 'DD.MM.YYYY') AS dateEvenement,
       TO_CHAR(i.date, 'DD.MM.YYYY') AS dateInscription,
       (i.date - e.dateOuverture) AS joursDifference
FROM Gymnaste g
JOIN Inscription i ON g.idPersonne = i.idgymnaste
JOIN Personne p ON g.idPersonne = p.id
JOIN evenement e ON i.idevenement = e.id
WHERE i.date > e.dateOuverture;
```
7. Par événement, lister tous les gymnastes inscrits en les classant par date d'inscription à
l'événement (de la plus ancienne à la plus récente).
```sql
SELECT e.nom AS nomEvenement, 
       TO_CHAR(e.dateOuverture, 'DD.MM.YYYY') AS dateEvenement,
       p.nom AS nomGymnaste, 
       p.prenom AS prenomGymnaste,
       TO_CHAR(i.date, 'DD.MM.YYYY') AS dateInscription
FROM evenement e
JOIN inscription i ON e.id = i.idevenement
JOIN gymnaste g ON i.idgymnaste = g.idPersonne
JOIN personne p ON g.idPersonne = p.id
ORDER BY e.nom, i.date, p.nom, p.prenom;
```
8. En partant du principe que les coachs payent les frais d'inscription aux événements de
leurs gymnastes qui y participent en tant que juniors (moins de 16 ans au début de
l'événement), classer les coachs par le montant total des frais d’inscriptions qu'ils ont payé
(ordre décroissant) puis par ordre alphabétique de leur nom.
```sql
SELECT pc.nom AS nomCoach, 
       pc.prenom AS prenomCoach,
       SUM(e.fraisInscription) AS totalPrix
FROM Coach c
JOIN Gymnaste g ON g.idCoach = c.idPersonne
JOIN Inscription i ON g.idPersonne = i.idgymnaste
JOIN evenement e ON i.idevenement = e.id
JOIN Personne pc ON c.idPersonne = pc.id
JOIN Personne p ON g.idPersonne = p.id
WHERE EXTRACT(YEAR FROM AGE(e.dateOuverture, p.dateNaissance)) < 16
GROUP BY pc.nom, pc.prenom
ORDER BY totalPrix desc, pc.nom ASC, pc.prenom ASC;
```
9. Par fédération qui a au moins 1 membre, indiquer le nombre de membres qui sont
originaires de son pays et le nombre qui sont originaires d'un autre pays.
```sql
-- TODO: finir
SELECT f.nom AS federation,
	   pf.nom as paysFederation,
       p.nom AS gymnasteNom,
       p.prenom AS gymnastePrenom,
       pp.nom AS paysGymnaste
FROM Federation f
JOIN Gymnaste g ON f.id = g.idFederation
JOIN Personne p ON g.idPersonne = p.id
JOIN Pays pp ON p.idPays = pp.id
JOIN Pays pf ON f.idPays = pf.id
ORDER BY f.nom, p.nom, p.prenom;
```
10. Pour chaque gymnaste, indiquer le nombre d'événements auxquels il est inscrit et qui
n'ont pas encore commencé.
```sql

```
11. Pour l’événement 'TRA RGI World Cup 2022', lister toutes les inscriptions (gymnastes +
frais réels).
Pour calculer les frais réels, on prend les frais d’inscription en tenant compte de 2 règles :
- On les double pour toute inscription hors délai (après l’ouverture de l’événement).
- Les gymnastes membres de la fédération qui organise l’événement ont un rabais de
20%.
```sql

```
12. Les fédérations (triées par leur nom) avec leurs événements ainsi que l'écart entre les frais
d'inscription à l'événement et les frais d'inscription moyens aux événements de la
fédération.
```sql

```
13. Les gymnastes qui ne se sont inscrits qu’à des événements organisés par leur fédération
```sql

```