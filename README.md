# Hosts-Sweet-Hosts
Outil de mise à jour des Hosts dans le fichier Hosts local.

Une application graphique simple pour gérer automatiquement votre fichier hosts à partir d'une source en ligne.

## Fonctionnalités
- Téléchargement automatique d'un fichier hosts depuis une URL HTTPS
- Mise à jour programmée avec minuteur configurable
- Sauvegarde automatique du fichier hosts avant modification
- Vidage du cache DNS après mise à jour
- Interface utilisateur intuitive avec thème sombre
- Configuration persistante

## Prérequis
- Python 3.6 ou supérieur (ou utiliser l'executable compilé)
- Bibliothèques requises : requests, tkinter
- Droits administrateur (nécessaires pour modifier le fichier hosts)

## Utilisation
- Configurez l'URL source du fichier hosts dans les paramètres
- Définissez l'intervalle de rafraîchissement souhaité
- Cliquez sur "GO" pour lancer la mise à jour
- Activez l'option "Auto Refresh" pour que l'application démarre automatiquement les mises à jour

## Compatibilité
- Windows : Entièrement compatible
- macOS : Compatible
(nécessite des droits administrateur)

L'application nécessite des droits administrateur pour modifier le fichier hosts sur macOS.
Assurez-vous de l'exécuter avec sudo ou via une application compilée avec les droits appropriés.

## Hosts-Sweet-Hosts en service (Windows)

Si vous souhaitez utiliser ce programme en service sous windows, installez-le à l'aide de NSSM https://nssm.cc/download, c'est simple et rapide.

-Executez nssm install nomdevotreservice

-Suivez les instructions en pointant l'executable Hosts-Sweet-Hosts.exe

Je n'ai pas encore compilé et testé sur MacOS, je ne peux pas vous donner une méthode. Dès que les test sur MacOS seront effectués, j'etudierais l'integration native de la mise du processus en service (windows et mac).
