import pandas as pd
from datetime import datetime ,date
from numpy.distutils.fcompiler import none
from sqlalchemy import create_engine
from linkedin_api import Linkedin
from configparser import ConfigParser
from flask_wtf import FlaskForm
import os
import sqlite3
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from functools import reduce
import pickle
from sqlalchemy import create_engine

# Loading config params*
configpar= ConfigParser()
path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
configpar.read(os.path.join(path, 'config.ini'))



class Scraping(FlaskForm):
    """
    Classe pour scrapper nettoyer et stocker les profils Linkedin
    """
    def __init__(self):
        pass

    def scraping_F(self, motcle):
        """
        scraping_F permet de récuperer tout les profils nécessaires pour alimenter notre BD
        en utilisant l'api Linkedin  en spécifiant un domaine bien déterminé comme entrée


        :Parameters:  **motcle (str)** - pour spécifier la description du profil à chercher.

                      **api (str)** - permet d'accéder à l'API LinkedIn

        :Return: les tables Profil,Langues,Skills,Sociéte,Formation,Expérience et Certifications remplies dans la BD

        :Return type: table sql
        """

        #Connection sur la bd Sqlite
        engine = create_engine('sqlite:///LinkedInDB', echo=False)
        #se connecter à l'API avec le mail et le mot de passe
        api = Linkedin(configpar['param']['usr'], configpar['param']['pw'])
        #recuperation des profils selon le mot cle
        self.people = api.search_people(keywords=motcle)
        print(self.people)
        #Creation des dataframes vide
        df_Profil = pd.DataFrame(columns=['profile_id', 'firstName', 'lastName', 'birthDate', 'phone_numbers', 'summary', 'geoCountryName',
                                                'email_address', 'followersCount','headline', 'Volunteer', 'Publications', 'honors', 'student'])
        df_Langues = pd.DataFrame(columns=['profile_id','name_langue', 'proficiency'])
        df_Societe = pd.DataFrame(columns=['companyUrn', 'companyName', 'geoLocationName', 'industries', 'staffCount', 'companyPageUrl',
                                                'companyType', 'phone', 'profile_id'])
        df_Skills = pd.DataFrame(columns=['standardizedSkillUrn', 'name_skill','profile_id'])
        df_Formation = pd.DataFrame(columns=['entityUrn', 'schoolName', 'degreeName', 'fieldOfStudy', 'Period', 'profile_id'])
        df_Experience = pd.DataFrame(columns=['entityUrn', 'companyUrn', 'Period','title', 'profile_id'])
        df_Certifications = pd.DataFrame(columns=['entityUrn','authority', 'name_certif', 'Period','profile_id'])

        #itérer chaque profil et décomposer son contenu en différentes dataframes

        for i in range(len(self.people)):
            #extraire l'id public du profil en cours de traitement
            self.public_id = self.people[i]['public_id']

            #recuperer les informations de ce profil avec son public_id
              #info profil
            profil = api.get_profile(self.public_id)
              #info personnel(@mail,num_tel)
            contact = api.get_profile_contact_info(self.public_id)
              #info sur les connexions de linkedin
            info = api.get_profile_network_info(self.public_id)
              #info sur les compétences
            skills = api.get_profile_skills(self.public_id)

            #extraire de ce profil les parties:languages,experience,education et certifications
            lang = profil['languages']
            experience = profil['experience']
            education = profil['education']
            certifications = profil['certifications']

            #Dataframe Profile
            #créer une colonne profile_id et la remplir à partir de la fonction get_profile de l'api
            df_Profil.loc[i, 'profile_id'] = profil.get('profile_id')
            # créer une colonne firstName et la remplir à partir de la fonction get_profile de l'api
            df_Profil.loc[i, 'firstName'] = profil.get('firstName')
            # créer une colonne lastName et la remplir à partir de la fonction get_profile de l'api
            df_Profil.loc[i, 'lastName'] = profil.get('lastName')
            #bloc try/exept pour eviter les erreurs provoqué par les valeurs manquantes de l'api
            try:
                #recuperer la valeur birthDate à partir de la fonction get_profile de l'api
                b = profil['birthDate']
                #extraire le jour et le moi de la date et les concatinées en les insérées dans la colonne birthDate du dataframe
                df_Profil.loc[i, 'birthDate'] = str(b.get('day')) + '-' + str(b.get('month'))
                # créer une colonne phone_numbers et la remplir à partir de la fonction get_profile_contact_info de l'api
                df_Profil.loc[i, 'phone_numbers'] = str(contact.get('phone_numbers'))
            except:
                #on utilise se bloc si ya une valeur manquante et en la remplace par 'Not Found' si elle est de type chaine ou par 0 si son type est entier
                df_Profil.loc[i, 'birthDate'] = 'Not Found'
                df_Profil.loc[i, 'phone_numbers'] = str(0)
            # créer une colonne summary et la remplir à partir de la fonction get_profile de l'api
            df_Profil.loc[i, 'summary'] =profil.get('summary')
            # créer une colonne geoCountryName et la remplir à partir de la fonction get_profile de l'api
            df_Profil.loc[i, 'geoCountryName'] = profil.get('geoCountryName')
            # créer une colonne email_address et la remplir à partir de la fonction get_profile_contact_info de l'api
            df_Profil.loc[i, 'email_address'] = contact.get('email_address')
            # créer une colonne followersCount et la remplir à partir de la fonction  get_profile_network_info de l'api
            df_Profil.loc[i, 'followersCount'] = info.get('followersCount')
            # créer une colonne headline et la remplir à partir de la fonction get_profile de l'api
            df_Profil.loc[i, 'headline'] = profil.get('headline')
            # nom du table dans la bd
            df_Profil.name = 'Profil'

            # Dataframe Langue
            #creer un dataframe auxiliaire pour éviter l'ecrasement du datframe de base
            dflang = pd.DataFrame()

            #iterer tous les langues du profil au cours du traitement
            for j in range(len(lang)):

                try:
                    # créer une colonne name_langue et la remplir à partir de la partie languages de la fonction get_profile de l'api
                    dflang.loc[j, 'name_langue'] = profil['languages'][j]['name']
                    # créer une colonne name_langue et la remplir à partir de la partie languages de la fonction get_profile de l'api
                    dflang.loc[j, 'proficiency'] = profil['languages'][j]['proficiency']

                except:
                    #remplacer name_langue et proficiency par Not Found si elles n'existe pas
                    dflang.loc[j,[ 'name_langue','proficiency']] = 'Not Found'
                # créer une colonne profile_id et la remplir à partir de la fonction get_profile de l'api
                dflang.loc[j, 'profile_id'] = profil.get('profile_id')
            #ajouter les lignes du Dataframe auxiliaire au Dataframe originale
            df_Langues = df_Langues.append(dflang)

            # nom du table dans la bd
            df_Langues.name = 'Langues'


            ''' Dataframe Societe '''
            # creer un dataframe auxiliaire pour éviter l'ecrasement du datframe de base
            dfcomp = pd.DataFrame()
            # iterer tous les Societes ou le profil au cours du traitement a travailler dedans
            for j in range(len(experience)):
                try:
                    # créer une colonne companyUrn et la remplir à partir de la partie experience de la fonction get_profile de l'api
                    dfcomp.loc[j, 'companyUrn'] = profil['experience'][j]['companyUrn'].split(':')[3]
                    #recuperer la valeur du 'companyUrn' dans la variable compurn si elle existe
                    compurn = dfcomp.loc[j, 'companyUrn']
                    dfcomp.loc[j, 'companyName'] = profil['experience'][j]['companyName']
                    dfcomp.loc[j, 'geoLocationName'] = profil['experience'][j]['geoLocationName']
                    dfcomp.loc[j, 'industries'] = profil['experience'][j]['company']['industries']
                except:
                    # remplacer les colonnes de dataframe par Not Found si elles n'existe pas
                    dfcomp.loc[j, ['companyName','companyUrn','geoLocationName','industries']] = 'Not Found'
                    # si la valeur du 'companyUrn' est null  la variable compurn prend un 0
                    compurn = 0

                try:
                    #si la valeur compurn est non null alors on va recupérer les autres champs de la société
                    if compurn != 0:
                        #utuliser la fonction get_company de l'api qui prend en paramétres le urn de l'entreprise

                        company = api.get_company(compurn)

                        dfcomp.loc[j, 'staffCount'] = company.get('staffCount')
                        dfcomp.loc[j, 'companyPageUrl'] = company.get('companyPageUrl')
                        try:
                            dfcomp.loc[j, 'companyType'] = company['companyType']['localizedName']
                            dfcomp.loc[j, 'phone'] = company['phone']['number']
                        except:
                            dfcomp.loc[j, 'companyType'] = 'Not Found'
                            dfcomp.loc[j, 'phone'] = 0
                    else:
                        dfcomp.loc[j, ['staffCount','phone']] = 0
                        dfcomp.loc[j, ['companyPageUrl','companyType']] = 'Not found'
                except:
                    dfcomp.loc[j, 'companyUrn'] = 'Not Found'

                dfcomp.loc[j, 'profile_id'] = profil.get('profile_id')
            # ajouter les lignes du Dataframe auxiliaire au Dataframe originale
            df_Societe = df_Societe.append(dfcomp)
            df_Societe.name = 'Societe'

            #Dataframe Compétence
            # creer un dataframe auxiliaire pour éviter l'ecrasement du datframe de base
            dfskill = pd.DataFrame()
            # iterer tous les Compétences de profil au cours du traitement
            for j in range(len(skills)):
                try:
                    # créer une colonne standardizedSkillUrn et la remplir à partir de la fonction get_profile_skills de l'api
                    dfskill.loc[j, 'standardizedSkillUrn'] = skills[j]['standardizedSkillUrn'].split(':')[3]
                except:
                    dfskill.loc[j, 'standardizedSkillUrn'] = 'Not Found'
                # créer une colonne name_skill et la remplir à partir de la fonction get_profile_skills de l'api
                dfskill.loc[j, 'name_skill'] = skills[j]['name']

                dfskill.loc[j, 'profile_id'] = profil.get('profile_id')
            # ajouter les lignes du Dataframe auxiliaire au Dataframe originale
            df_Skills = df_Skills.append(dfskill)
            df_Skills.name = 'Skills'
            print(df_Skills)

            ''' Dataframe Formation '''
            # creer un dataframe auxiliaire pour éviter l'ecrasement du datframe de base
            dfeduc = pd.DataFrame()
            # iterer la partie education de profil au cours du traitement
            for j in range(len(education)):
                try:
                    # créer une colonne entityUrn et la remplir à travers la partie education de la fonction get_profile de l'api
                    dfeduc.loc[j, 'entityUrn'] = profil['education'][j]['school']['entityUrn'].split(':')[3]
                    # créer une colonne degreeName et la remplir à travers la partie education de la fonction get_profile de l'api
                    dfeduc.loc[j, 'degreeName'] = profil['education'][j]['degreeName']
                    # créer une colonne fieldOfStudy et la remplir à travers la partie education de la fonction get_profile de l'api
                    dfeduc.loc[j, 'fieldOfStudy'] = profil['education'][j]['fieldOfStudy']
                   #recuperer la date de début de la formation
                    a = profil['education'][j]['timePeriod']['startDate']
                    #extraire l'anne de la date de début de formation
                    startDate = str(a.get('year'))
                    #si la formation encours de traitement contient la date de fin de formation
                    if "endDate" in profil['education'][j]['timePeriod']:
                        #recuperer la date de fin de la formation
                        b = profil['education'][j]['timePeriod']['endDate']
                        # extraire l'anne de la date de fin de formation
                        endDate = str(b.get('year'))
                        #soustraire la date de début de la date de fin
                        tf = datetime.strptime(endDate, '%Y').date() - datetime.strptime(startDate,'%Y').date()
                        #creer la colonne periode qui contient le nombre des jours ecoulés dans la formation en cours de traitement
                        dfeduc.loc[j, 'Period'] = tf.days
                    # si la formation encours de traitement ne contient pas la date de fin de formation
                    else:
                        # soustraire la date de début de la date actuelle
                        tf = date.today() - datetime.strptime(startDate, '%Y').date()
                        # creer la colonne periode qui contient le nombre des jours ecoulés dans la formation en cours de traitement
                        dfeduc.loc[j, 'Period'] = tf.days

                except:
                    # remplacer les colonnes de dataframe par Not Found si elles n'existe pas
                    dfeduc.loc[j, ['entityUrn','degreeName','fieldOfStudy','Period']] = 'Not Found'

                dfeduc.loc[j, 'schoolName'] = profil['education'][j]['schoolName']
                dfeduc.loc[j, 'profile_id'] = profil.get('profile_id')
            # ajouter les lignes du Dataframe auxiliaire au Dataframe originale
            df_Formation = df_Formation.append(dfeduc)
            df_Formation.name = 'Formation'
            print(df_Formation)

            #Dataframe Expérience
            # creer un dataframe auxiliaire pour éviter l'ecrasement du datframe de base
            dfexp = pd.DataFrame()
            # iterer la partie experience de profil au cours du traitement
            for j in range(len(experience)):
                # créer une colonne entityUrn et la remplir à travers la partie education de la fonction get_profile de l'api
                dfexp.loc[j, 'entityUrn'] = profil['experience'][j]['entityUrn'].split(',')[1]

                try:
                    # créer une colonne companyUrn et la remplir à travers la partie education de la fonction get_profile de l'api
                    dfexp.loc[j, 'companyUrn'] = profil['experience'][j]['companyUrn'].split(':')[3]
                    # recuperer la date de début d'experience
                    a = profil['experience'][j]['timePeriod']['startDate']
                    # extraire le moi et l'anne de la date de début d'experience
                    startDate = str(a.get('month')) + '-' + str(a.get('year'))
                    # si l'experience encours de traitement contient la date de fin d'experience
                    if "endDate" in profil['experience'][j]['timePeriod']:
                        # recuperer la date de fin d'exprérience
                        b = profil['experience'][j]['timePeriod']['endDate']
                        # extraire le moi et l'anne de la date de fin d'experience
                        endDate = str(b.get('month')) + '-' + str(b.get('year'))
                        # soustraire la date de début de la date de fin
                        td = datetime.strptime(endDate, '%m-%Y').date() - datetime.strptime(startDate,'%m-%Y').date()
                        # creer la colonne periode qui contient le nombre des jours ecoulés dans l'experience en cours de traitement
                        dfexp.loc[j, 'Period'] = (td.days) + 30
                    # si l'experience encours de traitement ne contient pas la date de fin d'experience
                    else:
                        # soustraire la date de début de la date actuelle
                        td = date.today() - datetime.strptime(startDate, '%m-%Y').date()
                        # creer la colonne periode qui contient le nombre des jours ecoulés dans l'experience en cours de traitement
                        dfexp.loc[j, 'Period'] = td.days

                except:
                    # remplacer les colonnes de dataframe par Not Found si elles n'existe pas
                    dfexp.loc[j,[ 'companyUrn','Period']] = 'Not Found'

                dfexp.loc[j, 'title'] = profil['experience'][j]['title']
                dfexp.loc[j, 'profile_id'] = profil.get('profile_id')
            # ajouter les lignes du Dataframe auxiliaire au Dataframe originale
            df_Experience = df_Experience.append(dfexp)
            df_Experience.name = 'Experience'

            #Dataframe Certification
            # creer un dataframe auxiliaire pour éviter l'ecrasement du datframe de base
            dfcert = pd.DataFrame()
            # iterer la partie certifications de profil au cours du traitement
            for j in range(len(certifications)):

                try:
                    # créer une colonne entityUrn et la remplir à travers la partie certifications de la fonction get_profile de l'api
                    dfcert.loc[j, 'entityUrn'] = str((profil['certifications'][j]['company']['entityUrn']).split(':')[3])
                    # créer une colonne authority et la remplir à travers la partie certifications de la fonction get_profile de l'api
                    dfcert.loc[j, 'authority'] = str(profil['certifications'][j]['authority'])
                    # créer une colonne name_certif et la remplir à travers la partie certifications de la fonction get_profile de l'api
                    dfcert.loc[j, 'name_certif'] = str(profil['certifications'][j]['name'])
                    # recuperer la date de l'obtention du certif
                    a = profil['certifications'][j]['timePeriod']['startDate']
                    # extraire le moi et l'anne de la date de l'obtention du certif
                    startDate = str(a.get('month')) + '-' + str(a.get('year'))
                    # si le certif encours de traitement contient la date d'expiration
                    if "endDate" in profil['certifications'][j]['timePeriod']:
                        # recuperer la date d'expiration du certif
                        b = profil['certifications'][j]['timePeriod']['endDate']
                        # extraire le moi et l'anne de la date d'expiration du certif
                        endDate = str(b.get('month')) + '-' + str(b.get('year'))
                        # soustraire la date d'obtention de la date d'expiration
                        dt = datetime.strptime(endDate, '%m-%Y').date() - datetime.strptime(startDate,'%m-%Y').date()
                        # creer la colonne periode qui contient le nombre des jours de validité du certif
                        dfcert.loc[j, 'Period'] = str((dt.days) + 30)
                    else:
                        # soustraire la date d'obtention de la date actuelle
                        dt = date.today() - datetime.strptime(startDate, '%m-%Y').date()
                        # creer la colonne periode qui contient le nombre des jours apartir de la date d'obtention du certif
                        dfcert.loc[j, 'Period'] = str(dt.days)
                except:
                    # remplacer les colonnes de dataframe par Not Found si elles n'existe pas
                    dfcert.loc[j, ['entityUrn','authority','name_certif','Period']] = 'Not Found'

                dfcert.loc[j, 'profile_id'] = str(profil.get('profile_id'))

            # ajouter les lignes du Dataframe auxiliaire au Dataframe originale
            df_Certifications = df_Certifications.append(dfcert)
            df_Certifications.name = 'Certifications'
            print(df_Certifications)


        #Enregistrer  les dataframes sous forme des tables SQL
        #Liste des différents dataframe
        df=[df_Profil,df_Skills,df_Societe,df_Langues,df_Formation,df_Experience,df_Certifications]
        #iterer la liste des dataframe
        for val in df:
            #convertir un dataframe a un table sql
            val.to_sql(
            #le nom du dataframe dans sql
            name=val.name,
            con=engine,
            index=False,
            if_exists='append'
            )
        return "",200


class preprocess_Candidate_data():

    def __init__(self):
        pass

    def load_data(self, Table_name):
        """ Accès aux bases de données SQLite;
        output: Profile dataframe contient les informations général d'un profil """
        conn = sqlite3.connect('LinkedInDB')
        cur = conn.cursor()
        if Table_name == 'Profil':
            Tab_dic = cur.execute("SELECT profile_id,firstName,lastName,summary,headline FROM Profil").fetchall()
            Table = pd.DataFrame(Tab_dic, columns=['profile_id', 'firstName', 'lastName', 'summary', 'headline'])
        elif Table_name == 'Formation':
            Tab_dic = cur.execute("SELECT degreeName,fieldOfStudy,profile_id FROM Formation").fetchall()
            Table = pd.DataFrame(Tab_dic, columns=['degreeName', 'fieldOfStudy', 'profile_id'])
        elif Table_name == 'Experience':
            Tab_dic = cur.execute("SELECT description,title,profile_id FROM Experience").fetchall()
            Table = pd.DataFrame(Tab_dic, columns=['description', 'title', 'profile_id'])
        elif Table_name == 'Certifications':
            Tab_dic = cur.execute("SELECT name_certif,profile_id FROM Certifications").fetchall()
            Table = pd.DataFrame(Tab_dic, columns=['name_certif', 'profile_id'])
        elif Table_name == 'Societe':
            Tab_dic = cur.execute("SELECT industries,profile_id FROM Societe").fetchall()
            Table = pd.DataFrame(Tab_dic, columns=['industries', 'profile_id'])
        elif Table_name == 'Skills':
            Tab_dic = cur.execute("SELECT name_skill,profile_id FROM Skills").fetchall()
            Table = pd.DataFrame(Tab_dic, columns=['name_skill', 'profile_id'])
        else:
            print(Table_name,
                  "---Table name error! accepted tables are: Profil, Formation, Experience, Certifications, Langues, Societe,Skills    ")

        Table.drop_duplicates(keep='first', inplace=True, ignore_index=True)
        return Table



    def clean_text(self,text):
        text = text.replace('\\r', '').replace('&nbsp', '').replace('\n', '')
        text = re.sub('<[^>]*>', '', text)
        emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
        text = re.sub('[\W]+', ' ', text.lower()) + ' '.join(emoticons).replace('-', '')
        return text

    def _concatenate_df_row(self, row):
        """
        Concatinate dataframes rows
        input(multiple rows)
        output(one row)
                                    """
        rows_as_str = ' '.join(set(row))
        return rows_as_str

    def DF_transformation(self, Table_name):
        """
        dataframes Transformation
                                      """
        if Table_name == 'Experience':
            # recupération du dataframe expérience
            df = self.load_data('Experience')
            df = df.groupby('profile_id').agg(self._concatenate_df_row)
        elif Table_name == 'Profil':
            df = self.load_data('Profil')
            df = df[['profile_id', 'summary', 'headline']]
        elif Table_name == 'Formation':
            df = self.load_data('Formation')
            df = df.groupby('profile_id').agg(self._concatenate_df_row)

        elif Table_name == 'Certifications':
            df = self.load_data('Certifications')
            df = df.groupby(df['profile_id']).agg(self._concatenate_df_row)

        elif Table_name == 'Societe':
            df = self.load_data('Societe')
            df = df.groupby(df['profile_id']).agg(self._concatenate_df_row)

        elif Table_name == 'Skills':
            df = self.load_data('Skills')
            df = df.groupby('profile_id').agg(self._concatenate_df_row)
        else:
            print(Table_name,
                  "---Table name error! accepted tables are: Profil, Formation, Experience, Certifications, Langues, Societe,Skills    ")

        return df

    def Final_userdf_(self):
        """
        Final user Datafrme
                                    """
        skills = self.DF_transformation('Skills')
        profile = self.DF_transformation('Profil')
        Certif = self.DF_transformation('Certifications')
        Experience = self.DF_transformation('Experience')
        Formation = self.DF_transformation('Formation')
        Societe = self.DF_transformation('Societe')

        user_ = reduce(lambda x, y: pd.merge(x, y, on='profile_id', how='outer'),
                       [profile, skills, Experience, Certif, Formation, Societe])

        user_ = user_.fillna(value=np.nan)
        user_ = user_.replace(np.nan, '', regex=True)
        user_["candidate_info"] = (user_["summary"] + " " + user_["headline"] + " " + user_["name_skill"] + " " + user_[
            "name_certif"] + " " + user_["description"] + " " + user_["title"] + " " + user_["degreeName"] + " " +
                                   user_["fieldOfStudy"] + " " + user_["industries"]).agg(self.clean_text)
        userfinal_ = user_[["profile_id", "candidate_info"]]

        return userfinal_


class get_recommendations():
    def __init__(self):
       pass



    def recommendation(self,JobDescription):
        instance = preprocess_Candidate_data()
        userfinal_ = instance.Final_userdf_()
        dfProfilinfo = instance.load_data('Profil')
        dfinfo = dfProfilinfo[['profile_id', 'firstName', 'lastName']]
        eng = create_engine('sqlite:///recommendation', echo=False)
        df = pd.DataFrame(columns=['id', 'nom', 'prenom'])
        #pickle l'output du Final_userdf dans un objet
        with open('Final_userdf.pk', mode='wb') as fuserdf:
            pickle.dump(userfinal_, fuserdf)
        # pickle vectorizer dans un objet
        vectorizer = TfidfVectorizer(max_features=5000, max_df=0.95, min_df=2, analyzer='word', stop_words='english',
                                     use_idf=True)
        with open('vectorizer.pk', mode='wb') as vectorizerr:
            pickle.dump(vectorizer, vectorizerr)

        with open('Final_userdf.pk', mode='rb') as fuserdf:
            candidatepk = pickle.load(fuserdf)

        with open('vectorizer.pk', mode='rb') as vectorizerr:
            vectorizerpk = pickle.load(vectorizerr)
        # 2# 2- appelle l'objet Final_userdf.pk, et son utilisation pour alimenter tfidf_vectorizer.fit_transform : matrice X
        # appele du vectorizer.pk
        tfidf_user_matrix = vectorizerpk.fit_transform(candidatepk['candidate_info'])
        # print(tfidf_user_matrix)

        #3
        tfidf_matrixjob = vectorizerpk.transform(JobDescription)

        # 4 - calculer les cosine_similarity
        cosine_simlilarity_output = cosine_similarity(tfidf_matrixjob, tfidf_user_matrix)

        # 5 +6  - sort les cosine similarities   afficher les top 5
        index_des_max_simi = np.argsort(-cosine_simlilarity_output)[:, :5]
        valuelist = ((np.sort(-cosine_simlilarity_output )* -1 )[:,:5].tolist())

        reclist = []
        for i, v in dfinfo.iterrows():
            if (i in index_des_max_simi):
                reclist.append(v)
                # add a column to T, at the front:
        l = np.insert(reclist, 1, valuelist, axis=1)

        df = pd.DataFrame(l, columns=['LinkedIn_Profile', 'Score', 'Nom', 'Prenom'])
        df.LinkedIn_Profile = "https://www.linkedin.com/in/" + df.LinkedIn_Profile
        df.Score = ((df.Score)*100).apply(lambda x: f"{x:.2f}")

        df.to_sql('recandidate', con=eng, if_exists='append', index_label='id')
        return df





