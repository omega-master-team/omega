function question ()
{
    while true ; do
        read -r -p "$1 [Y/n] " input
        if [[ "$input" =~ ^[yY][eE][sS]$  || "$input" =~ ^[yY]$ || -z "$input" ]] ; then
            echo true 
            break
        elif [[ "$input" =~ ^[nN][oO][nN]$ || "$input" =~ ^[nN] ]] ; then
            echo false
            break
        fi
    done
}

#certbot certonly --webroot -w /var/www/html --email xxx@gmail.com -d protocole-omega.tech

DEBUG_SCREEN=-dm

if [[ true = $(question "Arreter omega?") ]] ; then
        screen -XS omega kill
fi

if [[ true = $(question "Arreter oauth?") ]] ; then
        screen -XS oauth kill
fi


if [[ true = $(question "Lancer omega?") ]] ; then
        screen $DEBUG_SCREEN -S omega python3 omega.py
fi

if [[ true = $(question "Lancer oauth?") ]] ; then
        screen $DEBUG_SCREEN -S oauth env API_UID= API_SECRET= API_REDIRECT=https://protocole-omega.tech/connected DB_FILE=./omega.db ./oauth/target/release/oauth
fi


#nginx -t
systemctl restart nginx.service

#Show screen
sleep 1
echo recap
screen -lst

