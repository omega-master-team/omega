<?php
namespace App\Controller;

use App\View\View;
use Rexlabs\HyperHttp\Hyper;

class MainController {

    public function getHome() {
        return View::generatePage(200, 'index');
    }

    public function getOauth() {
        if (!isset($_GET['code']))
            return View::generatePage(400, 'error');
        session_start();
        $_SESSION['code'] = $_GET['code'];
        $data['url_intra'] = 'https://api.intra.42.fr/oauth/authorize?client_id='.$_ENV['API_UID'].'&redirect_uri='.$_ENV['DOMAIN'].'%2Fconnected&response_type=code';
        //echo $data['url_intra'];
        return View::generatePage(200, 'api', $data);
    }

    public function getConnectDiscord() {
        if (!isset($_GET['code'])/* || !isset($_SESSION['code'])*/) 
            return View::generatePage(400, 'error');
        $codeIntra = $_GET['code'];
        if (isset($_SESSION) && isset($_SESSION['code']))
            $codeDiscord = $_SESSION['code'];
            $data_token = json_encode([
                'code' => $codeIntra,
            'client_id' => $_ENV['API_UID'],
            'client_secret' => $_ENV['API_SECRET'],
            'grant_type' => 'authorization_code',
            'redirect_uri' => $_ENV['DOMAIN'].'/connected'
        ]);
        if (is_string($data_token)) {
            $data_token = str_replace("\\/", "/", $data_token);
            try {
                $response = Hyper::post('https://api.intra.42.fr/oauth/token', $data_token, ['content-type' => 'application/json']);
            } catch (\Throwable $th) {
                return View::generatePage(400, 'error');
            }
            $tmp = $response->toArray();
            $token = $tmp['token_type'] . ' ' . $tmp['access_token'];
            try {
                $response = Hyper::get('https://api.intra.42.fr/v2/me', [], null, ['Authorization' => $token]);
            } catch (\Throwable $th) {
                return View::generatePage(400, 'error');
            }
            $tmp = $response->toArray();
            // echo '<pre>';
            // var_dump($tmp);
            // echo '</pre>';
            // TODO db
            return View::generatePage(201, 'connected');
        } else {
            return View::generatePage(500, 'error');
        }
    }
}