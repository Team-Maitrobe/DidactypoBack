-- Insérer le cours principal
INSERT INTO COURS (titre_cours, description_cours, duree_cours, difficulte_cours) VALUES 
('Premiers pas', 'Le premier cours, pour apprendre les bases de la didactypo, notamment la posture et le placement des doigts', 20, 4);

-- Insérer les sous-cours avec un identifiant unique pour chaque entrée
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES 
(1, 1, 'La posture', 'Salut ! Content de te voir !\nDans ce cours, nous allons te présenter les bases de l''écriture à dix doigts.\nTout d''abord, mets-toi dans une bonne posture pour travailler : dos droit et pieds bien à plat sur le sol.', 'https://media.istockphoto.com/id/1352439563/fr/vectoriel/femme-travaille-sur-ordinateur-à-table-dans-la-bonne-position.jpg?s=612x612&w=0&k=20&c=beic8-syTGKEGdF3kciRkULrPfqLMT36M4eggn5KQQE=');

INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, contenu_cours) VALUES 
(1, 2, 'Super, reste dans cette position pour le reste du cours. (Si c''est trop difficile, fais une petite pause.)\nIl est très important de garder cette posture pour ta santé et pour améliorer ton efficacité devant l''écran.');

INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES 
(1, 3, 'Le placement des doigts', 'Maintenant, il est temps de mettre tes mains en bonne position. Pose tes index sur les touches F et J ; elles ont de petites bosses pour t''aider ;)\nLes deux pouces se reposent sur la barre d’espace (le bouton long en bas).\nPlace les autres doigts sur les touches Q, S, D, et K, L, M pour te retrouver avec tes 10 doigts alignés.', 'https://www.pentakonix.fr/wp-content/uploads/2022/11/taper-avec-les-dix-doigts.jpg');

INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES 
(1, 4, 'Bon travail ! L''étape la plus dure est terminée.\nDans la prochaine étape, on va jouer au piano. Ou au moins, faire semblant.\nEssaye de monter tes poignets, comme si tu voulais faire une petite table avec tes mains pour qu''elles ne touchent pas la table, comme au piano !', 'https://cdn-dhfgh.nitrocdn.com/uZLtwkdbfkSbTAIEdKvdekQfaGOIVgLx/assets/images/optimized/rev-24e28f1/wp-content/uploads/2021/10/MyPianoPop_position_doigts_main_piano_main-5-1.png');

INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours) VALUES 
(1, 5, 'Exercice', 'Maintenant, nous allons faire un petit exercice pour que tu puisses t''entraîner à bien écrire.');

INSERT INTO COURS (titre_cours, description_cours, duree_cours, difficulte_cours) VALUES 
('Le placement des doigts', 'Le deuxième cours, dans lequel on précise quelles touches l''utilisateur doit utiliser pour chaque doigt', 30, 8);
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours) VALUES
(2,1,'le placement des doigts','Salut, c''est un grand plaisir de te revoir !\n Je savais que tu continuerais ton aventure dans la dactylographie (l''art de taper au clavier).
\n Maintenant, on va voir le placement des doigts plus en détail, donc quel doigt doit appuyer sur quelle touche du clavier.
\n On va commencer par le petit doigt gauche et continuer de la gauche vers la droite.');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,2,'Le petit doigt gauche','Le petit doigt gauche a un rôle très important. Il doit saisir la touche Maj quand on veut écrire des lettres majuscules. De plus, il s''occupe aussi des touches a, q, w, 1, 2 et des touches tout à gauche du clavier.
Il y a juste un problème : c''est qu''on n''utilise jamais ce doigt pour écrire au clavier. Il faudra donc s''entraîner davantage sur ce doigt et même éventuellement le muscler.','https://fr.pinterest.com/pin/azerty-keyboard--492722015487127908/');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,3,'L''annulaire gauche','L''annulaire gauche a un rôle plus simple que celui d''avant. Il s''occupe des touches z, s, x et 3.
Mais lui aussi n''a pas été vraiment utilisé, donc on se retrouve un peu avec le même problème que le petit doigt. Alors, il faut prendre plus de temps pour l''entraîner.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,4,'Le majeur gauche','Le majeur gauche, maintenant, on a des doigts avec un job simple.Il s''occupe des touches e, d, c et 4.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,5,'L''index gauche','L''index gauche, c''est un des doigts qu''on utilise le plus, mais il a beaucoup de touches à couvrir.Il s''occupe des touches r, f, v, t, g, b, 5 et 6.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,6,'Les pouces','Ici, on peut regrouper les deux pouces, car ils traitent seulement trois touches: La touche espace (leur position initiale) et les deux touches Alt.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,7,'L''index droit','L''index droit, comme le gauche, s''occupe de beaucoup de touches: y, h, n, u, j, 7, 8, ?.
Comme on peut le voir, les doigts de la main droite s''occupent aussi des caractères spéciaux comme le point d''interrogation ou d''exclamation.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,8,'Le majeur droit','Le majeur droit s''occupe des touches i, k, 9 et du point.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,9,'L''annulaire droit','L''annulaire droit s''occupe des touches o, l, 0 et du /.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(2,10,'Le petit doigt droit','Le petit doigt droit, le doigt le plus difficile. Il s''occupe des touches p, m et de toutes les touches restantes à droite. Cela fait beaucoup, mais c''est possible. Alors, il faut s''entraîner beaucoup sur ce doigt.','https://i.postimg.cc/4NNWGfp0/Azerty-keyboard.jpg');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, contenu_cours) VALUES
(2,11,'Bon travail, je sais que c''était long, mais tu peux vraiment être fier de ton travail !
Mais malheureusement, le vrai travail commence à partir de maintenant. La dactylographie est majoritairement de la pratique. Dans les cours qui suivent, je vais t''accompagner dans cette aventure pour maîtriser la dactylographie.');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours) VALUES
(2,12,'Exercice','Maintenant tu peux faire un petit exercice global sur toutes les touches');


INSERT INTO COURS (titre_cours, description_cours, duree_cours, difficulte_cours) VALUES 
('Un départ dans la pratique','cours pour lancer la pratique réguliaire sur les exercices',10,2);
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours) VALUES
(3,1,'Un départ dans la pratique','Salut !
Il est temps de rentrer dans le cœur de la dactylographie : la pratique, pour appliquer tout ce qu''on a vu ensemble dans les cours précédents.
Tout d''abord, on va s''entraîner sur le placement des doigts avec des petits exercices simples pour s''entraîner sur chaque doigt. Pour cela, tu peux aller dans la section exercices.
Si tu les as tous faits, passe à la page suivante.');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, contenu_cours, chemin_img_sous_cours) VALUES
(3,2,'Voilà, bon travail.
Comme tu l''as sûrement vu, c''est pénible de s''obliger à utiliser cette manière de taper. Il est tout à fait normal que ta vitesse ait fortement diminué, mais c''est seulement une question de pratique.
Le plus important, c''est de continuer et de ne pas se démotiver!','https://cdn.creazilla.com/cliparts/60301/thumb-up-emoji-clipart-xl.png');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, contenu_cours) VALUES
(3,3,'Le meilleur que tu puisses faire maintenant, c''est de répéter ce cours pendant une semaine pour ancrer le placement des doigts dans ta mémoire musculaire. Plus tu pratiques, mieux tu vas devenir, et dans quelques semaines, tu vas être beaucoup plus rapide qu''au début. En moyenne, la WPM (mots tapés par minute au clavier) est de 45 pour une personne, mais avec la bonne méthode que tu es en train d''apprendre, elle peut monter jusqu''à 100 !');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, contenu_cours) VALUES
(3,4,'Bon, le plus important, c''est de rester motivé. Bonne chance et à demain !');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours) VALUES
(3,5,'Exercice','Petit lien pour accéder à l''exercice');


INSERT INTO COURS (titre_cours, description_cours, duree_cours, difficulte_cours) VALUES 
('C''est le temps pour le mode compétition','Dernier cours, qui mène l''utilisateur sur le mode compétition pour s''améliorer en autonomie',10,4);
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, titre_sous_cours, contenu_cours) VALUES
(4,1,'C''est le temps pour le mode compétition','Salut, Salut !
Maintenant, tu es prêt à te lancer dans le mode compétition !
Bravo !
Après le travail sur ta précision et sur la mémoire musculaire de la dernière semaine, tu peux commencer à améliorer ta vitesse dans le mode compétition.
C''est tout simple : comme dans les exercices, tu dois écrire une phrase le plus rapidement possible. Mais n''oublie pas d''utiliser tes 10 doigts. Je comprends que ça peut devenir frustrant et que tu vas sûrement avoir fortement envie de repasser sur seulement 4 doigts, mais n''oublie jamais, après un certain temps, tu vas maîtriser l''écriture à 10 doigts et ainsi le top 1 du leaderboard va être un jeu d''enfant.');
INSERT INTO SOUSCOURS (id_cours_parent, id_sous_cours, contenu_cours,chemin_img_sous_cours) VALUES
(4,2,'Si tu penses avoir encore des petits problèmes sur ta précision, n''hésite pas à repasser sur les exercices ou à jouer le mode compétition en ignorant le timer.
Ainsi, tu as réussi tout ce que je peux t''apprendre. C''est à toi de devenir le champion de la dactylographie.','https://img.freepik.com/vecteurs-premium/joueur-football-tenant-celebration-du-champion-gagnant-du-trophee-illustration-dessin-anime_201904-397.jpg');
