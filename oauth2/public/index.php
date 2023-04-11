
<?php
require_once dirname(__DIR__) . DIRECTORY_SEPARATOR . 'vendor' . DIRECTORY_SEPARATOR . 'autoload.php';

use App\Router;

// echo '<pre>';
// var_dump($_ENV);
// $tmp = new Manager();
// // var_dump($_SERVER);
// // var_dump($_ENV);
// echo '</pre>';

$router = new Router();
$router
    ->get('/', 'Main#getHome', 'home page')
    ->get('/api', 'Main#getOauth', 'login page')
    ->get('/connected', 'Main#getConnectDiscord', 'connected page')
    ->run();