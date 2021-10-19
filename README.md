# Linkedin Talent Recommandation System


### Informations génerales
***
Le projet : 

La Conception et mise en place d'une application permettant la récupération et le traitement des informations sur un pool de candidats potentiels. En spécifiant des critères ou des mots clés, en premier lieu , l'application fait une recherche exhaustive sur les candidats potentiels disponibles sur le site Linkedin. Nous avons ainsi la possibilité d'archiver et de mettre à jours ces données et les utiliser dans un système de recommandation.

Ce système de recommandation aura pour objectif l'identification de profils pertinents, en précisant au départ un ensemble de critères .




### Installation des prérequis

* Instructions d’installation et de configuration.


#### 1- Configurez l’environnement virtuel: 

Dans le terminal, vous devez aller dans le repertoire principal du projet. Vérifiez bien que vous etes dans le bon emplacement avant de lancer ces étapes. 
Exécuter les commandes ci-dessous :

```

python3 -m venv Linkedin_rec
source Linkedin_rec/bin/activate

```
Installation des bibliothèques nécessaires :

```
pip install -r requirements.txt

```

#### 2-  Renseignez les paramètres de Connexion Linkedin :

 Remplir le fichier "config.ini" avec les paramétres username & password du compte Linkedin, avant de lancer l'application.

```
[param]
usr =
pw =
```
#### 3- Lancez l’application:


##### Définissez la variable d'environnement FLASK_APP
$ (Unix/Mac) export FLASK_APP=run.py

$ (Windows) set FLASK_APP=run.py

$ (Powershell) $env:FLASK_APP = ".\run.py"

##### Démarrez l'application 

$ #--host=0.0.0.0 - exposer l'application sur toutes les interfaces  (default 127.0.0.1)
$ # --port=5000    - spécifier le port de l'application (default 5000)  
$ flask run --host=0.0.0.0 --port=5000
##### Accédez au tableau de bord dans le navigateur: http://127.0.0.1:5000/


