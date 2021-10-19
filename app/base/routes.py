# -*- encoding: utf-8 -*-
import bcrypt
import flask
import mail
from app import mail,bcrypt
from flask import Flask,jsonify, render_template, redirect, request, url_for, flash
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user)
from app import db, login_manager,Jobs
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm,RequestResetForm, ResetPasswordForm,UpdateAccountForm
from app.base.models import User
from app.base.util import verify_pass

from app.base.Local_functions import Scraping,get_recommendations
from flask_mail import Message
import sqlite3
from app.base.models import User,Job
#from ipython_genutils.py3compat import str_to_bytes
from werkzeug.security import generate_password_hash,check_password_hash
import pandas as pd
import json

@blueprint.route('/')
def route_default():
    """Hash a password for storing."""
    return redirect(url_for('base_blueprint.login'))


## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])

def login():

    """
    Permet à chaque utilisateur d'accéder a son compte à travers son nom d'utilisateur et  mot de passe
    """

    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()

        # Check the password
        if user:
            if verify_pass(password, user.password):
                login_user(user)
                return redirect(url_for('base_blueprint.route_default'))
            else:
                 status = 'Password Error !'
            return render_template('accounts/login.html', form=login_form, msg=status)
        else:
            status = "User doesn't exist !"
            return render_template('accounts/login.html', form=login_form, msg=status)
    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form,
                               )
    return redirect(url_for('home_blueprint.index'))


def send_reset_email(user):
    """
     Permet d'envoyer le mail de réinitialisation
            """



    token = user.get_reset_token()
    msg = Message('Demande de réinitialisation du mot de passe',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''pour réinitialiser votre mot de passe, visitez le lien suivant:
     {url_for('base_blueprint.reset_token', token=token, _external=True)}
     '''
    mail.send(msg)


@blueprint.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """
         Pour demander une réinitialisation de mot de passe
    """

    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('base_blueprint.login'))
    return render_template('accounts/reset_request.html', title='Rénitialiser mot de passe', form=form)



@blueprint.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """
          ¨Permet réinitialiser le mot de passe avec le jeton actif

                """
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))


    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('base_blueprint.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #hashed_password = bcrypt.hashpw((form.password.data).encode('utf-8'), bcrypt.gensalt())

        user.password = (hashed_password).encode()
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('base_blueprint.login'))
    return render_template('accounts/reset_token.html', title='Reset Password', form=form)




@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
            Permet d'enregister un nouveau utilisateur
             """
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('base_blueprint.register'))

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user

        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('base_blueprint.register'))
    else:
        return render_template('accounts/register.html', form=create_account_form)



@blueprint.route('/logout')
def logout():
    """
               Permet à un utilisateur de se déconnécter
                """
    logout_user()
    return redirect(url_for('base_blueprint.login'))

#Linkedin
@blueprint.route('/linkedin')
@login_required
def my_form():
    return render_template('TalentSearch.html')

scrapinstance= Scraping()
@blueprint.route('/linkedin',methods=['POST','GET'])
@login_required
def my_form_post():
    """
         Permet d'afficher le formulaire de scrapping des donneés
                """
    text=request.form['keyword']
    return Scraping.scraping_F(scrapinstance,text)

recommendationinstance= get_recommendations()
@blueprint.route('/recommendation', methods=['POST','GET'])
@login_required
def my_posjob():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags = request.form['value']

        j = Job(title,description,tags)
        Jobs.session.add(j)
        Jobs.session.commit()
        jobdesciption= title+" "+description+"  "+tags
        df = get_recommendations.recommendation(recommendationinstance, [jobdesciption])

        # parsing the DataFrame in json format.
        json_records = df.to_json(orient='records')
        data = []
        context = json.loads(json_records)



        return render_template('Recresult.html', context=context)

    return render_template('Recommender.html')

@blueprint.route('/jobrecommendation')
@login_required
def jobrecommendation():


    return render_template('Recresult.html')


@blueprint.route('/DisplayProfiltab')
@login_required
def Display_profiletab():
    """
             Affichage des information générale du profil de l'utilisateur connecté

             """

    conn = sqlite3.connect('LinkedInDB_TEST')
    cur = conn.cursor()
    req="SELECT firstName,lastName,headline FROM Profil"
    result=cur.execute(req)
    data=cur.fetchall()
    return render_template('DisplayProfiltab.html',data=data)



## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500




#userProfile


@blueprint.route('/userprofile/<username>/' ,methods=['POST','GET'])
@login_required
def userprofileform(username):
    """
           Mise à jour des information générale du profil de l'utilisateur connecté


           :Parameters:  **username (str)** - le nom d'utilisateur de session connécté


           :Return: Profil mis à jour

           """

    form=UpdateAccountForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Votre compte a été mis à jour!", "Succès")

            old = request.form['current_password']
            password = request.form['new_password']
            confirm = request.form['confirm_password']
            if password != confirm:
                flash('le mot de passe et le mot de passe de confirmation ne correspondent pas', 'danger')
                return redirect(url_for('base_blueprint.userprofileform', username=User.username))
            password = bcrypt.generate_password_hash(password)
            print(password)
            conn = sqlite3.connect('db.sqlite3')
            cur = conn.cursor()
            result = cur.execute("SELECT * from User where username=?",[username])

            if result != None:
                user = cur.fetchone()
                print(user)
                passw = user[3]
                print(passw)
                pas=(passw.decode("utf-8"))

                old = generate_password_hash(old)
                if   check_password_hash(pas,old):
                    flash('le mot de passe ne correspond pas', 'danger')
                    print('le mot de passe ne correspond pas', 'danger')
                    return redirect(url_for('base_blueprint.userprofileform', username=User.username))

                else:

                    cur = conn.cursor()
                    password.decode('utf-8')
                    cur.execute("UPDATE User SET password=? WHERE username=?", [password, username])
                    conn.commit()
                    cur.close()
                    flash('Mot de passe modifier avec succe', 'success')
                    print('Mot de passe modifier avec succe', 'success')
                    return redirect(url_for('base_blueprint.userprofileform', username=User.username))
            return redirect(url_for('base_blueprint.userprofileform',username=User.username))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('UserProfile.html',form=form)


def connect():
    '''
      Accès aux bases de données SQLite;
      :utput: Profile dataframe contient les informations général d'un profil
        '''
    # Utilisez la méthode connect() du module sqlite3 et passez le nom de la base de données en argument.
    conn = sqlite3.connect('LinkedInDB_TEST')
    #Créez un objet curseur à l’aide de l’objet de connexion renvoyé par la méthode connect() pour exécuter des requêtes SQLite
    cur = conn.cursor()
    # la méthode execute() du curseur,permet d'exécuter une requête
    Profildict = cur.execute("SELECT * FROM Profil").fetchall()
    #Creer un dataframe a partir des données récupérer de la BD
    ProfilDF = pd.DataFrame(Profildict,columns=['profile_id', 'keyword', 'firstName', 'lastName', 'birthDate', 'phone_numbers',
                                     'summary', 'geoCountryName', 'email_address', 'followersCount', 'headline','Volunteer', 'Publications', 'honors', 'student'])

    Formationdict = cur.execute("SELECT * FROM Formation").fetchall()
    FormationDF = pd.DataFrame(Formationdict,columns=['entityUrn', 'schoolName', 'degreeName', 'fieldOfStudy', 'Period','profile_id'])

    Experiencedict = cur.execute("SELECT * FROM Experience").fetchall()
    ExperienceDF = pd.DataFrame(Experiencedict, columns=['entityUrn', 'companyUrn', 'Period', 'title', 'profile_id'])

    Certificationsdict = cur.execute("SELECT * FROM Certifications").fetchall()
    CertificationsDF = pd.DataFrame(Certificationsdict,columns=['entityUrn', 'authority', 'name_certif', 'Period', 'profile_id'])

    Languesdict = cur.execute("SELECT * FROM Langues").fetchall()
    LanguesDF = pd.DataFrame(Languesdict, columns=['profile_id', 'name_langue', 'proficiency'])

    Societedict = cur.execute("SELECT * FROM Societe").fetchall()
    SocieteDF = pd.DataFrame(Societedict,columns=['companyUrn', 'companyName', 'geoLocationName', 'industries', 'staffCount',
                                        'companyPageUrl', 'companyType', 'phone', 'profile_id'])

    Skillsdict = cur.execute("SELECT * FROM Skills").fetchall()
    SkillsDF = pd.DataFrame(Skillsdict, columns=['standardizedSkillUrn', 'name_skill', 'profile_id'])
    #Efface les redondance d'un dataframe
    l = [ProfilDF, FormationDF, ExperienceDF, CertificationsDF, LanguesDF, SocieteDF, SkillsDF]
    for i in l:
        i.drop_duplicates(keep='first', inplace=True)
    return ProfilDF, FormationDF, ExperienceDF, CertificationsDF, LanguesDF, SocieteDF, SkillsDF


def connectcloud():
    '''
      Accès aux bases de données SQLite;
      output: Profile dataframe contient les informations général d'un profil
        '''
    connc = sqlite3.connect('mix')
    curc = connc.cursor()

    Profildict = curc.execute("SELECT * FROM Profil").fetchall()
    ProfilDF = pd.DataFrame(Profildict,
     columns=['profile_id', 'firstName', 'lastName', 'birthDate', 'phone_numbers', 'summary',
       'geoCountryName', 'geoLocationName', 'email_address', 'followersCount', 'headline',
       'Volunteer', 'Publications', 'honors', 'student', 'keyword'])

    return ProfilDF


@blueprint.route('/Chart',methods=['POST','GET'])
def index():
    return render_template("Chart.html")


@blueprint.route('/Chart/profil_motcle',methods=['POST','GET'])
def profil_motcle():
    '''
    Afficher le nombre des profils par mots clés

    :output: Diagramme '''

    data = []
    l = ['Cloud','Java','Web','Data_Science']
    for i in l:
        # connect
        ProfilDF = connectcloud()
        #filtrer DF selon la liste des mot cles"l"
        Profil = ProfilDF[ProfilDF['keyword'] == i]
        #calculer nombre des profils par mot cle
        data.append(len(Profil))
        #trier la liste
        data.sort(reverse=True)
    #recuperer la liste des labels
    keywordlist = (ProfilDF['keyword'].unique()).tolist()
    #convertir la liste en json
    keywordjson = json.dumps(keywordlist)

    return jsonify({'data': data,'keywordjson':keywordjson})

@blueprint.route('/Chart/profil_anneexp',methods=['POST','GET'])
def profil_anneexp():
    '''
    Afficher le nombre des profils par nombre d'années d'experience

    :output: Diagramme
    '''
    #connection à la bd
    ExperienceDF = connect()[2]
    #remplacer "Not Found" par 0
    ExperienceDF = ExperienceDF.replace("Not Found", 0)
    #extraire le champ période et le convertir en numérique
    ExperienceDF['Period'] = pd.to_numeric(ExperienceDF['Period'])
    #convertir le nombre des jours en année
    ProfilePer = (ExperienceDF.groupby("profile_id").sum("Period") / 365).round()
    L = []
    x = range(26)
    #extraire le champ periode du ProfilePer et le convertir en numérique
    ProfilePer["Period"] = pd.to_numeric(ProfilePer["Period"])
    #
    for i in x:
        # filtrer DF selon les différentes valeur du range
        Profil = ProfilePer[ProfilePer["Period"] == i]
        #calculer nombre des profils par valeur
        L.append(len(Profil))
    return jsonify({'L': L})


@blueprint.route('/Chart/profil_ecole',methods=['POST','GET'])
def profil_ecole():
    '''
    Afficher le nombre des profils pour les 10 premiéres écoles

    :output: Diagramme
    '''
    # Recuperer Ecole dataframe
    EcoleDF = connect()[1]
    # calculer le nombre de repetition des ecole dans le df selon leurs nom
    EcoleSeries = EcoleDF.groupby("schoolName").count()['entityUrn']
    # extraire les top 10 ecole (ont le plus grand nombre des répetitions)
    TopEcole = EcoleSeries.nlargest(10)
    # enregistrer le reste des ecoles dans la partie autres
    OtherSeries = (EcoleSeries.sort_values(ascending=False)).iloc[10:]
    # calculer pourcentage de la partie autre
    otherper = (OtherSeries.sum() / EcoleSeries.sum()) * 100
    # creer un dictionnaire on mettant de dans le label el la valeur de la partie 'Other'
    dictper = {'Other': otherper}
    # convertir le type dectionnaire en series
    serper = pd.Series(dictper)
    # calculer pourcentage du top 10 ecoles
    TopEcole = ((TopEcole / EcoleSeries.sum()) * 100)
    # ajouter la partie other au series principale
    Ecolechart = pd.Series(TopEcole.append(serper))

    listecoleper = []
    # formater chaque ecole en lui ajoutant le symbole "%"  et lui arrondissant à 2 décimales aprés la virgule
    for i in Ecolechart:
        listecoleper.append("{:0.2f}".format(i))

    # récuperer les label des series automatiquement
    labelecole = ((Ecolechart.index).values)
    #convertir les labels récupérer à une liste
    listecole = labelecole .tolist()
    # convertir la listes en json
    json_Perlistecole = json.dumps(listecoleper)
    json_Labellistecole = json.dumps(listecole)

    return jsonify({'json_Perlistecole': json_Perlistecole ,'json_Labellistecole':json_Labellistecole})

@blueprint.route('/Chart/profil_skills',methods=['POST','GET'])
def profil_skills():
    '''
    Afficher le nombre des profils par Comptétence

    :output: Diagramme
    '''
    # Recuperer Skills dataframe
    SkillsDF = connect()[6]
    # calculer le nombre de repetition des skills dans le df selon leurs nom
    SkillsSeries = SkillsDF.groupby("name_skill").count()['standardizedSkillUrn']
    # extraire les top 10 skills (ont le plus grand nombre des répetitions)
    TopSkill = SkillsSeries.nlargest(10)
    # enregistrer le reste des skills dans la partie autres
    OtherSeries = (SkillsSeries.sort_values(ascending=False)).iloc[10:]
    # calculer pourcentage de la partie autre
    otherper = (OtherSeries.sum() / SkillsSeries.sum()) * 100
    # creer un dictionnaire on mettant de dans le label el la valeur de la partie 'Other'
    dictper = {'Other': otherper}
    # convertir le type dectionnaire en series
    serper = pd.Series(dictper)
    # calculer pourcentage du top 10 skills
    TopSkill = ((TopSkill / SkillsSeries.sum()) * 100)
    # ajouter la partie other au series principale
    Skillschart = pd.Series(TopSkill.append(serper))

    ListSkillschart = []
    # formater chaque skill en lui ajoutant le symbole "%"  et lui arrondissant à 2 décimales aprés la virgule
    for i in Skillschart:
        ListSkillschart.append("{:0.2f}".format(i))

    # récuperer les label des series automatiquement
    labelskill = ((Skillschart.index).values)

    #convertir les labels en liste
    listlabelskill=labelskill.tolist()
    #convertir les listes en json
    json_labelskell = json.dumps(listlabelskill)
    json_skillper = json.dumps(ListSkillschart)
    return jsonify({'json_skillper': json_skillper,'json_labelskell':json_labelskell })

@blueprint.route('/Chart/Sc_Industries',methods=['POST','GET'])
def Sc_Industries():
    '''
    Afficher le nombre des scociétés par secteur

    :output: Diagramme
    '''
    # connection à la bd
    ScINdf = connect()[5]
    # remplacer tous apparition du mot 'Not Found ' par Inconnu
    ScINdf = ScINdf.replace("Not Found", 'Inconnu')
    # calculer le nombre de repetition des secteurs dans le df selon leurs nom
    SectSeries = ScINdf.groupby("industries").count()['companyUrn']
    # extraire les top 10 secteurs (ont le plus grand nombre des répetitions)
    TopSkIndus = SectSeries.nlargest(5)
    # enregistrer le reste des secteur dans la partie autres
    OtherSeries = (SectSeries.sort_values(ascending=False)).iloc[10:]
    # calculer pourcentage de la partie autre
    otherper = (OtherSeries.sum() / SectSeries.sum()) * 100
    # creer un dictionnaire on mettant de dans le label el la valeur de la partie 'Other'
    dictper = {'Other': otherper}
    # convertir le type dectionnaire en series
    serper = pd.Series(dictper)
    # calculer pourcentage du top 5 secteurs
    TopSkIndus = ((TopSkIndus / SectSeries.sum()) * 100)
    # ajouter la partie other au series principale
    indus = pd.Series(TopSkIndus.append(serper))

    listesecteur = []
    # formater chaque secteur en lui ajoutant le symbole "%"  et lui arrondissant à 2 décimales aprés la virgule
    for i in indus:
        listesecteur.append("{:0.2f}".format(i))

    # convertir la liste en json
    json_listesecteur = json.dumps(listesecteur)
    return jsonify({'json_listesecteur': json_listesecteur})

@blueprint.route('/Chart/TotalProfil',methods=['POST','GET'])
def TotalProfil():

  '''
  Calcul des totaux

  :output: 3 diagramme
  '''
  #Total des profils
  #connection à la bd
  Profildf=connect()[0]
  #calcul de nombre des profils
  profnb= Profildf.count()
  #convertir le dataframe en list
  profval = profnb.values
  lists = profval.tolist()
  #convertir la liste en json
  json_str = json.dumps(lists[1])

  #Total des compétences
  #connection à la bd
  dfskill = connect()[6]
  #recuperation des compétences sans redondance
  uniqskill = (dfskill['name_skill'].unique())
  #convertir le dataframe en list
  skilist = (uniqskill.tolist())
  #calcul de nombre des compétences
  listlen = len(skilist)
  #convertir la liste en json
  skiljson = json.dumps(listlen)

  #Total des secteurs
  #connection à la bd
  ScINd = connect()[5]
  #recuperation des secteurs sans redondance
  sect = ScINd['industries'].unique()
  # convertir le dataframe en list
  listsec = sect.tolist()
  #calcul de nombre des compétences
  listseclen = len(listsec)
  #convertir la liste en json
  sectjson=json.dumps(listseclen)
  return jsonify({'json_str': json_str,'skiljson':skiljson ,'sectjson':sectjson})

@blueprint.route('/Chart/Pays',methods=['POST','GET'])
def Pays():
    '''
    Afficher la distribution des profils sur la carte

    :output: Map
     '''
    # connection à la bd
    ProfilDF = connect()[0]
    #recuperation des pays sans redondance
    pays = (ProfilDF['geoCountryName'].unique())
    #convertir le Series à une liste
    payslist = pays.tolist()
    #effacer les valeur null
    str_list = list(filter(None, payslist))
    pays = []
    #creation du dictionnaire du pay composé du 'nom de pay' :'code du pay'
    dict = {'Indonesia': 'ID',
            'Papua New Guinea': 'PG',
            'Mexico': 'MX',
            'Estonia': 'EE',
            'Algeria': 'DZ',
            'Morocco': 'MA',
            'Mauritania': 'MR',
            'Senegal': 'SN',
            'Gambia': 'GM',
            'Guinea-Bissau': 'GW',
            'Guinea': 'GN',
            'Sierra Leone': 'SL',
            'Liberia': 'LR',
            'Cote d\'Ivoire': 'CI',
            'Mali': 'ML',
            'Burkina Faso': 'BF',
            'Niger': 'NE',
            'Ghana': 'GH',
            'Togo': 'TG',
            'Benin': 'BJ',
            'Nigeria': 'NG',
            'Tunisia': 'TN',
            'Libya': 'LY',
            'Egypt': 'EG',
            'Chad': 'TD',
            'Sudan': 'SD',
            'Cameroon': 'CM',
            'Eritrea': 'ER',
            'Djibouti': 'DJ',
            'Ethiopia': 'ET',
            'Somalia': 'SO',
            'Yemen': 'YE',
            'Central African Republic': 'CF',
            'Sao Tome and Principe': 'ST',
            'Equatorial Guinea': 'GQ',
            'Gabon': 'GA',
            'Congo': 'CG',
            'Angola': 'AO',
            'Congo': 'CD',
            'Rwanda': 'RW',
            'Burundi': 'BI',
            'Uganda': 'UG',
            'Kenya': 'KE',
            'Tanzania': 'TZ',
            'Zambia': 'ZM',
            'Malawi': 'MW',
            'Mozambique': 'MZ',
            'Zimbabwe': 'ZW',
            'Namibia': 'NA',
            'Botswana': 'BW',
            'Swaziland': 'SZ',
            'Lesotho': 'LS',
            'South Africa': 'ZA',
            'Greenland': 'GL',
            'Australia': 'AU',
            'New Zealand': 'ZN',
            'New Caledonia': 'NC',
            'Italy': 'IT',
            'France': 'FR',
            'Netherlands': 'NL',
            'Belgium': 'BE',
            'Germany': 'DE',
            'Denmark': 'DK',
            'Switzerland': 'CH',
            'Austria': 'AT',
            'Croatia': 'HR',
            'Canada': 'CA',
            'Spain': 'ES',
            'Portugal': 'PT',
            'United States of America': 'US',
            'Malaysia': 'MY',
            'Brunei Darussalam': 'BN',
            'Timor-Leste': 'TL',
            'Solomon Islands': 'SB',
            'Vanuatu': 'VU',
            'Fiji': 'FJ',
            'Philippines': 'PH',
            'China': 'CN',
            'Taiwan': 'TW',
            'Japan': 'JP',
            'Russian Federation': 'RU',
            'Mauritius': 'MU',
            'Reunion': 'RE',
            'Madagascar': 'MG',
            'Comoros': 'KM',
            'Seychelles': 'SC',
            'Maldives': 'MV',
            'Cape Verde': 'CV',
            'French Polynesia': 'PF',
            'Saint Kitts and Nevis': 'KN',
            'Antigua and Barbuda': 'AG',
            'Dominica': 'DM',
            'Saint Lucia': 'LC',
            'Barbados': 'BB',
            'Grenada': 'GD',
            'Trinidad and Tobago': 'TT',
            'Dominican Republic': 'DO',
            'Haiti': 'HT',
            'Falkland Islands': 'FK',
            'Iceland': 'IS',
            'Norway': 'NO',
            'Sri Lanka': 'lk',
            'Cuba': 'CU',
            'Bahamas': 'BS',
            'Jamaica': 'JM',
            'Ecuador': 'EC',
            'Guatemala': 'GT',
            'Honduras': 'HN',
            'El Salvador': 'SV',
            'Nicaragua': 'NI',
            'Costa Rica': 'CR',
            'Panama': 'PA',
            'Colombia': 'CO',
            'Venezuela': 'VE',
            'Guyana': 'GY',
            'Suriname': 'SR',
            'French Guiana': 'GF',
            'Peru': 'PE',
            'Bolivi': 'BO',
            'Paraguay': 'PY',
            'Uruguay': 'UY',
            'Argentina': 'AR',
            'Chile': 'CL',
            'Brazil': 'BR',
            'Belize': 'BZ',
            'Mongolia': 'MN',
            'North Korea': 'KP',
            'South Korea': 'KR',
            'Kazakhstan': 'KZ',
            'Turkmenistan': 'TM',
            'Uzbekistan': 'UZ',
            'Tajikistan': 'TJ',
            'Kyrgyz Republic': 'KG',
            'Afghanistan': 'AF',
            'Pakistan': 'PK',
            'India': 'IN'

            }
    #iterer les valeur du dictionnaire
    for cle, valeur in dict.items():
        #iterer la liste des pays de la bd si le pays existe alors en récupére le code dans une nouvelle liste pays
        for i in str_list:
            if i == cle:
                pays.append(valeur)

    return jsonify({'pays': pays})



