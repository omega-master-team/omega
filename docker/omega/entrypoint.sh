#!/bin/bash

function is_running {
    if kill -0 $1 >/dev/null 2>&1; then
        return 0  # Processus en cours d'exécution
    else
        return 1  # Processus arrêté
    fi
}

#tail -f

# Lancement des deux services en arrière-plan
echo 'Lancement du service omega'
python3 omega.py &
echo 'Lancement du service web de omega'
env DB_FILE=/app/omega.db /app/oauth/target/release/oauth &

# Enregistrement des PID des deux services
service1_pid=$!
service2_pid=$!

# Vérification que les deux services sont toujours en cours d'exécution
while is_running $service1_pid && is_running $service2_pid; do
    sleep 5
done

# Si l'un des services s'est arrêté brutalement, affichage d'un message d'erreur et arrêt du script
echo "Un des services d\'omega s'est arrêté brutalement !"
exit 1
