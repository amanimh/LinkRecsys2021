
#### Installation de Sphinx:

```
pip install sphinx 
```
.
.
.




#### 1-  Configuration Sphinx :

##### 1.1- Création d'un nouveau projet de documentation

* ouvrir le terminal ou cmd et changer le chemin actuel vers celui du dossier projet 
 * executer la commande :
 ```   
  sphinx-quickstart ("yes" pour la premiere question)
 ```
 
 Vous devez voir ce message qui s'affiche sur le terminal :

```   
      Bienvenue dans le kit de démarrage rapide de Sphinx 3.1.2.

    Please enter values for the following settings (just press Enter to
    accept a default value, if one is given in brackets).

    Selected root path: .

    You have two options for placing the build directory for Sphinx output.
    Either, you use a directory "_build" within the root path, or you separate
    "source" and "build" directories within the root path.
    > Séparer les répertoires build et source (y/n) [n]: y

    The project name will occur in several places in the built documentation.
    > Nom du projet: Example Sphinx Project
    > Nom(s) de l'auteur: me
    > version du projet []:

    If the documents are to be written in a language other than English,
    you can select a language here by its language code. Sphinx will then
    translate text that it generates into that language.

    For a list of supported codes, see
    https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language.
    > Langue du projet [en]:

    [...]
```
   * retrouvez avec un dossier source/ qui contiendra votre documentation, et deux fichiers :
       * Makefile pour générer la doc depuis Linux, MacOS,...
       * make.bat pour générer la doc depuis Windows.
  
  
  
 ##### 1.2- Génération de la documentation
* Pour générer la documentation en HTML:
  
         * sphinx-apidoc -o source/rst/ ../app/base
         * make clean
         * make html
         
 * Une fois la documentation générée, vous retrouverez le résultat dans le dossier build/html/.
   - Vous pouvez à présent ouvrir index.html dans votre navigateur et voir le résultat.

* Pour générer la documentation en PDF:

        * sphinx-build -b rinoh source _build/rinoh
  
 * Une fois la doc générée, vous retrouverez le résultat dans le dossier _build/rinoh/….