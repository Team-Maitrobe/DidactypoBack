INSERT INTO DIDACTYPO.COURS (titre_cours,description_cours,duree_cours,difficulte_cours) VALUES ("Premiers pas","Le premier cours, pour apprendre
les bases de la didactypo, notament la posture et le placement des doigts",20,4);

INSERT INTO DIDACTYPO.SOUS_COURS (id_cours_parent,titre_sous_cours,contenu_cours,chemin_img_sous_cours) VALUES (1,"La posture",
"Salut ! Content de te voir !\n
Dans ce cours, nous allons te présenter les bases de l’écriture à dix doigts.\n
Tout d’abord, mets-toi dans une bonne posture pour travailler : dos droit et pieds bien à plat sur le sol.","https://media.istockphoto.com/id/1352439563/fr/vectoriel/femme-travaille-sur-ordinateur-à-table-dans-la-bonne-position.jpg?s=612x612&w=0&k=20&c=beic8-syTGKEGdF3kciRkULrPfqLMT36M4eggn5KQQE=");
INSERT INTO DIDACTYPO.SOUS_COURS (id_cours_parent,contenu_cours) VALUES (1,"Super, reste dans cette position pour le reste du cours. 
(Si c’est trop difficile, fais une petite pause.)\n
Il est très important de garder cette posture pour ta santé et pour améliorer ton efficacité devant l’écran.");
INSERT INTO DIDACTYPO.SOUS_COURS (id_cours_parent,titre_sous_cours,contenu_cours,chemin_img_sous_cours) VALUES (1,"Le placement des doigts",
"Maintenant, il est temps de mettre tes mains en bonne position. Pose tes index sur les touches F et J ; elles ont de petites bosses pour t’aider ;)\n
Les deux pouces se reposent sur la barre d’espace (le bouton long en bas).\n
Place les autres doigts sur les touches Q, S, D, et K, L, M pour te retrouver avec tes 10 doigts alignés.","https://www.pentakonix.fr/wp-content/uploads/2022/11/taper-avec-les-dix-doigts.jpg");
INSERT INTO DIDACTYPO.SOUS_COURS (id_cours_parent,contenu_cours,chemin_img_sous_cours) VALUES (1,"Bon travail ! L’étape la plus dure est terminée.\n
Dans la prochaine étape, on va jouer au piano. Ou au moins, faire semblant.\n
Essaye de monter tes poignets, comme si tu voulais faire une petite table avec tes mains pour qu’elles ne touchent pas la table, comme au piano !",
"https://cdn-dhfgh.nitrocdn.com/uZLtwkdbfkSbTAIEdKvdekQfaGOIVgLx/assets/images/optimized/rev-24e28f1/wp-content/uploads/2021/10/MyPianoPop_position_doigts_main_piano_main-5-1.png");
INSERT INTO DIDACTYPO.SOUS_COURS (id_cours_parent,titre_sous_cours,contenu_cours) VALUES (1,"Exercice","Maintenant, nous allons faire faire un petit exercice pour que tu puisses t’entraîner à bien écrire.");
