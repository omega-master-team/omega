# Project Omega

## Concept de base
Le bot a pour but de synchroniser automatiquement les roles discord aux differents items présents sur [l'intranet](https://profile.intra.42.fr). Il supporte actuellement les items suivants :
- Cursus
- Groupes
- Projects
- Coalitions
- Années

Il permet également de définir une politique de nommage permettant d'uniformiser le nom des membres.

## Etre pris en compte par protocole Omega

Executer la commande `/login` puis suivre l'oauth sur le lien qui vous sera transmis.

Cette manipulation n'est nécessaire qu'une seule fois par étudiant

___

# Déploiment

## Prérequis

- Connexion internet
- 5 Go
- `docker`
- `docker-compose` (command) ou `docker compose` (plugin)
- les droits super-utilisateur pour ouvrir les ports réservé (http ou https) ([< 1024](https://www.w3.org/Daemon/User/Installation/PrivilegedPorts.html))

## Lancement

Renommer le fichier `.env.template` en `.env`, puis saisir toutes les informations.

- `DOMAIN`: Le domaine avec son protocole (ex: `http://toto.42`)
- `BOT_TOKEN`: Le token du bot discord présent sur le portail developpeur
- `API_UID`: api intra 42 uid
- `API_SECRET`: api intra 42 secret
- `MODE`: DEV (pour run en http), PROD (pour run en https)

**Note:** pour l'api la redirect uri devra correspondre à `DOMAIN/connected`, avec `DOMAIN` la variable du `.env`.

Le déploiement se fait avec docker, pour lancer omega lancer:
```bash
# see make help
make
```
**Attention:** le port exposé dans le `docker-compose.yml` ne doit pas être utilisé.

**Note:** le build prend quelques minutes (selon la connexion et le cpu).

## Détails liés à la mise en production

> Pour lancer le projet en production, il faut:
> - dans le `.env`, mettre `MODE=PROD`
> - dans le `docker-compose`, mettre les 2 fichiers pour les certificats ssl en volume (décommenter et mettre le bon path) /!\ changer uniquement le path de la machine et non celui du conteneur
> - dans le `docker-compose`, changer le port exposé (normalement 443)

___

# Administrer un serveur sous Project Omega
Les commandes suivantes servent à la configuration des différentes options du bot. Elles peuvent être effectuées par tout membre possédant les droits administrateur sur le serveur.

**Attention** les configurations sont uniques, chaque serveur possède la sienne.

## Les commandes de configuration

### `/sync` : *Configuration globale*

> Elle vous permettra de définir l'item à synchroniser

![image](https://user-images.githubusercontent.com/73013583/217251656-c52517a0-d417-4f47-a2c5-e57d7276a841.png)

> Son identifiant sur l'intranet (dans le cas de l'année il faut mettre l'année d'entrée à l'ecole au lieu d'un id)

![image](https://user-images.githubusercontent.com/73013583/217251919-783fa14f-a457-454d-9761-f28ef995c58a.png)

> L'identifiant du rôle discord correspondant

![image](https://user-images.githubusercontent.com/73013583/217252106-451343f9-83f9-4dfd-8176-89995a599c90.png)

> Et enfin vous pouvez définir l'id du campus nécessaire pour obtenir le rôle. (pour définir tous les campus vous pouvez entrer 0)

![image](https://user-images.githubusercontent.com/73013583/217252464-bc7aa4cd-dd22-4c71-b4f5-1b1b11eb4601.png)

### `/sync_piscine` : *Syncronisation des piscines*

> Elle vous permettra d'attribuer un role a un utilisateur en fonction des dates de sa piscine.

### `/sync_project` : *Syncronisation des projets*

> Elle vous permettra de définir son identifiant sur l'intranet

![image](https://user-images.githubusercontent.com/73013583/217271621-98cba57a-4c63-4a0f-bb15-6e74f9f4d86f.png)

> D'autoriser ou non les differents statuts possibles avec le projet

![image](https://user-images.githubusercontent.com/73013583/217272838-bbe0ddc0-efe3-440b-b054-e2dbd39e4a42.png)

> De définir l'identifiant du rôle discord correspondant

![image](https://user-images.githubusercontent.com/73013583/217272356-73a8b784-4e54-492f-a178-66fe12a2a064.png)

> Et enfin vous pouvez définir l'id du campus necessaire pour obtenir le rôle. (Pour définir tous les campus vous pouvez entrer 0)

![image](https://user-images.githubusercontent.com/73013583/217272447-f76af907-2d3a-48a6-b0bc-bab761ad730b.png)

### `/nick` : *Définition de la politique de nommage*

![Screenshot from 2023-02-07 23-39-16](https://user-images.githubusercontent.com/73013583/217383303-a51f6b7e-9099-417c-a029-92d66627e6e6.png)

> L'argument **naming_patern** permet de configurer le patern de nommage. (&login et &campus sont des valeurs dynamiques elles seront remplacées par leur valeur pour chaque étudiant).

> L'argument **campus** correspond à l'id du campus sur lesquel la politique va s'appliquer. (Pour définir tous les campus vous pouvez entrer 0).

## Supprimer sa configuration

### `/delete` : *Suppression de la configuration*

> Elle vous permettra de spécifier le type de sychronisation à interrompre

![image](https://user-images.githubusercontent.com/73013583/217357888-95d4e890-b0f4-4ec1-a7bb-012226665479.png)

> L'id intranet ou l'id discord en rapport

![image](https://user-images.githubusercontent.com/73013583/217358609-5d94a3cf-a2e9-4668-86d8-c6e02d63a5e9.png)

> Et enfin l'identifiant

![image](https://user-images.githubusercontent.com/73013583/217358701-47730a2c-319a-4bba-8b04-90a6569f4648.png)

### `/nick_reset` : Suppression des politiques de nommage sur le serveur

![image](https://user-images.githubusercontent.com/73013583/217359712-2807b613-cb4d-4a41-8b6e-c0bd3465bf34.png)

___

# Notes des devs

> La version actuelle (beta) a une base de données litesql3 (changement certainement à venir [mariadb])
