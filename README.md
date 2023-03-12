# Project Omega
## Concept de base
Le bot a pour but de syncroniser automatiquement les roles discord aux differents items present sur [l'intranet](https://profile.intra.42.fr). Il supporte actuellement les items suivant :
- Cursus
- Groupes
- Projects
- Coalition
- Années

il permet egalement de definir une politique de nommage permettant d'uniformiser le nom des membres.

## Etre pris en compte par protocole Omega
executez la commande /login puis suivre l'oauth sur le lien qui vous sera transmit

Cette manipulation n'est necessaire qu'une seule fois par etudiant

# Administrer un serveur sous Project Omega
Les commandes suivantes servent a la configuration des differentes options du bot. Elles peuvent etre effectuer par tous membres possedant les droits administrateur sur le serveur. **Attention** les configurations sont unique, chaque serveur possede la sienne.
## Les commandes de configuration

### `/sync` : *Configuration globale*

> Elle vous permettra de definir l'item a syncroniser

![image](https://user-images.githubusercontent.com/73013583/217251656-c52517a0-d417-4f47-a2c5-e57d7276a841.png)

> Son identifiant sur l'intranet (dans le cas de l'année il faut mettre l'année d'enter a l'ecole au lieu d'un id)

![image](https://user-images.githubusercontent.com/73013583/217251919-783fa14f-a457-454d-9761-f28ef995c58a.png)

> L'identifiant du role discord correspondant

![image](https://user-images.githubusercontent.com/73013583/217252106-451343f9-83f9-4dfd-8176-89995a599c90.png)

> Et enfin vous pouvez definir l'id du campus necessaire pour obtenir le role. (pour definir tous les campus vous pouvez entrer 0)

![image](https://user-images.githubusercontent.com/73013583/217252464-bc7aa4cd-dd22-4c71-b4f5-1b1b11eb4601.png)

### `/sync_project` : *Syncronisation des projets*

> Elle vous permettra de definir son identifient sur l'intranet

![image](https://user-images.githubusercontent.com/73013583/217271621-98cba57a-4c63-4a0f-bb15-6e74f9f4d86f.png)

> D'autoriser ou non les differents statuts possible avec le projet

![image](https://user-images.githubusercontent.com/73013583/217272838-bbe0ddc0-efe3-440b-b054-e2dbd39e4a42.png)

> De definir l'identifiant du role discord correspondant

![image](https://user-images.githubusercontent.com/73013583/217272356-73a8b784-4e54-492f-a178-66fe12a2a064.png)

> Et enfin vous pouvez definir l'id du campus necessaire pour obtenir le role. (Pour definir tous les campus vous pouvez entrer 0)

![image](https://user-images.githubusercontent.com/73013583/217272447-f76af907-2d3a-48a6-b0bc-bab761ad730b.png)

### `/nick` : *Definition de la politique de nommage*

![Screenshot from 2023-02-07 23-39-16](https://user-images.githubusercontent.com/73013583/217383303-a51f6b7e-9099-417c-a029-92d66627e6e6.png)

> L'argument **naming_patern** permet de configurer le patern de nommage. (&login et &campus sont des valeurs dynamiques elle seront remplacee par leur valeur pour chaque etudiants).

> L'argument **campus** correspond a l'id du campus sur lesquels la politique va s'appliquer. (pour definir tout les campus vous pouvez entrer 0).

## Supprimer sa configuration

### `/delete` : *Suppression de la configuration*

> Elle vous permettra de specifier le type de sychronisation a interrompre

![image](https://user-images.githubusercontent.com/73013583/217357888-95d4e890-b0f4-4ec1-a7bb-012226665479.png)

> L'id intranet ou l'id discord en rapport

![image](https://user-images.githubusercontent.com/73013583/217358609-5d94a3cf-a2e9-4668-86d8-c6e02d63a5e9.png)

> Et enfin l'identifiant

![image](https://user-images.githubusercontent.com/73013583/217358701-47730a2c-319a-4bba-8b04-90a6569f4648.png)

### `/nick_reset` : Suppression des politique de nomage sur le serveur

![image](https://user-images.githubusercontent.com/73013583/217359712-2807b613-cb4d-4a41-8b6e-c0bd3465bf34.png)

# Lancer avec docker

Renommer le fichier `.env.template` en `.env`, puis saisir toutes les informations.

- `DOMAIN`: Le domaine avec son protocole (`http://toto.42`)
- `BOT_TOKEN`: Le token du bot discord présent sur le portail developpeur
- `API_UID`: api intra 42 uid
- `API_SECRET`: api intra 42 secret
- `MODE`: DEV (pour run en http), PROD (pour run en https)

## Lancer en dev

Celon la version de docker compose:
```bash
docker-compose up --build
```
ou
```bash
docker compose up --build
```

## Lancer en prod

Ajouter / modifier sur le service `oauth` dans le `docker-compose.yml`
- les certificats 
- expose le port https

```yml
volumes:
    - ./omega.db:/app/omega.db
    - file_privkey:/app/cert/privkey.pem
    - file_fullchain:/app/cert/fullchain.pem
ports:
    - "443:443"
```

Celon la version de docker compose:
```bash
docker-compose up --build
```
ou
```bash
docker compose up --build
```
## Notes
La version actuel (beta) a une base de données litesql3 (changement certainement à venir)
