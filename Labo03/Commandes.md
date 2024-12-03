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

```
4. Les coachs qui entrainent plus de 2 gymnastes qui se sont inscrits à au moins 1
événement.
```sql

```
5. Pour les gymnastes ayant participé à au moins 2 événements, indiquer l’écart entre les
frais d’inscription les moins élevés et les plus élevés payés. Classer les résultats par ordre
alphabétique croissant du nom, puis du prénom des gymnastes.
```sql

```
6. Indiquer (gymnaste + événement avec sa date d’ouverture + nombre de jours de retard)
toutes les inscriptions faites après la date d’ouverture d'un événement.
```sql

```
7. Par événement, lister tous les gymnastes inscrits en les classant par date d'inscription à
l'événement (de la plus ancienne à la plus récente).
```sql

```
8. En partant du principe que les coachs payent les frais d'inscription aux événements de
leurs gymnastes qui y participent en tant que juniors (moins de 16 ans au début de
l'événement), classer les coachs par le montant total des frais d’inscriptions qu'ils ont payé
(ordre décroissant) puis par ordre alphabétique de leur nom.
```sql

```
9. Par fédération qui a au moins 1 membre, indiquer le nombre de membres qui sont
originaires de son pays et le nombre qui sont originaires d'un autre pays.
```sql

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