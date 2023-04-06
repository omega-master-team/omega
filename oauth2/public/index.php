
<?php
require_once dirname(__DIR__) . DIRECTORY_SEPARATOR . 'vendor' . DIRECTORY_SEPARATOR . 'autoload.php';

use App\Environnement;

//if (Environnement::getInfos()['maintenance'])

use App\Router;

$router = new Router();
// echo '<pre>';
// var_dump($_SERVER);
// var_dump($_ENV);
// echo '</pre>';
$_ENV['DOMAIN'] = getenv('DOMAIN');
$_ENV['API_UID'] = getenv('API_UID');
$_ENV['API_SECRET'] = getenv('API_SECRET');
$router
    ->get('/', 'Main#getHome', 'home page')
    ->get('/api', 'Main#getOauth', 'login page')
    ->get('/connected', 'Main#getConnectDiscord', 'connected page')
    ->run();