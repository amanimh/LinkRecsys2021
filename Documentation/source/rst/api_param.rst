Paramétres de L'API LinkedIn
=============================

Table Profil
-----------------

              *  **profile_id** -  identifiant de profil

              * **firstName** -   prénom du profil LinkedIn.

              * **lastName** -    nom du profil

              * **birthDate** -   date de naissance du profil

              * **phone_numbers** - numéro de téléphone de profil

              * **summary** - une description courte et claire qui donne une idée sur le profil

              * **geoCountryName** -  Nom du pays


              * **email_address** -   adresse  email

              * **followersCount** -  nombre d'abonnés

              * **headline** - Titre de profil

              * **Volunteer** - vrai si le propriétaire

              * **Publications** - vrai si le propriétaire du profil a participer à la vie associative

                                 Faux si non

              * **honors** -  vrai si le propriétaire du profil a pris des honneurs

                                 Faux si non

              * **student** -  vrai si le propriétaire du profil est un étudiant

                                 Faux si non

Table Langues
-----------------

              * **profile_id** -    identifiant de profil

              * **name_langue** -   langue

              * **proficiency** -   niveau de compétence


Table Societe
-----------------

              * **companyUrn** -  identifiant de l'entreprise

              * **companyName** -   nom de l'entreprise

              * **geoLocationName** -    emplacement géographique

              * **industries** -    secteur d'activité de l'entreprise

              * **staffCount** -    nombre d'employés

              * **companyPageUrl** -    adresse éléctronique

              * **companyType** -    type de l'entreprise

              * **phone** -    numéro du télephone

              * **profile_id** -    identifiant de profil


Table Skills
-----------------

              * **standardizedSkillUrn** -  identifiant de compétence

              * **name_skill** -   nom de la compétence

              * **profile_id** -    identifiant de profil

Table Formation
-----------------

              * **entityUrn** -  identifiant de l'école

              * **schoolName** -   nom de l'école

              * **degreeName** -    niveau d'études

              * **fieldOfStudy** -    domaine d'étude


              * **Period** -    Période d'étude

              * **profile_id** -    identifiant de profil

Table Experience
-----------------

              * **entityUrn** -  identifiant de l'éxperience

              * **companyUrn** -   identifiant de l'entreprise

              * **Period** -    Période de l'éxperience

              * **title** -  Poste occupé

              * **profile_id** -    identifiant de profil

Table Certifications
----------------------


              * **authority** -  L'organisation qui agit pour valider la certification

              * **name_certif** -   nom de certification

              * **Period** -    Période de validité

              * **profile_id** -    identifiant de profil


Paramétres ConfigParser
=============================
   * **[param]**

      * **usr**  (str) – Nom d’utilisateur du compte LinkedIn.

      * **pw**  (str) - Mot de passe du compte LinkedIn.








