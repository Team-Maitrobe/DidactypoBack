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
